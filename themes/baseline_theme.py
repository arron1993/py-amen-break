from utils.timing import STEPS_PER_BAR


class BaselineTheme:
    def __init__(self):
        self.name = "baseline"
        self.arrangement = [
            {"name": "Intro", "type": "section", "bars": 2, "bass": False, "pad": False},
            {"name": "Verse", "type": "section", "bars": 8, "bass": False, "pad": True},
            {"name": "Fill", "type": "fill", "bars": 0.5},
            {"name": "Drop", "type": "section", "bars": 8, "bass": True, "pad": True},
            {"name": "Outro", "type": "section", "bars": 2, "bass": False, "pad": False},
        ]
        self.target_bpm = 108
        self.chord_progression = ["Dm", "F", "Am", "C"]
        self.bass_roots = {"Dm": 36.71, "F": 43.65, "Am": 27.50, "C": 32.70}
        self.pad_voicings = {
            "Dm": [293.66, 349.23, 440.00],
            "F": [349.23, 440.00, 523.25],
            "Am": [440.00, 523.25, 659.25],
            "C": [523.25, 659.25, 783.99],
        }
        self.lead_tones = {
            "Dm": [587.33, 698.46, 880.00],
            "F": [698.46, 880.00, 1046.50],
            "Am": [880.00, 1046.50, 1318.51],
            "C": [1046.50, 1318.51, 1567.98],
        }
        self.bass_on_every_kick = False
        self.bars_per_chord = 1
        self.drum_gain_db = -11
        self.pad_gain_db = -4
        self.lead_gain_db = -4
        self.stereo_sweep = None

    def generate_pattern(self, bars, rng):
        total_steps = int(bars * STEPS_PER_BAR)
        sequence = []
        for i in range(total_steps):
            step = i % STEPS_PER_BAR
            if step in (0, 4):
                sequence.append("kick")
            elif step in (2, 6):
                sequence.append("snare")
            elif step in (1, 5):
                hit = rng.choices(["cymbal", "stutter"], weights=[80, 20], k=1)[0]
                sequence.append(hit)
            elif step in (3, 7):
                hit = rng.choices(["kick", "cymbal"], weights=[70, 30], k=1)[0]
                sequence.append(hit)
        return sequence

    def generate_progression(self, num_chords, rng):
        return [
            self.chord_progression[i % len(self.chord_progression)]
            for i in range(num_chords)
        ]
