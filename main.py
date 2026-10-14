import argparse
import random

from racks.baseline_rack import BaselineRack
from racks.jungle_rack import JungleRack
from racks.sombre_rack import SombreRack
from themes.baseline_theme import BaselineTheme
from themes.jungle_theme import JungleTheme
from themes.sombre_theme import SombreTheme

from synths.baseline_bass_synth import BaselineBassSynth
from synths.baseline_pad_synth import BaselinePadSynth
from synths.jungle_pad_synth import JunglePadSynth
from synths.sampled_bass_synth import SampledBassSynth
from synths.sombre_bass_synth import SombreBassSynth
from synths.sombre_pad_synth import SombrePadSynth

from leads.baseline_lead import BaselineLead
from leads.sombre_lead import SombreLead

from exporters.video_exporter import VideoExporter

from sequencers.bpm_converter import BpmConverter
from sequencers.break_chopper import BreakChopper
from sequencers.break_sequencer import BreakSequencer
from sequencers.sample_hits import SampleHits
from sequencers.vocal_phrases import VocalPhrases


ORIGINAL_BPM = 137
DEFAULT_THEME = "sombre"
BREAK_SAMPLE = "samples/amen_break.wav"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a track from the Amen break."
    )
    parser.add_argument(
        "--seed", type=int, help="seed for the track; a random one is used if not set"
    )
    parser.add_argument(
        "--theme",
        choices=["sombre", "jungle", "baseline"],
        default=DEFAULT_THEME,
        help=f"theme for the track (default: {DEFAULT_THEME})",
    )
    parser.add_argument(
        "--video",
        action="store_true",
        help="also export a video with a generated thumbnail for YouTube",
    )
    return parser.parse_args()


def load_break(theme, seed):
    audio = BpmConverter(BREAK_SAMPLE, ORIGINAL_BPM, theme.target_bpm).process()
    return BreakChopper(audio, theme.target_bpm, seed=seed)


def main():
    args = parse_args()
    seed = args.seed if args.seed is not None else random.randint(0, 10000)
    print(f"Using seed {seed}")
    samples = None

    if args.theme == "sombre":
        theme = SombreTheme()
        chopper = load_break(theme, seed)
        effects_rack = SombreRack()
        bass_synth = SombreBassSynth()
        pad_synth = SombrePadSynth()
        lead = SombreLead()
    elif args.theme == "jungle":
        theme = JungleTheme(seed)
        print(f"Jungle tempo: {theme.target_bpm} BPM")
        chopper = load_break(theme, seed)
        effects_rack = JungleRack()
        bass_synth = SampledBassSynth(**theme.bass)
        pad_synth = JunglePadSynth()
        lead = None
        samples = {
            name: VocalPhrases(**settings) for name, settings in theme.vocals.items()
        }
        for name, hits in theme.sample_hits.items():
            samples[name] = SampleHits(hits)
    else:
        theme = BaselineTheme()
        chopper = load_break(theme, seed)
        effects_rack = BaselineRack()
        bass_synth = BaselineBassSynth(freq=30.0)
        pad_synth = BaselinePadSynth()
        lead = BaselineLead()

    sequencer = BreakSequencer(
        chopper,
        seed=seed,
        theme=theme,
        bass_synth=bass_synth,
        pad_synth=pad_synth,
        effects_rack=effects_rack,
        lead=lead,
        samples=samples,
    )

    track_path = f"track_{theme.name}_{seed}.wav"

    sequencer.compose_full_track()
    sequencer.export(
        track_path,
        f"drums_{theme.name}_{seed}.wav",
        f"bass_{theme.name}_{seed}.wav",
        f"pad_{theme.name}_{seed}.wav",
        f"lead_{theme.name}_{seed}.wav",
    )

    if args.video:
        VideoExporter().export(
            track_path,
            f"video_{theme.name}_{seed}.mp4",
            f"thumbnail_{theme.name}_{seed}.jpg",
            title=theme.name,
            subtitle=f"seed {seed}  ·  {theme.target_bpm} BPM",
        )


if __name__ == "__main__":
    main()
