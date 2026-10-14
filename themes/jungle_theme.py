import random

from pedalboard import Distortion, HighpassFilter, LowpassFilter, Pedalboard

from utils.timing import STEPS_PER_BAR


class JungleTheme:
    def __init__(self, seed=None):
        self.name = "jungle"
        self.arrangement = [
            {
                "name": "Build",
                "type": "section",
                "bars": 12,
                "bass": False,
                "pad": True,
                "pattern": self.generate_build_pattern,
                "drum_sweep_hz": (250, 9000),
                "samples": "question",
            },
            {
                "name": "Pause",
                "type": "section",
                "bars": 2,
                "bass": False,
                "pad": False,
                "pattern": self.generate_pause_pattern,
                "samples": "reaction",
            },
            {
                "name": "Drop",
                "type": "section",
                "bars": 16,
                "bass": True,
                "pad": True,
                "pattern": self.generate_drop_pattern,
                "samples": "sound_system",
            },
            {
                "name": "Breakdown",
                "type": "section",
                "bars": 8,
                "bass": False,
                "pad": True,
                "pattern": self.generate_build_pattern,
                "drum_sweep_hz": (250, 9000),
                "samples": "callback",
            },
            {
                "name": "Drop 2",
                "type": "section",
                "bars": 16,
                "bass": True,
                "pad": True,
                "pattern": self.generate_drop_pattern,
                "samples": "sound_system",
            },
            {"name": "Outro", "type": "section", "bars": 4, "bass": False, "pad": False},
        ]
        self.tempos = [168, 174, 169, 175]
        tempo_rng = random.Random(None if seed is None else f"{seed}-style")
        self.target_bpm = tempo_rng.choice(self.tempos)
        self.chop_gain_db = -2
        self.build_gain_db = -6
        self.drop_gain_db = 4
        self.chop_phrase = [
            [1, 2, 3, 4, 5, 6, 7, 8],
            [1, 2, 3, 4, 1, 2, 3, 4],
            [1, 2, 3, 4, 5, 6, 7, 8],
            [1, 2, 3, 4, 3, 4, 3, 8],
        ]
        self.second_half_chop_phrase = [
            [5, 6, 7, 8, 5, 6, 7, 8],
            [1, 2, 3, 4, 5, 6, 7, 8],
            [5, 6, 7, 8, 1, 2, 3, 4],
            [1, 2, 3, 4, 7, 8, 7, 8],
        ]
        self.bass_steps = [0, 5]
        self.bass_rest_bars = 1
        self.bass = {
            "samples": {
                55.00: self._bass_sample("A0"),
                61.74: self._bass_sample("B0"),
                65.41: self._bass_sample("C1"),
                73.42: self._bass_sample("D1"),
                82.41: self._bass_sample("E1"),
                87.31: self._bass_sample("F1"),
                98.00: self._bass_sample("G1"),
            },
            "transpose": 2.0,
            "gain_db": -3.2,
        }
        self.vocals = {
            "question": {
                "phrases": [
                    ("samples/we_need_jungle/question_1.wav", 0.07),
                    ("samples/we_need_jungle/question_2.wav", 4.25),
                    ("samples/we_need_jungle/question_3.wav", 7.07),
                    ("samples/we_need_jungle/question_4.wav", 9.13),
                    ("samples/we_need_jungle/drum_and_bass.wav", 11.01),
                    ("samples/we_need_jungle/we_need_jungle_im_afraid.wav", 12.15),
                ],
                "end_s": 13.85,
                "gain_db": 3,
            },
            "reaction": {
                "phrases": [("samples/ah_shit_here_we_go_again/line.wav", 0)],
                "end_s": 2.3,
                "gain_db": 4.6,
                "board": Pedalboard(
                    [
                        HighpassFilter(cutoff_frequency_hz=400),
                        HighpassFilter(cutoff_frequency_hz=400),
                        LowpassFilter(cutoff_frequency_hz=2800),
                        LowpassFilter(cutoff_frequency_hz=2800),
                        Distortion(drive_db=12),
                    ]
                ),
            },
        }
        sub = "samples/blu_mar_ten/Bass/Wheel Up Sub.wav"
        signal = "samples/blu_mar_ten/FX/Wheel Up Signal - 12A.wav"
        rewind = "samples/blu_mar_ten/FX/Ganga Rewind.wav"
        self.sample_hits = {
            "sound_system": [
                {"path": sub, "bar": 1, "gain_db": -10},
                {"path": signal, "bar": 1, "gain_db": -9.5},
                {"path": rewind, "bar": 8, "anchor": "end", "gain_db": -10.5},
                {"path": signal, "bar": 9, "gain_db": -9.5},
                {"path": rewind, "bar": 16, "anchor": "end", "gain_db": -10.5},
            ],
            "callback": [
                self._line_hit((0.0, 0.97), bar=5),
                self._line_hit((0.34, 0.97), bar=6, beat=1),
                self._line_hit((0.34, 0.97), bar=6, beat=3),
                self._line_hit((0.34, 0.97), bar=7, beat=1, length_beats=1),
                self._line_hit((0.34, 0.97), bar=7, beat=2, length_beats=1),
                self._line_hit((0.34, 0.97), bar=7, beat=3, length_beats=1),
                self._line_hit((0.34, 0.97), bar=7, beat=4, length_beats=1),
                self._line_hit((0.34, 0.97), bar=8, beat=1, length_beats=0.5),
                self._line_hit((0.34, 0.97), bar=8, beat=1.5, length_beats=0.5),
                self._line_hit((0.34, 0.97), bar=8, beat=2, length_beats=0.5),
                self._line_hit((0.34, 0.97), bar=8, beat=2.5, length_beats=0.5),
                self._line_hit((0.97, 1.70), bar=8, anchor="end", gap_ms=30),
            ],
        }
        self.chord_transitions = {
            "Em9": (["Cmaj7", "Dadd9", "Am7", "Gmaj7", "Bm7"], [35, 20, 20, 15, 10]),
            "Cmaj7": (["Dadd9", "Em9", "Am7"], [45, 30, 25]),
            "Dadd9": (["Em9", "Bm7", "Cmaj7"], [60, 20, 20]),
            "Am7": (["Em9", "Bm7", "Cmaj7"], [35, 35, 30]),
            "Bm7": (["Em9", "Cmaj7"], [70, 30]),
            "Gmaj7": (["Dadd9", "Cmaj7", "Am7"], [40, 30, 30]),
        }
        self.bass_roots = {
            "Em9": 41.20,
            "Cmaj7": 32.70,
            "Dadd9": 36.71,
            "Am7": 27.50,
            "Bm7": 30.87,
            "Gmaj7": 49.00,
        }
        self.pad_voicings = {
            "Em9": [123.47, 164.81, 196.00, 246.94, 293.66, 369.99],
            "Cmaj7": [130.81, 164.81, 196.00, 246.94, 329.63],
            "Dadd9": [146.83, 185.00, 220.00, 293.66, 329.63],
            "Am7": [110.00, 164.81, 196.00, 261.63, 329.63],
            "Bm7": [123.47, 185.00, 220.00, 293.66, 369.99],
            "Gmaj7": [123.47, 146.83, 196.00, 246.94, 369.99],
        }
        self.lead_tones = {
            "Em9": [329.63, 392.00, 493.88, 587.33, 659.25, 739.99],
            "Cmaj7": [329.63, 392.00, 493.88, 523.25, 659.25],
            "Dadd9": [293.66, 369.99, 440.00, 587.33, 659.25],
            "Am7": [329.63, 392.00, 440.00, 523.25, 659.25],
            "Bm7": [293.66, 369.99, 440.00, 493.88, 587.33],
            "Gmaj7": [293.66, 392.00, 493.88, 587.33, 739.99],
        }
        self.bass_on_every_kick = False
        self.bars_per_chord = 2
        self.drum_gain_db = 3
        self.pad_gain_db = -1
        self.lead_gain_db = -1
        self.stereo_sweep = {
            "pad_period_s": (8, 14),
            "pad_depth": (0.4, 0.7),
            "lead_period_s": (6, 10),
            "lead_depth": (0.2, 0.4),
            "lead_offset": 0.25,
        }

    def _bass_sample(self, note):
        folder = "samples/musicradar-90s-jungle-samples/Bass Multisamples/Bass D"
        return f"{folder}/Jungle_BassD[Multi]_{note}.wav"

    def _line_hit(self, slice_s, **placement):
        return {
            "path": "samples/we_need_jungle/we_need_jungle_im_afraid.wav",
            "slice_s": slice_s,
            "gain_db": 5,
            **placement,
        }

    def generate_pattern(self, bars, rng):
        sequence = []
        for bar in range(int(bars)):
            for chop in self.chop_phrase[bar % len(self.chop_phrase)]:
                sequence.append((f"chop_{chop}", self.chop_gain_db))
        return sequence

    def generate_pause_pattern(self, bars, rng):
        return ["rest"] * int(bars * STEPS_PER_BAR)

    def generate_drop_pattern(self, bars, rng):
        gain_db = self.chop_gain_db + self.drop_gain_db
        sequence = []
        for bar in range(int(bars)):
            if bar < int(bars) // 2:
                phrase = self.chop_phrase
            else:
                phrase = self.second_half_chop_phrase
            for chop in phrase[bar % len(phrase)]:
                sequence.append((f"chop_{chop}", gain_db))
        return sequence

    def generate_build_pattern(self, bars, rng):
        sequence = [
            (name, gain_db + self.build_gain_db)
            for name, gain_db in self.generate_pattern(bars, rng)
        ]
        sequence[-STEPS_PER_BAR // 4 :] = ["rest"] * (STEPS_PER_BAR // 4)
        return sequence

    def generate_bass_pattern(self, bars, rng):
        return [
            (bar * STEPS_PER_BAR + step, "root")
            for bar in range(self.bass_rest_bars, int(bars))
            for step in self.bass_steps
        ]

    def generate_progression(self, num_chords, rng):
        progression = ["Em9"]
        while len(progression) < num_chords:
            options, weights = self.chord_transitions[progression[-1]]
            progression.append(rng.choices(options, weights=weights, k=1)[0])
        return progression[:num_chords]
