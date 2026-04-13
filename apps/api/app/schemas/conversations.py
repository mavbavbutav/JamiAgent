from datetime import datetime
from pydantic import BaseModel


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationCreateRequest(BaseModel):
    title: str


class ConversationCreateResponse(BaseModel):
    id: str
    title: str


class MessageRecord(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
