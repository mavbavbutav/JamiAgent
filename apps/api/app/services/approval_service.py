import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Approval


class ApprovalService:
    """Database-backed approval workflow service."""

    def create_pending(self, session: Session, tool_name: str, payload: dict) -> Approval:
        item = Approval(tool_name=tool_name, payload=json.dumps(payload), status="pending")
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def list_items(self, session: Session) -> list[Approval]:
        stmt = select(Approval).order_by(Approval.created_at.desc())
        return list(session.scalars(stmt))

    def decide(self, session: Session, approval_id: str, approve: bool) -> Approval:
        item = session.get(Approval, approval_id)
        if item is None:
            raise KeyError(f"Approval '{approval_id}' not found")
        item.status = "approved" if approve else "denied"
        item.decided_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
