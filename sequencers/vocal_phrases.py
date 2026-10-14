from pydub import AudioSegment

from utils.board_mixin import BoardMixin


class VocalPhrases(BoardMixin):
    def __init__(self, phrases, end_s, gain_db=0, board=None):
        self.phrases = []
        for path, offset_s in phrases:
            phrase = AudioSegment.from_file(path)
            if board is not None:
                phrase = self.apply_board(phrase, board)
            self.phrases.append((phrase + gain_db, offset_s))
        self.end_s = end_s

    def place(self, length_ms, sr, bar_ms):
        start_ms = length_ms - self.end_s * 1000
        placements = []
        for phrase, offset_s in self.phrases:
            position = round(start_ms + offset_s * 1000)
            if position >= 0:
                placements.append((phrase.set_frame_rate(sr), position))
        return placements
