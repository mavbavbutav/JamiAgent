import json

from sqlalchemy.orm import Session

from app.models.entities import AuditLog


class AuditService:
    def log_event(
        self,
        session: Session,
        *,
        event_type: str,
        target_type: str,
        target_id: str,
        payload: dict,
    ) -> AuditLog:
        item = AuditLog(
            event_type=event_type,
            target_type=target_type,
            target_id=target_id,
            payload=json.dumps(payload),
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
