from pedalboard import Pedalboard, Reverb, Distortion

from racks.effects_rack import EffectsRack


class BaselineRack(EffectsRack):
    def generate_board(self, rng):
        return Pedalboard(
            [Distortion(drive_db=15), Reverb(room_size=0.2, wet_level=0.3)]
        )
