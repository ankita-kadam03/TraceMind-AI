import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import os
from faster_whisper import WhisperModel
from opentelemetry import trace

tracer = trace.get_tracer("speech")

SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio(duration: int = 5) -> str:
    """Record audio from mic and save to temp wav file. Returns file path."""
    with tracer.start_as_current_span("record_audio") as span:
        span.set_attribute("duration_seconds", duration)
        span.set_attribute("sample_rate", SAMPLE_RATE)

        print(f"\n[MIC] Recording for {duration} seconds... speak now!")
        audio = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
        )
        sd.wait()
        print("[MIC] Recording complete.")

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(tmp.name, SAMPLE_RATE, audio)
        span.set_attribute("wav_path", tmp.name)
        return tmp.name


def transcribe(wav_path: str, model_size: str = "base") -> str:
    """Transcribe a wav file to text using faster-whisper (runs on CPU)."""
    with tracer.start_as_current_span("transcribe") as span:
        span.set_attribute("model_size", model_size)
        span.set_attribute("wav_path", wav_path)

        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(wav_path, beam_size=5)

        text = " ".join(seg.text.strip() for seg in segments)
        span.set_attribute("transcript", text)
        span.set_attribute("language", info.language)

        os.unlink(wav_path)
        return text.strip()


def record_and_transcribe(duration: int = 5, model_size: str = "base") -> str:
    """Pipeline: mic → wav → text."""
    with tracer.start_as_current_span("record_and_transcribe"):
        wav_path = record_audio(duration)
        return transcribe(wav_path, model_size)
