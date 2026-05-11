from pathlib import Path

from openai import OpenAI, OpenAIError

from app.config import get_settings
from app.services.text import clean_text


def transcription_unavailable_message() -> str:
    return (
        "Transcript is not available for this media file yet."
    )


def fallback_segments() -> list[dict[str, float | str]]:
    return []


def transcribe_media(path: Path) -> list[dict[str, float | str]]:
    settings = get_settings()
    sidecar = path.with_suffix(".txt")
    if sidecar.exists():
        text = clean_text(sidecar.read_text(encoding="utf-8"))
        return [{"start": 0.0, "end": 30.0, "text": text}]

    if settings.openai_api_key:
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            with path.open("rb") as media:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=media,
                    response_format="verbose_json",
                )
        except OpenAIError:
            return fallback_segments()

        segments = getattr(transcript, "segments", None) or []
        return [
            {
                "start": float(getattr(segment, "start", 0.0)),
                "end": float(getattr(segment, "end", 0.0)),
                "text": clean_text(getattr(segment, "text", "")),
            }
            for segment in segments
            if getattr(segment, "text", "").strip()
        ]

    return fallback_segments()
