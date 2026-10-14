import numpy as np
from pedalboard import Pedalboard, Delay, LowpassFilter, Reverb
from pydub import AudioSegment

from utils.board_mixin import BoardMixin
from utils.synth_mixin import SynthMixin
from utils.timing import STEPS_PER_BAR


class SombreLead(BoardMixin, SynthMixin):
    def __init__(self, level=0.16):
        self.level = level

    def generate(self, tones_per_bar, eighth_ms, length_ms, sr, rng):
        notes = self._choose_notes(tones_per_bar, rng)

        lead_block = AudioSegment.silent(duration=length_ms, frame_rate=sr)
        for step, steps, freq in notes:
            start = round(step * eighth_ms)
            duration = round((step + steps) * eighth_ms) - start
            lead_block = lead_block.overlay(
                self._note(freq, duration, sr), position=start
            )

        board = Pedalboard(
            [
                LowpassFilter(cutoff_frequency_hz=5000),
                Delay(delay_seconds=1.5 * eighth_ms / 1000, feedback=0.35, mix=0.25),
                Reverb(room_size=0.9, damping=0.6, wet_level=0.5, dry_level=0.7),
            ]
        )
        return self.apply_board(lead_block, board).fade_out(400)

    def _choose_notes(self, tones_per_bar, rng):
        starts = []
        for bar, tones in enumerate(tones_per_bar):
            count = rng.choices([0, 1, 2, 3], weights=[25, 40, 25, 10], k=1)[0]
            for beat in sorted(rng.sample([0, 2, 4, 6], count)):
                starts.append((bar * STEPS_PER_BAR + beat, tones))

        notes = []
        previous = None
        for index, (step, pool) in enumerate(starts):
            if previous is None:
                weights = [1] * len(pool)
            else:
                weights = []
                for freq in pool:
                    semitones = abs(12 * np.log2(freq / previous))
                    if semitones < 0.5:
                        weights.append(0.25)
                    else:
                        weights.append(1 / (1 + semitones / 3) ** 2)
            freq = rng.choices(pool, weights=weights, k=1)[0]

            if index + 1 < len(starts):
                next_step = starts[index + 1][0]
            else:
                next_step = len(tones_per_bar) * STEPS_PER_BAR
            notes.append((step, min(next_step - step, STEPS_PER_BAR), freq))
            previous = freq
        return notes

    def _note(self, freq, duration_ms, sr):
        num_samples = int(sr * duration_ms / 1000.0)
        t = np.arange(num_samples) / sr
        partials = [(1, 1.0, 2.5), (2, 0.35, 1.2), (3, 0.12, 0.6), (4, 0.06, 0.4)]

        waveform = np.zeros(num_samples)
        for multiple, level, decay_s in partials:
            waveform += (
                level * np.sin(2 * np.pi * freq * multiple * t) * np.exp(-t / decay_s)
            )
        waveform *= self.level / sum(level for _, level, _ in partials)

        return self.to_segment(waveform, sr).fade_in(8).fade_out(60)
