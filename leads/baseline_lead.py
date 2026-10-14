import numpy as np
from pydub import AudioSegment

from utils.synth_mixin import SynthMixin
from utils.timing import STEPS_PER_BAR


class BaselineLead(SynthMixin):
    def __init__(self, level=0.1):
        self.level = level

    def generate(self, tones_per_bar, eighth_ms, length_ms, sr, rng):
        lead_block = AudioSegment.silent(duration=length_ms, frame_rate=sr)
        for bar, tones in enumerate(tones_per_bar):
            start = round(bar * STEPS_PER_BAR * eighth_ms)
            note = self._note(tones[0], round(2 * eighth_ms), sr)
            lead_block = lead_block.overlay(note, position=start)
        return lead_block

    def _note(self, freq, duration_ms, sr):
        num_samples = int(sr * duration_ms / 1000.0)
        t = np.arange(num_samples) / sr
        waveform = self.level * np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.2)
        return self.to_segment(waveform, sr).fade_in(5).fade_out(20)
