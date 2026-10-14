import librosa

from utils.audio import waveform_to_segment

class BpmConverter:
    def __init__(self, file_path, original_bpm, target_bpm):
        self.file_path = file_path
        self.rate = target_bpm / original_bpm

    def process(self):
        y, sr = librosa.load(self.file_path, sr=None)
        y_resampled = librosa.resample(y, orig_sr=sr, target_sr=int(sr / self.rate))
        return waveform_to_segment(y_resampled, sr)