from pydub import AudioSegment


class SampleHits:
    def __init__(self, hits):
        self.hits = []
        for hit in hits:
            sample = AudioSegment.from_file(hit["path"]).set_sample_width(2)
            if "slice_s" in hit:
                start_s, end_s = hit["slice_s"]
                sample = sample[round(start_s * 1000) : round(end_s * 1000)]
                sample = sample.fade_in(6).fade_out(6)
            self.hits.append({**hit, "sample": sample + hit.get("gain_db", 0)})

    def place(self, length_ms, sr, bar_ms):
        beat_ms = bar_ms / 4
        placements = []
        for hit in self.hits:
            sample = hit["sample"]
            if "length_beats" in hit:
                sample = sample[: round(hit["length_beats"] * beat_ms)].fade_out(6)
            position = (hit["bar"] - 1) * bar_ms + (hit.get("beat", 1) - 1) * beat_ms
            if hit.get("anchor") == "end":
                position = hit["bar"] * bar_ms - len(sample) - hit.get("gap_ms", 0)
            if position < length_ms:
                placements.append((sample.set_frame_rate(sr), round(position)))
        return placements
