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


def test_check_ffmpeg_returns_bool():
    engine = ConversionEngine()
    result = engine.check_ffmpeg()
    assert isinstance(result, bool)


def test_convert_file_returns_error_for_missing_input(tmp_path):
    engine = ConversionEngine()
    wav_path = str(tmp_path / "output.wav")
    success, error = engine.convert_file("/nonexistent/path.mp3", wav_path, "wav")
    assert success is False
    assert len(error) > 0


@requires_ffmpeg
def test_convert_mp3_to_wav_returns_success(tmp_path):
    audio = AudioSegment.silent(duration=500)
    mp3_path = str(tmp_path / "test.mp3")
    wav_path = str(tmp_path / "output.wav")
    audio.export(mp3_path, format="mp3")

    engine = ConversionEngine()
    success, error = engine.convert_file(mp3_path, wav_path, "wav")

    assert success is True
    assert error == ""
    assert os.path.exists(wav_path)


@requires_ffmpeg
def test_convert_mp3_to_wav_creates_valid_wav(tmp_path):
    audio = AudioSegment.silent(duration=500)
    mp3_path = str(tmp_path / "test.mp3")
    wav_path = str(tmp_path / "output.wav")
    audio.export(mp3_path, format="mp3")

    engine = ConversionEngine()
    engine.convert_file(mp3_path, wav_path, "wav")

    with wave.open(wav_path, "rb") as f:
        assert f.getnframes() > 0


@requires_ffmpeg
def test_convert_wav_to_mp3_returns_success(tmp_path):
    audio = AudioSegment.silent(duration=500)
    wav_path = str(tmp_path / "test.wav")
    mp3_path = str(tmp_path / "output.mp3")
    audio.export(wav_path, format="wav")

    engine = ConversionEngine()
    success, error = engine.convert_file(wav_path, mp3_path, "mp3")

    assert success is True
    assert error == ""
    assert os.path.exists(mp3_path)
    assert os.path.getsize(mp3_path) > 0
