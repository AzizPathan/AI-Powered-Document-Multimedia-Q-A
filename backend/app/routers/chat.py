from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import ChatMessage, User
from app.rate_limit import check_rate_limit
from app.routers.files import get_owned_file
from app.schemas import AskRequest, AskResponse, Citation
from app.services.ai import answer_question, stream_answer
from app.services.retrieval import retrieve

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AskResponse:
    check_rate_limit(request)
    record = get_owned_file(db, user, payload.file_id)
    chunks = retrieve(payload.question, record.extracted_text, record.segments)
    answer = await answer_question(payload.question, chunks)
    db.add(ChatMessage(file_id=record.id, user_id=user.id, question=payload.question, answer=answer))
    db.commit()
    return AskResponse(
        answer=answer,
        citations=[
            Citation(text=chunk.text, start_seconds=chunk.start_seconds, end_seconds=chunk.end_seconds)
            for chunk in chunks
        ],
    )


@router.get("/stream")
async def stream(
    request: Request,
    file_id: int = Query(...),
    question: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    check_rate_limit(request)
    record = get_owned_file(db, user, file_id)
    chunks = retrieve(question, record.extracted_text, record.segments)

    async def events():
        async for token in stream_answer(question, chunks):
            yield f"data: {token}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
