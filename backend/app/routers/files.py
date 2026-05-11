from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse as MediaFileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import UploadedFile, User
from app.schemas import Citation, FileResponse, TimestampResponse
from app.services.ingestion import ingest_file
from app.services.retrieval import find_topic_segments

router = APIRouter(prefix="/api/files", tags=["files"])


def get_owned_file(db: Session, user: User, file_id: int) -> UploadedFile:
    record = db.scalar(
        select(UploadedFile)
        .options(selectinload(UploadedFile.segments))
        .where(UploadedFile.id == file_id, UploadedFile.owner_id == user.id)
    )
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    return record


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    upload: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UploadedFile:
    try:
        return await ingest_file(db, user, upload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[FileResponse])
def list_files(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[UploadedFile]:
    return list(db.scalars(select(UploadedFile).where(UploadedFile.owner_id == user.id).order_by(UploadedFile.id.desc())))


@router.get("/{file_id}/summary")
def get_summary(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, str]:
    record = get_owned_file(db, user, file_id)
    return {"summary": record.summary}


@router.get("/{file_id}/timestamps", response_model=TimestampResponse)
def get_timestamps(
    file_id: int,
    topic: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TimestampResponse:
    record = get_owned_file(db, user, file_id)
    matches = find_topic_segments(topic, record.segments)
    return TimestampResponse(
        topic=topic,
        matches=[
            Citation(text=match.text, start_seconds=match.start_seconds, end_seconds=match.end_seconds)
            for match in matches
        ],
    )


@router.get("/{file_id}/media")
def get_media(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> MediaFileResponse:
    record = get_owned_file(db, user, file_id)
    path = Path(record.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored media not found")
    return MediaFileResponse(path, media_type=record.content_type, filename=record.filename)
