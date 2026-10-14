import io
import soundfile as sf
from pydub import AudioSegment


def waveform_to_segment(waveform, sr):
    buffer = io.BytesIO()
    sf.write(buffer, waveform, sr, format="WAV", subtype="PCM_16")
    buffer.seek(0)
    return AudioSegment.from_file(buffer, format="WAV")
