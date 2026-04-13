from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Conversation, Message


class ConversationService:
    def get_or_create(self, session: Session, conversation_id: str | None) -> Conversation:
        if conversation_id:
            conversation = session.get(Conversation, conversation_id)
            if conversation:
                return conversation
        conversation = Conversation(title="New Conversation")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    def list_conversations(self, session: Session) -> list[Conversation]:
        stmt = select(Conversation).order_by(Conversation.updated_at.desc())
        return list(session.scalars(stmt))

    def create(self, session: Session, title: str) -> Conversation:
        conversation = Conversation(title=title)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation


    def exists(self, session: Session, conversation_id: str) -> bool:
        return session.get(Conversation, conversation_id) is not None

    def list_messages(self, session: Session, conversation_id: str) -> list[Message]:
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        return list(session.scalars(stmt))

    def add_message(self, session: Session, conversation_id: str, role: str, content: str) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        session.add(message)
        session.commit()
        session.refresh(message)
        return message
