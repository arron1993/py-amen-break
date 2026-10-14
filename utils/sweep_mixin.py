import numpy as np
from scipy.signal import butter, lfilter


class SweepMixin:
    def lowpass_sweep(self, segment, start_hz, end_hz, chunk=256):
        sr = segment.frame_rate
        channels = segment.channels
        x = np.array(segment.get_array_of_samples(), dtype=np.float64)
        x = x.reshape(-1, channels)
        swept = np.zeros_like(x)
        state = np.zeros((2, channels))

        for start in range(0, len(x), chunk):
            cutoff = start_hz * (end_hz / start_hz) ** (start / len(x))
            b, a = butter(2, cutoff / (sr / 2))
            for channel in range(channels):
                swept[start : start + chunk, channel], state[:, channel] = lfilter(
                    b, a, x[start : start + chunk, channel], zi=state[:, channel]
                )

        data = np.int16(np.clip(swept, -32768, 32767))
        return segment._spawn(data.tobytes())
