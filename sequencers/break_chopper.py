import random

from utils.timing import STEPS_PER_BAR


class BreakChopper:
    def __init__(self, audio_segment, target_bpm, seed=None):
        self.amen = audio_segment
        self.sr = int(audio_segment.frame_rate)
        self.beat = 60000 / target_bpm
        self.eighth = self.beat / 2
        self.step_ms = self.eighth
        self.rng = random.Random(seed)

        stutter_chop = self.amen[: int(self.eighth / 2)].fade_in(3).fade_out(3)

        self.slices = {
            "kick": self.amen[0 : int(self.eighth)].fade_in(5).fade_out(5),
            "snare": self.amen[int(self.beat) : int(self.beat + self.eighth)]
            .fade_in(5)
            .fade_out(5),
            "cymbal": self.amen[int(self.beat * 2) : int(self.beat * 2 + self.eighth)]
            .fade_in(5)
            .fade_out(5),
            "stutter": stutter_chop + stutter_chop,
        }
        for i in range(STEPS_PER_BAR):
            start = round(i * self.eighth)
            end = round((i + 1) * self.eighth)
            self.slices[f"chop_{i + 1}"] = self.amen[start:end].fade_in(2).fade_out(4)

    def generate_fill(self, bars=0.5):
        num_steps = int(bars * STEPS_PER_BAR)
        sequence = []
        for _ in range(num_steps):
            hit = self.rng.choices(
                ["snare", "stutter", "cymbal"], weights=[40, 40, 20], k=1
            )[0]
            sequence.append(hit)
        return sequence