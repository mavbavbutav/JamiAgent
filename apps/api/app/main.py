"""Entry point for the FastAPI application.

This module wires together the core components of the professional
assistant backend. It defines the FastAPI instance and registers
routes, middleware and exception handlers. For now, it exposes
minimal endpoints for health checking and a stubbed chat interface.

To create a fully functioning assistant, implement the agent logic
in `app/agents`, tool wrappers in `app/tools`, and route handlers
in `app/routes`. See the documentation in `docs/` for more details.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from .config import Settings, get_settings


class ChatRequest(BaseModel):
    """Payload for sending a chat message to the assistant."""
    conversation_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    """Response returned by the assistant."""
    conversation_id: str
    reply: str


def create_application(settings: Settings) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Professional Assistant API", version="0.1.0")

    @app.get("/health", summary="Health check", tags=["system"])
    def health() -> dict[str, str]:
        """Return a simple health check response."""
        return {"status": "ok"}

    @app.post("/chat/send", response_model=ChatResponse, summary="Send a chat message")
    async def chat_send(chat_request: ChatRequest, settings: Settings = Depends(get_settings)) -> ChatResponse:
        """Handle a chat message and return the assistant's reply.

        This is a stub implementation. The real assistant should invoke the
        OpenAI API via the agent orchestrator, handle tool calls, manage
        conversation state and record audit logs.
        """
        # TODO: load or create a conversation record in the database
        conversation_id = chat_request.conversation_id or "conv_123"

        # TODO: orchestrate the call to the OpenAI model, handle tool calls, etc.
        reply_text = (
            "This is a placeholder response. Implement the agent logic "
            "to get meaningful answers from the assistant."
        )

        return ChatResponse(conversation_id=conversation_id, reply=reply_text)

    return app


settings = get_settings()
app = create_application(settings)