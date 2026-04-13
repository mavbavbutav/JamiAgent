from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.orchestrator import AssistantOrchestrator
from app.db.session import get_db_session
from app.schemas.chat import ChatSendRequest, ChatSendResponse
from app.services.audit_service import AuditService
from app.services.container import (
    get_audit_service,
    get_conversation_service,
    get_orchestrator,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatSendResponse)
def send_message(
    payload: ChatSendRequest,
    orchestrator: AssistantOrchestrator = Depends(get_orchestrator),
    conversation_service: ConversationService = Depends(get_conversation_service),
    audit_service: AuditService = Depends(get_audit_service),
    session: Session = Depends(get_db_session),
) -> ChatSendResponse:
    conversation = conversation_service.get_or_create(session, payload.conversation_id)
    conversation_service.add_message(session, conversation.id, "user", payload.message)

    response = orchestrator.handle_message(conversation.id, payload.message, session=session)
    conversation_service.add_message(session, conversation.id, "assistant", response.reply)

    audit_service.log_event(
        session,
        event_type="chat_turn_completed",
        target_type="conversation",
        target_id=conversation.id,
        payload={"response_id": response.response_id, "used_tools": response.used_tools},
    )
    return response
