import numpy as np
from pedalboard import Chorus, Pedalboard, Reverb
from pydub import AudioSegment
from scipy.signal import butter, sosfilt

from utils.synth_mixin import SynthMixin
from utils.timing import STEPS_PER_BAR


class JunglePadSynth(SynthMixin):
    def __init__(self, level_db=-29, attack_s=0.1, release_s=0.3, chord_overlap_ms=500):
        self.level_db = level_db
        self.attack_s = attack_s
        self.release_s = release_s
        self.chord_overlap_ms = chord_overlap_ms
        self.detunes = (0.993, 0.997, 1.0, 1.003, 1.007)
        self.pulse_patterns = [
            (8, [0, 1, 3, 4, 6]),
            (8, [0, 1, 2, 3, 4, 5, 6, 7]),
            (16, [0, 1, 3, 4, 6, 8, 9, 11, 12, 14]),
        ]
        self.pulse_floors = [0.15, 0.0]
        self.settings = None

    def _get_settings(self, rng):
        if self.settings is None:
            pulses_per_bar, pulse_steps = rng.choice(self.pulse_patterns)
            self.settings = {
                "pulses_per_bar": pulses_per_bar,
                "pulse_steps": pulse_steps,
                "pulse_floor": rng.choice(self.pulse_floors),
            }
        return self.settings

    def overlap_ms(self, rng):
        return self.chord_overlap_ms

    def _saw(self, freq, t):
        waveform = np.zeros(len(t))
        for i, detune in enumerate(self.detunes):
            waveform += 2 * ((freq * detune * t + 0.37 * i) % 1.0) - 1
        return waveform / len(self.detunes)

    def _lowpass(self, waveform, sr, cutoff_hz, order):
        return sosfilt(butter(order, cutoff_hz, fs=sr, output="sos"), waveform)

    def _pulse(self, t, eighth_ms, settings):
        step_ms = STEPS_PER_BAR * eighth_ms / settings["pulses_per_bar"]
        t_ms = t * 1000
        step = (t_ms // step_ms).astype(int) % settings["pulses_per_bar"]
        within = (t_ms % step_ms) / step_ms
        floor = settings["pulse_floor"]
        shape = np.minimum(1, within * 12) * np.minimum(1, (1 - within) * 6 + floor)
        return np.where(np.isin(step, settings["pulse_steps"]), shape, floor)

    def generate_chord(self, frequencies, duration_ms, sr, rng, eighth_ms):
        settings = self._get_settings(rng)
        num_samples = int(sr * duration_ms / 1000)
        if num_samples <= 0:
            return AudioSegment.silent(duration=0)

        t = np.arange(num_samples) / sr
        waveform = sum(self._saw(freq / 2, t) for freq in frequencies)
        waveform = self._lowpass(waveform, sr, 900, 4)
        waveform = waveform + 1.5 * self._lowpass(waveform, sr, 200, 2)
        waveform = waveform * self._pulse(t, eighth_ms, settings)

        time_left = t[-1] - t
        waveform = waveform * np.minimum(1, t / self.attack_s)
        waveform = waveform * np.minimum(1, time_left / self.release_s)

        board = Pedalboard(
            [
                Chorus(rate_hz=0.6, depth=0.3, mix=0.4),
                Reverb(room_size=0.8, wet_level=0.35, dry_level=0.65),
            ]
        )
        waveform = board(waveform.astype(np.float32)[None, :], sr)[0].astype(np.float64)
        waveform = waveform * np.minimum(1, time_left / 0.05)

        rms = max(np.sqrt((waveform**2).mean()), 1e-9)
        waveform = waveform * 10 ** (self.level_db / 20) / rms
        return self.to_segment(waveform, sr)
