import numpy as np
from pydub import AudioSegment


class BoardMixin:
    def apply_board(self, segment, board):
        samples = np.array(segment.get_array_of_samples(), dtype=np.float32) / 32768.0
        if segment.channels == 2:
            samples = samples.reshape((-1, 2)).T

        processed = board(samples, segment.frame_rate)

        if segment.channels == 2:
            processed = processed.T.flatten()

        int_data = np.int16(np.clip(processed, -1.0, 1.0) * 32767)
        return AudioSegment(
            int_data.tobytes(),
            frame_rate=segment.frame_rate,
            sample_width=2,
            channels=segment.channels,
        )
