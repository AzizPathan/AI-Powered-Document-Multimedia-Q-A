from pathlib import Path
import asyncio

import pytest

from app.config import Settings
from app.database import get_db
from app.models import TranscriptSegment
from app.rate_limit import _memory_hits, check_rate_limit
from app.services.ai import answer_question, fallback_answer, stream_answer
from app.services.ingestion import ingest_file, is_allowed
from app.services.retrieval import find_topic_segments, retrieve, retrieval_backend_name
from app.services.text import chunk_text, clean_text, summarize_text
from app.services.transcription import transcribe_media


def test_text_helpers():
    assert clean_text("hello\n\n world") == "hello world"
    assert chunk_text("One sentence. Two sentence.", max_chars=14) == ["One sentence.", "Two sentence."]
    assert summarize_text("") == "No readable text was extracted yet."


def test_get_db_closes_session():
    generator = get_db()
    db = next(generator)
    assert db.is_active
    with pytest.raises(StopIteration):
        next(generator)


def test_allowed_types():
    assert is_allowed("application/pdf")
    assert is_allowed("audio/mpeg")
    assert is_allowed("video/mp4")
    assert not is_allowed("image/png")


def test_retrieval_and_topics():
    segments = [
        TranscriptSegment(start_seconds=4, end_seconds=8, text="Pricing is discussed here."),
        TranscriptSegment(start_seconds=9, end_seconds=12, text="Deployment comes later."),
    ]
    chunks = retrieve("pricing", "", segments)
    assert chunks[0].start_seconds == 4
    assert find_topic_segments("deployment", segments)[0].start_seconds == 9
    assert retrieve("anything", "", []) == []


def test_vector_search_backend_is_available_or_falls_back():
    assert retrieval_backend_name() in {"faiss", "tfidf"}
    chunks = retrieve("pricing", "Pricing strategy. Deployment checklist.", [])
    assert chunks
    assert "Pricing" in chunks[0].text


def test_retrieval_fallback_and_empty_vectors(monkeypatch):
    import app.services.retrieval as retrieval_module

    monkeypatch.setattr(retrieval_module, "faiss", None)
    monkeypatch.setattr(retrieval_module, "np", None)
    assert retrieval_module.retrieval_backend_name() == "tfidf"
    assert retrieval_module.hashed_embedding("") == [0.0] * retrieval_module.VECTOR_DIMENSIONS
    assert retrieval_module.faiss_search("pricing", [retrieval_module.RetrievedChunk("Pricing", 1.0)], 1) == []
    assert retrieval_module.cosine({}, {"pricing": 1.0}) == 0.0
    chunks = retrieval_module.retrieve("unmatched", "Pricing strategy. Deployment checklist.", [], top_k=1)
    assert chunks


def test_faiss_search_edge_cases():
    import app.services.retrieval as retrieval_module

    corpus = [
        retrieval_module.RetrievedChunk("Pricing strategy", 1.0, 4, 8),
        retrieval_module.RetrievedChunk("Deployment checklist", 1.0, 9, 12),
    ]
    if retrieval_module.retrieval_backend_name() == "faiss":
        results = retrieval_module.faiss_search("pricing", corpus, 2)
        assert results[0].start_seconds == 4
        assert retrieval_module.faiss_search("", corpus, 2) == []


def test_fallback_answer_empty_and_with_context():
    assert "could not find" in fallback_answer("x", [])
    assert "Based on" in fallback_answer("x", retrieve("alpha", "Alpha beta. Gamma delta.", []))


def test_openai_answer_branch(monkeypatch):
    class Message:
        content = "openai answer"

    class Choice:
        message = Message()

    class Response:
        choices = [Choice()]

    class Completions:
        async def create(self, **kwargs):
            return Response()

    class Chat:
        completions = Completions()

    class Client:
        def __init__(self, api_key):
            self.chat = Chat()

    monkeypatch.setenv("OPENAI_API_KEY", "key")
    from app.config import get_settings
    import app.services.ai as ai_module

    get_settings.cache_clear()
    monkeypatch.setattr(ai_module, "AsyncOpenAI", Client)
    chunks = retrieve("alpha", "Alpha beta.", [])
    assert asyncio.run(answer_question("alpha", chunks)) == "openai answer"

    async def collect():
        return [token async for token in stream_answer("alpha", chunks)]

    streamed = asyncio.run(collect())
    assert streamed


def test_transcription_sidecar(tmp_path: Path):
    media = tmp_path / "clip.mp3"
    media.write_bytes(b"audio")
    media.with_suffix(".txt").write_text("hello transcript", encoding="utf-8")
    assert transcribe_media(media)[0]["text"] == "hello transcript"


def test_transcription_openai_branch(tmp_path: Path, monkeypatch):
    media = tmp_path / "clip.mp3"
    media.write_bytes(b"audio")

    class Segment:
        start = 1
        end = 2
        text = " topic text "

    class Response:
        segments = [Segment()]

    class Transcriptions:
        def create(self, **kwargs):
            return Response()

    class Audio:
        transcriptions = Transcriptions()

    class Client:
        def __init__(self, api_key):
            self.audio = Audio()

    monkeypatch.setenv("OPENAI_API_KEY", "key")
    from app.config import get_settings
    import app.services.transcription as transcription_module

    get_settings.cache_clear()
    monkeypatch.setattr(transcription_module, "OpenAI", Client)
    assert transcribe_media(media)[0]["text"] == "topic text"


def test_pdf_ingestion_path(client, token, monkeypatch):
    from app.database import SessionLocal
    from app.models import User
    import app.services.ingestion as ingestion_module

    class Upload:
        filename = "paper.pdf"
        content_type = "application/pdf"

        async def read(self):
            return b"%PDF"

    monkeypatch.setattr(ingestion_module, "extract_pdf_text", lambda path: "PDF content about launch.")
    with SessionLocal() as db:
        user = db.query(User).first()
        record = asyncio.run(ingest_file(db, user, Upload()))
        assert record.summary == "PDF content about launch."


def test_settings_parse_origins():
    settings = Settings(backend_cors_origins="http://a.test,http://b.test")
    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_docker_upload_dir_falls_back_for_local_dev():
    settings = Settings(upload_dir=Path("/app/uploads"))
    assert settings.resolved_upload_dir == Path("../runtime/uploads")


def test_docker_database_url_falls_back_for_local_dev():
    settings = Settings(database_url="postgresql+psycopg://qa_user:qa_password@db:5432/qa_app")
    assert settings.resolved_database_url == "sqlite+pysqlite:///./dev.db"


def test_memory_rate_limit(monkeypatch):
    class Client:
        host = "127.0.0.1"

    class Request:
        client = Client()

    _memory_hits.clear()
    monkeypatch.setenv("REDIS_URL", "")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "1")
    from app.config import get_settings

    get_settings.cache_clear()
    check_rate_limit(Request())
    with pytest.raises(Exception):
        check_rate_limit(Request())


def test_redis_rate_limit_branch(monkeypatch):
    class Client:
        host = "10.0.0.1"

    class Request:
        client = Client()

    class FakeRedis:
        calls = 0

        def incr(self, key):
            self.calls += 1
            return self.calls

        def expire(self, key, seconds):
            return True

    class RedisFactory:
        @staticmethod
        def from_url(*args, **kwargs):
            return FakeRedis()

    monkeypatch.setenv("REDIS_URL", "redis://example")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "1")
    from app.config import get_settings
    import app.rate_limit as rate_module

    get_settings.cache_clear()
    monkeypatch.setattr(rate_module.redis, "Redis", RedisFactory)
    check_rate_limit(Request())
