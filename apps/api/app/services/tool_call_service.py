import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import ToolCall


class ToolCallService:
    def create_requested(
        self,
        session: Session,
        *,
        conversation_id: str,
        tool_name: str,
        arguments: dict,
        requires_approval: bool,
    ) -> ToolCall:
        item = ToolCall(
            conversation_id=conversation_id,
            tool_name=tool_name,
            arguments=json.dumps(arguments),
            status="pending_approval" if requires_approval else "requested",
            requires_approval=requires_approval,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def mark_completed(self, session: Session, tool_call_id: str, result: dict) -> ToolCall:
        item = session.get(ToolCall, tool_call_id)
        if item is None:
            raise KeyError(f"Tool call '{tool_call_id}' not found")
        item.status = "completed"
        item.result = json.dumps(result)
        item.completed_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def mark_failed(self, session: Session, tool_call_id: str, error_message: str) -> ToolCall:
        item = session.get(ToolCall, tool_call_id)
        if item is None:
            raise KeyError(f"Tool call '{tool_call_id}' not found")
        item.status = "failed"
        item.result = json.dumps({"error": error_message})
        item.completed_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def list_by_conversation(self, session: Session, conversation_id: str) -> list[ToolCall]:
        stmt = select(ToolCall).where(ToolCall.conversation_id == conversation_id).order_by(ToolCall.created_at.asc())
        return list(session.scalars(stmt))
