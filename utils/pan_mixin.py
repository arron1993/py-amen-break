import numpy as np
from pydub import AudioSegment


class PanMixin:
    def auto_pan(self, segment, start_ms, period_s, depth, offset, phase):
        x = np.array(segment.get_array_of_samples(), dtype=np.float64)
        sr = segment.frame_rate
        t = start_ms / 1000.0 + np.arange(len(x)) / sr
        position = offset + depth * np.sin(2 * np.pi * t / period_s + phase)
        angle = (np.clip(position, -1, 1) + 1) * np.pi / 4

        stereo = np.empty(2 * len(x))
        stereo[0::2] = x * np.sqrt(2) * np.cos(angle)
        stereo[1::2] = x * np.sqrt(2) * np.sin(angle)

        data = np.int16(np.clip(stereo, -32768, 32767))
        return AudioSegment(data.tobytes(), frame_rate=sr, sample_width=2, channels=2)
