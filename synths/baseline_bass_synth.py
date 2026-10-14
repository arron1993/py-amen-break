import numpy as np

from utils.synth_mixin import SynthMixin


class BaselineBassSynth(SynthMixin):
    def __init__(self, freq=40.0, pitch_drop=80.0, decay_rate=4.0):
        self.base_freq = freq
        self.pitch_drop = pitch_drop
        self.decay_rate = decay_rate

    def generate_note(self, duration_ms, sr, root_freq):
        duration_ms = max(duration_ms, 350)
        t = self.time_axis(duration_ms, sr)

        amp_env = np.exp(-self.decay_rate * (t / (duration_ms / 1000.0)))
        freq_env = self.base_freq + self.pitch_drop * np.exp(-20.0 * t)

        phase = self.phase(freq_env, sr)

        waveform = 0.7 * np.sin(phase) * amp_env

        return self.to_segment(waveform, sr)
