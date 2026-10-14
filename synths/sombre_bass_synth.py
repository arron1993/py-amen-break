import numpy as np

from utils.synth_mixin import SynthMixin


class SombreBassSynth(SynthMixin):
    def __init__(
        self,
        pitch_drop=10.0,
        drop_speed=30.0,
        decay_rate=2.0,
        octave_level=0.25,
        fade_in_ms=15,
        fade_out_ms=30,
    ):
        self.pitch_drop = pitch_drop
        self.drop_speed = drop_speed
        self.decay_rate = decay_rate
        self.octave_level = octave_level
        self.fade_in_ms = fade_in_ms
        self.fade_out_ms = fade_out_ms

    def generate_note(self, duration_ms, sr, root_freq):
        duration_ms = max(duration_ms, 350)
        t = self.time_axis(duration_ms, sr)

        amp_env = np.exp(-self.decay_rate * (t / (duration_ms / 1000.0)))
        freq_env = root_freq + self.pitch_drop * np.exp(-self.drop_speed * t)

        phase = self.phase(freq_env, sr)

        waveform = np.sin(phase) + self.octave_level * np.sin(2 * phase)
        waveform = 0.7 * waveform / (1 + self.octave_level) * amp_env

        segment = self.to_segment(waveform, sr)
        return segment.fade_in(self.fade_in_ms).fade_out(self.fade_out_ms)
