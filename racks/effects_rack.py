from pydub import AudioSegment

from utils.board_mixin import BoardMixin


class EffectsRack(BoardMixin):
    def __init__(self, tail_ms=400):
        self.tail_ms = tail_ms

    def process(self, segment, board):
        padded = segment + AudioSegment.silent(
            duration=self.tail_ms, frame_rate=segment.frame_rate
        )
        return self.apply_board(padded, board).fade_out(self.tail_ms)
