import numpy as np
from pydub import AudioSegment

from utils.synth_mixin import SynthMixin


class SombrePadSynth(SynthMixin):
    def __init__(self):
        self.settings = None

    def _get_settings(self, rng):
        if self.settings is None:
            warm = rng.random() < 0.8
            vibrato = rng.random() < 0.5
            overlap = rng.random() < 0.7
            self.settings = {
                "overtone_rolloff": rng.uniform(1.5, 2.0) if warm else None,
                "unison_voices": 3 if rng.random() < 0.6 else 2,
                "vibrato_cents": rng.uniform(2, 6) if vibrato else 0,
                "vibrato_rate_hz": rng.uniform(0.2, 0.4),
                "overlap_ms": round(rng.uniform(1000, 2000)) if overlap else 0,
            }
        return self.settings

    def overlap_ms(self, rng):
        return self._get_settings(rng)["overlap_ms"]

    def _tone(self, phase, freq, rolloff):
        if rolloff is None:
            return np.sin(phase)
        tone = np.zeros(len(phase))
        energy = 0.0
        for n in range(1, 9):
            if n > 1 and n * freq > 2500:
                break
            tone += np.sin(n * phase) / n ** rolloff
            energy += 1 / n ** (2 * rolloff)
        return tone / np.sqrt(energy)

    def generate_chord(self, frequencies, duration_ms, sr, rng, eighth_ms):
        settings = self._get_settings(rng)
        t = self.time_axis(duration_ms, sr)
        num_samples = len(t)
        if num_samples == 0:
            return AudioSegment.silent(duration=0)

        duration_s = duration_ms / 1000.0

        if settings["overlap_ms"]:
            fade = min(settings["overlap_ms"] / 1000.0, duration_s / 2)
            amp_env = np.ones(num_samples)
            rise = t < fade
            amp_env[rise] = np.sin(0.5 * np.pi * t[rise] / fade) ** 2
            fall = t > duration_s - fade
            amp_env[fall] = np.sin(0.5 * np.pi * (duration_s - t[fall]) / fade) ** 2
            amp_env *= 0.75
        else:
            amp_env = np.sin(np.pi * (t / duration_s))

        if settings["unison_voices"] == 3:
            voices = [(1.0, 1.0), (1.004, 0.6), (0.996, 0.6)]
        else:
            voices = [(1.0, 1.0), (1.003, 0.5)]
        voice_scale = np.sqrt(1.25 / sum(level ** 2 for _, level in voices))

        depth = 2 ** (settings["vibrato_cents"] / 1200) - 1
        wobble = 1 + depth * np.sin(2 * np.pi * settings["vibrato_rate_hz"] * t)

        waveform = np.zeros(num_samples)
        for freq in frequencies:
            for detune, level in voices:
                phase = self.phase(freq * detune * wobble, sr)
                tone = self._tone(phase, freq, settings["overtone_rolloff"])
                waveform += 0.05 * level * voice_scale * tone

        waveform *= amp_env
        return self.to_segment(waveform, sr).fade_in(20).fade_out(20)
