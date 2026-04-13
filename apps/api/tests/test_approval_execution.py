from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.services.approval_service import ApprovalService
from app.models.entities import ToolCall
from app.services.tool_call_service import ToolCallService


def test_approve_endpoint_executes_pending_tool_call():
    approval_service = ApprovalService()
    tool_call_service = ToolCallService()

    with SessionLocal() as session:
        tool_call = tool_call_service.create_requested(
            session,
            conversation_id="conv_test_approval",
            tool_name="draft_email",
            arguments={"to": ["julie@example.com"], "subject": "Summary", "body": "Hello"},
            requires_approval=True,
        )
        tool_call_id = tool_call.id

        approval = approval_service.create_pending(
            session,
            tool_name="draft_email",
            payload={
                "tool_call_id": tool_call_id,
                "arguments": {"to": ["julie@example.com"], "subject": "Summary", "body": "Hello"},
            },
        )

    with TestClient(app) as client:
        response = client.post(f"/approvals/{approval.id}/approve")
        assert response.status_code == 200

    with SessionLocal() as session:
        updated = session.get(ToolCall, tool_call_id)
        assert updated is not None
        assert updated.status == "completed"
        assert updated.result is not None
