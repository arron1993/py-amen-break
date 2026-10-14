import numpy as np

from utils.audio import waveform_to_segment


class SynthMixin:
    def time_axis(self, duration_ms, sr):
        num_samples = max(int(sr * (duration_ms / 1000.0)), 0)
        return np.linspace(0, duration_ms / 1000.0, num_samples, endpoint=False)

    def phase(self, frequency, sr):
        dt = 1.0 / sr
        return 2 * np.pi * np.cumsum(frequency) * dt

    def to_segment(self, waveform, sr):
        return waveform_to_segment(np.clip(waveform, -1.0, 1.0), sr)
