from pydub import AudioSegment


class SampledBassSynth:
    def __init__(self, samples, transpose=1.0, gain_db=0, fade_out_ms=30):
        self.notes = {
            freq: AudioSegment.from_file(path).set_sample_width(2).set_channels(1)
            + gain_db
            for freq, path in samples.items()
        }
        self.transpose = transpose
        self.fade_out_ms = fade_out_ms

    def generate_note(self, duration_ms, sr, root_freq):
        target = root_freq * self.transpose
        nearest = min(self.notes, key=lambda freq: abs(freq - target))
        note = self.notes[nearest].set_frame_rate(sr)
        return note[:duration_ms].fade_out(self.fade_out_ms)
