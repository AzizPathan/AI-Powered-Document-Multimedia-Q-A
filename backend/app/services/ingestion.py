from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import TranscriptSegment, UploadedFile, User
from app.services.text import clean_text, extract_pdf_text, summarize_text
from app.services.transcription import transcribe_media

PDF_TYPES = {"application/pdf"}
AUDIO_PREFIX = "audio/"
VIDEO_PREFIX = "video/"
MEDIA_TRANSCRIPTION_UNAVAILABLE_SUMMARY = (
    "Media uploaded successfully. Transcript, summary, timestamps, and Q&A will be available "
    "after transcription is configured."
)


def is_allowed(content_type: str) -> bool:
    return content_type in PDF_TYPES or content_type.startswith(AUDIO_PREFIX) or content_type.startswith(VIDEO_PREFIX)


async def save_upload(upload: UploadFile) -> Path:
    settings = get_settings()
    upload_dir = settings.resolved_upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(upload.filename or "upload.bin").name
    destination = upload_dir / f"{uuid4().hex}_{safe_name}"
    content = await upload.read()
    destination.write_bytes(content)
    return destination


async def ingest_file(db: Session, owner: User, upload: UploadFile) -> UploadedFile:
    content_type = upload.content_type or "application/octet-stream"
    if not is_allowed(content_type):
        raise ValueError("Only PDF, audio, and video files are supported")

    path = await save_upload(upload)
    segments: list[dict[str, float | str]] = []
    if content_type in PDF_TYPES:
        extracted_text = extract_pdf_text(path)
    elif content_type.startswith(AUDIO_PREFIX) or content_type.startswith(VIDEO_PREFIX):
        segments = transcribe_media(path)
        extracted_text = clean_text(" ".join(str(segment["text"]) for segment in segments))
    else:
        extracted_text = ""

    file_record = UploadedFile(
        owner_id=owner.id,
        filename=Path(upload.filename or path.name).name,
        content_type=content_type,
        storage_path=str(path),
        extracted_text=extracted_text,
        summary=summarize_text(extracted_text) if extracted_text else MEDIA_TRANSCRIPTION_UNAVAILABLE_SUMMARY,
    )
    db.add(file_record)
    db.flush()

    for segment in segments:
        db.add(
            TranscriptSegment(
                file_id=file_record.id,
                start_seconds=float(segment["start"]),
                end_seconds=float(segment["end"]),
                text=str(segment["text"]),
            )
        )
    db.commit()
    db.refresh(file_record)
    return file_record
