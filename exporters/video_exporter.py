import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment


class VideoExporter:
    def __init__(
        self,
        width=1920,
        height=1080,
        font_path="/System/Library/Fonts/Avenir Next.ttc",
    ):
        self.width = width
        self.height = height
        self.font_path = font_path

    def export(self, audio_path, video_path, image_path, title, subtitle):
        self.draw_thumbnail(audio_path, image_path, title, subtitle)
        duration_s = len(AudioSegment.from_file(audio_path)) / 1000.0
        bars_width = int(self.width * 0.8)
        bars_height = self.height // 3
        bars_top = round(self.height * 0.42 - bars_height / 2)
        bars = (
            f"showfreqs=s={bars_width}x{bars_height}:mode=bar:fscale=log"
            ":ascale=sqrt:win_size=2048:colors=0x7FA0E0:rate=30"
        )
        filters = (
            f"[1:a]{bars},format=gbrp,"
            f"pad={self.width}:{self.height}:(ow-iw)/2:{bars_top}:black[bars];"
            "[0:v]format=gbrp[background];"
            "[background][bars]blend=all_mode=screen:shortest=1,"
            "scale=out_range=tv,format=yuv420p[video]"
        )

        with tempfile.NamedTemporaryFile(suffix=".png") as background:
            image = self._gradient()
            self._draw_titles(image, title, subtitle)
            image.save(background.name)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-framerate",
                    "30",
                    "-i",
                    background.name,
                    "-i",
                    audio_path,
                    "-filter_complex",
                    filters,
                    "-map",
                    "[video]",
                    "-map",
                    "1:a",
                    "-t",
                    f"{duration_s:.3f}",
                    "-r",
                    "30",
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "320k",
                    "-movflags",
                    "+faststart",
                    video_path,
                ],
                check=True,
                capture_output=True,
            )
        print(f"Exported video: {video_path} (thumbnail: {image_path})")

    def draw_thumbnail(self, audio_path, image_path, title, subtitle):
        image = self._gradient()
        self._draw_waveform(image, audio_path)
        self._draw_titles(image, title, subtitle)
        image.save(image_path, quality=90)

    def _draw_titles(self, image, title, subtitle):
        draw = ImageDraw.Draw(image)
        title_font = self._font(120)
        subtitle_font = self._font(44)
        draw.text(
            (self.width / 2, self.height * 0.8),
            title,
            font=title_font,
            fill=(220, 224, 235),
            anchor="mm",
        )
        draw.text(
            (self.width / 2, self.height * 0.9),
            subtitle,
            font=subtitle_font,
            fill=(130, 140, 162),
            anchor="mm",
        )

    def _gradient(self):
        top = np.array([16, 20, 36], dtype=np.float64)
        bottom = np.array([4, 5, 10], dtype=np.float64)
        blend = np.linspace(0, 1, self.height)[:, None]
        rows = top * (1 - blend) + bottom * blend
        pixels = np.repeat(rows[:, None, :], self.width, axis=1)
        return Image.fromarray(pixels.astype(np.uint8), "RGB")

    def _draw_waveform(self, image, audio_path):
        audio = AudioSegment.from_file(audio_path).set_channels(1)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float64)

        columns = int(self.width * 0.8)
        chunks = np.array_split(samples, columns)
        levels = np.array([np.sqrt(np.mean(chunk ** 2)) for chunk in chunks])
        levels /= levels.max()

        draw = ImageDraw.Draw(image)
        left = (self.width - columns) / 2
        centre = self.height * 0.42
        max_height = self.height * 0.22
        for index, level in enumerate(levels):
            half = level * max_height
            x = left + index
            draw.line(
                [(x, centre - half), (x, centre + half)],
                fill=(70, 88, 128),
            )

    def _font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except OSError:
            return ImageFont.load_default(size=size)
