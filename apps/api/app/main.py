"""FastAPI application entrypoint for the Jami Agent backend."""

from fastapi import FastAPI

from app.config import Settings, get_settings
from app.db.bootstrap import init_db
from app.routes.approvals import router as approvals_router
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router
from app.routes.files import router as files_router
from app.routes.health import router as health_router


def create_application(settings: Settings) -> FastAPI:
    app = FastAPI(title="Jami Agent API", version="0.5.0", debug=settings.debug)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)
    app.include_router(approvals_router)
    app.include_router(files_router)

    return app


settings = get_settings()
app = create_application(settings)
