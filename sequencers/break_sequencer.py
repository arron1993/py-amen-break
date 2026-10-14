import math
import random

from pydub import AudioSegment

from utils.pan_mixin import PanMixin
from utils.sweep_mixin import SweepMixin
from utils.timing import STEPS_PER_BAR

BASS_INTERVALS = {"root": 1.0, "fifth": 2 ** (7 / 12), "octave": 2.0}
MAX_BASS_NOTE_STEPS = 16


class BreakSequencer(PanMixin, SweepMixin):
    def __init__(
        self,
        chopper,
        seed=None,
        theme=None,
        bass_synth=None,
        pad_synth=None,
        effects_rack=None,
        lead=None,
        samples=None,
    ):
        self.theme = theme
        self.chopper = chopper
        self.chord_rng = random.Random(None if seed is None else f"{seed}-chords")
        self.fx_rng = random.Random(None if seed is None else f"{seed}-fx")
        self.pad_rng = random.Random(None if seed is None else f"{seed}-pad")
        self.lead_rng = random.Random(None if seed is None else f"{seed}-lead")
        self.pan_rng = random.Random(None if seed is None else f"{seed}-pan")
        self.bass_rng = random.Random(None if seed is None else f"{seed}-bass")
        self.bass_synth = bass_synth
        self.pad_synth = pad_synth
        self.fx = effects_rack
        self.lead = lead
        self.samples = samples or {}
        self.sr = chopper.sr
        self.pad_pan, self.lead_pan = self._choose_pan_settings()

        self.track_sections = []
        self.drum_sections = []
        self.bass_sections = []
        self.pad_sections = []
        self.lead_sections = []

    def _choose_pan_settings(self):
        sweep = self.theme.stereo_sweep
        if sweep is None:
            return None, None

        rng = self.pan_rng
        phase = rng.uniform(0, 2 * math.pi)
        pad_pan = dict(
            period_s=rng.uniform(*sweep["pad_period_s"]),
            depth=rng.uniform(*sweep["pad_depth"]),
            offset=0.0,
            phase=phase,
        )
        lead_pan = dict(
            period_s=rng.uniform(*sweep["lead_period_s"]),
            depth=rng.uniform(*sweep["lead_depth"]),
            offset=rng.choice([-1, 1]) * sweep["lead_offset"],
            phase=phase + math.pi,
        )
        return pad_pan, lead_pan

    def _process_slices(self):
        board = self.fx.generate_board(self.fx_rng)
        return {
            name: self.fx.process(segment, board)
            for name, segment in self.chopper.slices.items()
        }

    def _render_hits(
        self,
        hits,
        bass_on_kicks,
        drum_gain_db,
        step_chords=None,
        bass_notes=(),
        drum_sweep_hz=None,
    ):
        processed_slices = self._process_slices()
        step_ms = self.chopper.step_ms
        length = round(len(hits) * step_ms)
        track_block = AudioSegment.silent(duration=length, frame_rate=self.sr)
        drum_block = AudioSegment.silent(duration=length, frame_rate=self.sr)
        bass_block = AudioSegment.silent(duration=length, frame_rate=self.sr)

        for i, hit in enumerate(hits):
            name, hit_gain_db = hit if isinstance(hit, tuple) else (hit, 0)
            if name == "rest":
                continue
            position = round(i * step_ms)
            segment = self.chopper.slices[name]
            drum_hit = processed_slices[name] + (drum_gain_db + hit_gain_db)
            track_block = track_block.overlay(drum_hit, position=position)
            drum_block = drum_block.overlay(drum_hit, position=position)

            if bass_on_kicks and name == "kick":
                root_freq = self.theme.bass_roots[step_chords[i]]
                sub_bass = self.bass_synth.generate_note(len(segment), self.sr, root_freq)
                track_block = track_block.overlay(sub_bass - 6, position=position)
                bass_block = bass_block.overlay(sub_bass, position=position)

        for index, (step, interval) in enumerate(bass_notes):
            position = round(step * step_ms)
            if index + 1 < len(bass_notes):
                next_step = bass_notes[index + 1][0]
            else:
                next_step = len(hits)
            steps = min(next_step - step, MAX_BASS_NOTE_STEPS)
            duration = round((step + steps) * step_ms) - position
            freq = self.theme.bass_roots[step_chords[step]] * BASS_INTERVALS[interval]
            note = self.bass_synth.generate_note(duration, self.sr, freq)
            track_block = track_block.overlay(note - 6, position=position)
            bass_block = bass_block.overlay(note, position=position)

        if drum_sweep_hz is not None:
            drum_block = self.lowpass_sweep(drum_block, *drum_sweep_hz)
            track_block = drum_block.overlay(bass_block - 6)

        return track_block.fade_out(5), drum_block.fade_out(5), bass_block.fade_out(5)

    def _render_pad(self, progression, bars, length, steps_per_bar):
        if self.pad_synth is None:
            return AudioSegment.silent(duration=length, frame_rate=self.sr)

        bar_ms = steps_per_bar * self.chopper.step_ms
        bars_per_chord = self.theme.bars_per_chord
        overlap_ms = self.pad_synth.overlap_ms(self.pad_rng)
        pad_block = AudioSegment.silent(duration=length, frame_rate=self.sr)
        chords = list(zip(progression, range(0, bars, bars_per_chord)))

        for index, (chord_name, bar) in enumerate(chords):
            start = round(bar * bar_ms)
            end = round(min(bar + bars_per_chord, bars) * bar_ms)
            is_last = index == len(chords) - 1
            duration = end - start if is_last else end - start + overlap_ms
            frequencies = self.theme.pad_voicings[chord_name]
            chord = self.pad_synth.generate_chord(
                frequencies, duration, self.sr, self.pad_rng, bar_ms / STEPS_PER_BAR
            )
            pad_block = pad_block.overlay(chord, position=start)

        return pad_block

    def _render_lead(self, progression, bars, length):
        if self.lead is None:
            return AudioSegment.silent(duration=length, frame_rate=self.sr)

        bars_per_chord = self.theme.bars_per_chord
        bar_chords = [
            progression[min(bar // bars_per_chord, len(progression) - 1)]
            for bar in range(bars)
        ]
        tones_per_bar = [self.theme.lead_tones[chord] for chord in bar_chords]
        return self.lead.generate(
            tones_per_bar, self.chopper.step_ms, length, self.sr, self.lead_rng
        )

    def add_section(
        self,
        bars=2,
        use_bass=False,
        use_pad=False,
        generate_pattern=None,
        drum_sweep_hz=None,
        samples=None,
    ):
        start_ms = sum(len(section) for section in self.track_sections)
        generate_pattern = generate_pattern or self.theme.generate_pattern
        hits = generate_pattern(bars, self.chopper.rng)
        bass_plays = self.bass_synth is not None and (
            self.theme.bass_on_every_kick or use_bass
        )
        generate_bass_pattern = getattr(self.theme, "generate_bass_pattern", None)
        if bass_plays and generate_bass_pattern is not None:
            bass_notes = generate_bass_pattern(bars, self.bass_rng)
            bass_on_kicks = False
        else:
            bass_notes = ()
            bass_on_kicks = bass_plays

        bars_per_chord = self.theme.bars_per_chord
        num_chords = math.ceil(bars / bars_per_chord) if use_pad else 1
        progression = self.theme.generate_progression(num_chords, self.chord_rng)
        steps_per_bar = len(hits) // bars
        steps_per_chord = steps_per_bar * bars_per_chord
        step_chords = [
            progression[min(i // steps_per_chord, len(progression) - 1)]
            for i in range(len(hits))
        ]

        track_block, drum_block, bass_block = self._render_hits(
            hits,
            bass_on_kicks,
            self.theme.drum_gain_db,
            step_chords,
            bass_notes,
            drum_sweep_hz,
        )

        if use_pad:
            pad_block = self._render_pad(
                progression, bars, len(track_block), steps_per_bar
            )
            lead_block = self._render_lead(progression, bars, len(track_block))
            pad_block = pad_block + self.theme.pad_gain_db
            lead_block = lead_block + self.theme.lead_gain_db
            if self.pad_pan is not None:
                pad_block = self.auto_pan(pad_block, start_ms, **self.pad_pan)
                lead_block = self.auto_pan(lead_block, start_ms, **self.lead_pan)
            self.track_sections.append(
                track_block.overlay(pad_block.overlay(lead_block))
            )
            self.pad_sections.append(pad_block)
            self.lead_sections.append(lead_block)
        else:
            silence = AudioSegment.silent(duration=len(track_block))
            self.track_sections.append(track_block)
            self.pad_sections.append(silence)
            self.lead_sections.append(silence)

        if samples in self.samples:
            section = self.track_sections[-1]
            placements = self.samples[samples].place(
                len(track_block), self.sr, steps_per_bar * self.chopper.step_ms
            )
            for phrase, position in placements:
                section = section.overlay(phrase, position=position)
            self.track_sections[-1] = section

        self.drum_sections.append(drum_block)
        self.bass_sections.append(bass_block)
        return self

    def add_fill(self, bars=0.5):
        hits = self.chopper.generate_fill(bars)
        track_block, drum_block, bass_block = self._render_hits(
            hits, bass_on_kicks=False, drum_gain_db=self.theme.drum_gain_db + 2
        )

        silence = AudioSegment.silent(duration=len(track_block))
        self.track_sections.append(track_block)
        self.drum_sections.append(drum_block)
        self.bass_sections.append(bass_block)
        self.pad_sections.append(silence)
        self.lead_sections.append(silence)
        return self

    def compose_full_track(self):
        names = " -> ".join(section["name"] for section in self.theme.arrangement)
        print(f"Arranging track using theme '{self.theme.name}': {names}")

        for section in self.theme.arrangement:
            if section["type"] == "fill":
                self.add_fill(bars=section["bars"])
            else:
                self.add_section(
                    bars=section["bars"],
                    use_bass=section["bass"],
                    use_pad=section["pad"],
                    generate_pattern=section.get("pattern"),
                    drum_sweep_hz=section.get("drum_sweep_hz"),
                    samples=section.get("samples"),
                )

        return self

    def _join_sections(self, sections):
        joined = AudioSegment.empty()
        for section in sections:
            joined += section
        return joined

    def export(self, track_path, drums_path, bass_path, pad_path, lead_path):
        stems = [
            (self.track_sections, track_path),
            (self.drum_sections, drums_path),
            (self.bass_sections, bass_path),
            (self.pad_sections, pad_path),
            (self.lead_sections, lead_path),
        ]
        for sections, path in stems:
            self._join_sections(sections).export(path, format="wav")

        paths = ", ".join(path for _, path in stems)
        print(f"Exported stems successfully: {paths}")