from utils.timing import STEPS_PER_BAR


class SombreTheme:
    def __init__(self):
        self.name = "sombre"
        self.arrangement = [
            {"name": "Intro", "type": "section", "bars": 2, "bass": False, "pad": False},
            {"name": "Verse", "type": "section", "bars": 8, "bass": False, "pad": True},
            {"name": "Fill", "type": "fill", "bars": 0.5},
            {"name": "Verse 2", "type": "section", "bars": 8, "bass": True, "pad": True},
            {"name": "Outro", "type": "section", "bars": 2, "bass": False, "pad": False},
        ]
        self.target_bpm = 88
        self.chord_transitions = {
            "Dm9": (["Bbmaj7", "Gm9", "Am7", "Cadd9", "Fmaj7"], [30, 20, 15, 15, 20]),
            "Bbmaj7": (["Gm9", "Cadd9", "A7"], [40, 30, 30]),
            "Gm9": (["A7", "Dm9", "Bbmaj7"], [50, 30, 20]),
            "Am7": (["Bbmaj7", "Dm9"], [50, 50]),
            "Cadd9": (["Dm9", "Am7", "Fmaj7"], [50, 30, 20]),
            "A7": (["Dm9"], [100]),
            "Fmaj7": (["Bbmaj7", "Gm9", "Cadd9"], [40, 30, 30]),
        }
        self.bass_roots = {
            "Dm9": 36.71,
            "Am7": 27.50,
            "Fmaj7": 43.65,
            "Gm9": 49.00,
            "Bbmaj7": 29.14,
            "Cadd9": 32.70,
            "A7": 27.50,
        }
        self.pad_voicings = {
            "Dm9": [110.00, 146.83, 174.61, 220.00, 261.63, 329.63],
            "Am7": [110.00, 220.00, 261.63, 329.63, 392.00],
            "Fmaj7": [130.81, 174.61, 220.00, 261.63, 329.63],
            "Gm9": [116.54, 146.83, 174.61, 196.00, 220.00],
            "Bbmaj7": [116.54, 146.83, 174.61, 220.00, 293.66],
            "Cadd9": [130.81, 164.81, 196.00, 293.66, 329.63],
            "A7": [110.00, 164.81, 196.00, 277.18, 329.63],
        }
        self.lead_tones = {
            "Dm9": [293.66, 349.23, 440.00, 523.25, 587.33, 659.25],
            "Am7": [392.00, 440.00, 523.25, 659.25],
            "Fmaj7": [349.23, 440.00, 523.25, 659.25],
            "Gm9": [392.00, 440.00, 466.16, 587.33, 698.46],
            "Bbmaj7": [349.23, 440.00, 466.16, 587.33],
            "Cadd9": [392.00, 523.25, 587.33, 659.25],
            "A7": [392.00, 440.00, 554.37, 659.25],
        }
        self.bass_on_every_kick = True
        self.bars_per_chord = 2
        self.drum_gain_db = -9
        self.pad_gain_db = 1
        self.lead_gain_db = 1
        self.stereo_sweep = {
            "pad_period_s": (12, 20),
            "pad_depth": (0.4, 0.7),
            "lead_period_s": (8, 14),
            "lead_depth": (0.2, 0.4),
            "lead_offset": 0.25,
        }

    def generate_pattern(self, bars, rng):
        total_steps = int(bars * STEPS_PER_BAR)
        sequence = []
        for i in range(total_steps):
            step = i % STEPS_PER_BAR
            if step == 0:
                sequence.append("kick")
            elif step in (3, 6):
                sequence.append("snare")
            elif step in (2, 5, 7):
                hit = rng.choices(["stutter", "cymbal"], weights=[70, 30], k=1)[0]
                sequence.append(hit)
            else:
                sequence.append("kick" if rng.random() > 0.5 else "cymbal")
        return sequence

    def generate_progression(self, num_chords, rng):
        progression = ["Dm9"]
        while len(progression) < num_chords:
            options, weights = self.chord_transitions[progression[-1]]
            progression.append(rng.choices(options, weights=weights, k=1)[0])
        return progression[:num_chords]
