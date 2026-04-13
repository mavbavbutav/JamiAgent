from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.conversations import (
    ConversationCreateRequest,
    ConversationCreateResponse,
    ConversationSummary,
    MessageRecord,
    ToolCallRecord,
)
from app.services.container import get_conversation_service, get_tool_call_service
from app.services.conversation_service import ConversationService
from app.services.tool_call_service import ToolCallService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
def list_conversations(
    conversation_service: ConversationService = Depends(get_conversation_service),
    session: Session = Depends(get_db_session),
) -> list[ConversationSummary]:
    rows = conversation_service.list_conversations(session)
    return [
        ConversationSummary(
            id=row.id,
            title=row.title,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


@router.post("", response_model=ConversationCreateResponse)
def create_conversation(
    payload: ConversationCreateRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
    session: Session = Depends(get_db_session),
) -> ConversationCreateResponse:
    conversation = conversation_service.create(session, payload.title)
    return ConversationCreateResponse(id=conversation.id, title=conversation.title)


@router.get("/{conversation_id}/messages", response_model=list[MessageRecord])
def list_messages(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    session: Session = Depends(get_db_session),
) -> list[MessageRecord]:
    if not conversation_service.exists(session, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = conversation_service.list_messages(session, conversation_id)
    return [
        MessageRecord(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        for message in messages
    ]


@router.get("/{conversation_id}/tool-calls", response_model=list[ToolCallRecord])
def list_tool_calls(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    tool_call_service: ToolCallService = Depends(get_tool_call_service),
    session: Session = Depends(get_db_session),
) -> list[ToolCallRecord]:
    if not conversation_service.exists(session, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    rows = tool_call_service.list_by_conversation(session, conversation_id)
    return [
        ToolCallRecord(
            id=row.id,
            conversation_id=row.conversation_id,
            tool_name=row.tool_name,
            status=row.status,
            requires_approval=row.requires_approval,
            created_at=row.created_at,
            completed_at=row.completed_at,
        )
        for row in rows
    ]
