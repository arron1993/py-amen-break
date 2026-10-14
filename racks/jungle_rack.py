from pedalboard import Pedalboard, Compressor, Distortion, HighpassFilter, Reverb

from racks.effects_rack import EffectsRack


class JungleRack(EffectsRack):
    def __init__(self):
        super().__init__(tail_ms=250)
        self.settings = None

    def generate_board(self, rng):
        if self.settings is None:
            self.settings = {
                "drive_db": rng.uniform(12, 16),
                "room_size": rng.uniform(0.15, 0.3),
                "wet_level": rng.uniform(0.12, 0.2),
            }
        s = self.settings

        return Pedalboard(
            [
                HighpassFilter(cutoff_frequency_hz=60),
                Distortion(drive_db=s["drive_db"]),
                Compressor(threshold_db=-18, ratio=4, attack_ms=2, release_ms=80),
                Reverb(room_size=s["room_size"], wet_level=s["wet_level"]),
            ]
        )
