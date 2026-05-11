from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import auth, chat, files


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="AI Document & Multimedia Q&A", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup() -> None:
        init_db()

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "message": "AI Document & Multimedia Q&A API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "auth": "/api/auth",
                "files": "/api/files",
                "chat": "/api/chat"
            }
        }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(files.router)
    app.include_router(chat.router)
    return app


app = create_app()
