import sys
import os
import shutil
import wave
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converter import ConversionEngine
from pydub import AudioSegment

ffmpeg_available = shutil.which("ffmpeg") is not None
requires_ffmpeg = pytest.mark.skipif(not ffmpeg_available, reason="ffmpeg not in PATH")

try:
    import pillow_heif
    from PIL import Image
    pillow_available = True
except ImportError:
    pillow_available = False

requires_pillow = pytest.mark.skipif(not pillow_available, reason="Pillow/pillow-heif not installed")


# --- ConversionEngine base ---

def test_check_ffmpeg_returns_bool():
    engine = ConversionEngine()
    assert isinstance(engine.check_ffmpeg(), bool)


def test_convert_file_returns_error_for_missing_input(tmp_path):
    engine = ConversionEngine()
    success, error = engine.convert_file("/nonexistent/file.mp3", str(tmp_path / "out.wav"), "wav")
    assert success is False
    assert len(error) > 0


def test_convert_file_returns_error_for_unknown_format(tmp_path):
    engine = ConversionEngine()
    dummy = tmp_path / "file.xyz"
    dummy.write_bytes(b"dummy")
    success, error = engine.convert_file(str(dummy), str(tmp_path / "out.wav"), "wav")
    assert success is False


# --- Audio ---

@requires_ffmpeg
def test_convert_mp3_to_wav(tmp_path):
    audio = AudioSegment.silent(duration=300)
    mp3 = str(tmp_path / "test.mp3")
    wav = str(tmp_path / "out.wav")
    audio.export(mp3, format="mp3")
    success, error = ConversionEngine().convert_file(mp3, wav, "wav")
    assert success is True and os.path.exists(wav)


@requires_ffmpeg
def test_convert_wav_to_mp3(tmp_path):
    audio = AudioSegment.silent(duration=300)
    wav = str(tmp_path / "test.wav")
    mp3 = str(tmp_path / "out.mp3")
    audio.export(wav, format="wav")
    success, error = ConversionEngine().convert_file(wav, mp3, "mp3")
    assert success is True and os.path.getsize(mp3) > 0


@requires_ffmpeg
def test_convert_wav_to_flac(tmp_path):
    audio = AudioSegment.silent(duration=300)
    wav = str(tmp_path / "test.wav")
    flac = str(tmp_path / "out.flac")
    audio.export(wav, format="wav")
    success, error = ConversionEngine().convert_file(wav, flac, "flac")
    assert success is True and os.path.exists(flac)


@requires_ffmpeg
def test_convert_flac_to_mp3(tmp_path):
    audio = AudioSegment.silent(duration=300)
    wav = str(tmp_path / "test.wav")
    flac = str(tmp_path / "test.flac")
    mp3 = str(tmp_path / "out.mp3")
    audio.export(wav, format="wav")
    AudioSegment.from_wav(wav).export(flac, format="flac")
    success, error = ConversionEngine().convert_file(flac, mp3, "mp3")
    assert success is True and os.path.getsize(mp3) > 0


# --- Image ---

@requires_pillow
def test_convert_png_to_jpg(tmp_path):
    from PIL import Image
    png = str(tmp_path / "test.png")
    jpg = str(tmp_path / "out.jpg")
    Image.new("RGB", (10, 10), color=(255, 0, 0)).save(png, format="PNG")
    success, error = ConversionEngine().convert_file(png, jpg, "jpg")
    assert success is True and os.path.exists(jpg)


@requires_pillow
def test_convert_jpg_to_png(tmp_path):
    from PIL import Image
    jpg = str(tmp_path / "test.jpg")
    png = str(tmp_path / "out.png")
    Image.new("RGB", (10, 10), color=(0, 255, 0)).save(jpg, format="JPEG")
    success, error = ConversionEngine().convert_file(jpg, png, "png")
    assert success is True and os.path.exists(png)


@requires_pillow
def test_convert_rgba_png_to_jpg_strips_alpha(tmp_path):
    from PIL import Image
    png = str(tmp_path / "rgba.png")
    jpg = str(tmp_path / "out.jpg")
    Image.new("RGBA", (10, 10), color=(0, 0, 255, 128)).save(png, format="PNG")
    success, error = ConversionEngine().convert_file(png, jpg, "jpg")
    assert success is True
