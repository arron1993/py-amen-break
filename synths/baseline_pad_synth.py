import numpy as np
from pydub import AudioSegment

from utils.synth_mixin import SynthMixin


class BaselinePadSynth(SynthMixin):
    def overlap_ms(self, rng):
        return 0

    def generate_chord(self, frequencies, duration_ms, sr, rng, eighth_ms):
        t = self.time_axis(duration_ms, sr)
        num_samples = len(t)
        if num_samples == 0:
            return AudioSegment.silent(duration=0)

        amp_env = np.exp(-6.0 * (t / (duration_ms / 1000.0)))

        waveform = np.zeros(num_samples)
        for freq in frequencies:
            waveform += 0.15 * (
                2.0 * np.abs(2.0 * (t * freq - np.floor(0.5 + t * freq))) - 1.0
            )

        waveform *= amp_env
        return self.to_segment(waveform, sr)
