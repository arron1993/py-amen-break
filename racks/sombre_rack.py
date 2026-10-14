from pedalboard import (
    Pedalboard,
    Reverb,
    Distortion,
    HighpassFilter,
    LowpassFilter,
    LadderFilter,
    Chorus,
)

from racks.effects_rack import EffectsRack


def nudge(value, step, low, high, rng):
    return min(max(value + rng.uniform(-step, step), low), high)


class SombreRack(EffectsRack):
    def __init__(self):
        super().__init__(tail_ms=800)
        self.settings = None

    def generate_board(self, rng):
        if self.settings is None:
            self.settings = {
                "filter_type": rng.choices(
                    ["gentle", "ladder_lowpass", "ladder_both"],
                    weights=[60, 25, 15],
                    k=1,
                )[0],
                "chorus": rng.random() < 0.2,
                "lowpass_cutoff": rng.uniform(2500, 4500),
                "drive_db": rng.uniform(3, 8),
                "room_size": rng.uniform(0.6, 0.85),
                "damping": rng.uniform(0.7, 0.9),
            }
        else:
            s = self.settings
            s["lowpass_cutoff"] = nudge(s["lowpass_cutoff"], 300, 2500, 4500, rng)
            s["drive_db"] = nudge(s["drive_db"], 1.0, 3, 8, rng)
            s["room_size"] = nudge(s["room_size"], 0.05, 0.6, 0.85, rng)
            s["damping"] = nudge(s["damping"], 0.03, 0.7, 0.9, rng)

        return self._build_board()

    def _build_board(self):
        s = self.settings

        if s["filter_type"] == "ladder_both":
            highpass = LadderFilter(mode=LadderFilter.Mode.HPF24, cutoff_hz=90)
        else:
            highpass = HighpassFilter(cutoff_frequency_hz=90)

        if s["filter_type"] == "gentle":
            lowpass = LowpassFilter(cutoff_frequency_hz=s["lowpass_cutoff"])
        else:
            lowpass = LadderFilter(
                mode=LadderFilter.Mode.LPF24, cutoff_hz=s["lowpass_cutoff"]
            )

        effects = [
            highpass,
            Distortion(drive_db=s["drive_db"]),
            lowpass,
            Reverb(room_size=s["room_size"], damping=s["damping"], wet_level=0.45),
        ]

        if s["chorus"]:
            effects.append(Chorus(rate_hz=0.5, depth=0.2, mix=0.3))

        return Pedalboard(effects)
