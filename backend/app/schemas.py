from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class AuthPayload(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    summary: str
    created_at: datetime | None = None
    transcription_status: str = "ready"


class AskRequest(BaseModel):
    file_id: int
    question: str


class Citation(BaseModel):
    text: str
    start_seconds: float | None = None
    end_seconds: float | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]


class TimestampResponse(BaseModel):
    topic: str
    matches: list[Citation]
