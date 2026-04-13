from pydantic import BaseModel, Field


class ChatSendRequest(BaseModel):
    conversation_id: str | None = Field(default=None)
    message: str = Field(min_length=1, max_length=8000)


class ChatSendResponse(BaseModel):
    conversation_id: str
    response_id: str
    reply: str
    used_tools: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    approval_id: str | None = None
