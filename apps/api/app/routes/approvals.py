from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.approvals import ApprovalDecisionResponse, ApprovalItem
from app.services.approval_service import ApprovalService
from app.services.container import get_approval_service

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalItem])
def list_approvals(
    approval_service: ApprovalService = Depends(get_approval_service),
    session: Session = Depends(get_db_session),
) -> list[ApprovalItem]:
    return [
        ApprovalItem(id=item.id, tool_name=item.tool_name, status=item.status, created_at=item.created_at)
        for item in approval_service.list_items(session)
    ]


@router.post("/{approval_id}/approve", response_model=ApprovalDecisionResponse)
def approve(
    approval_id: str,
    approval_service: ApprovalService = Depends(get_approval_service),
    session: Session = Depends(get_db_session),
) -> ApprovalDecisionResponse:
    try:
        item = approval_service.decide(session, approval_id, approve=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApprovalDecisionResponse(id=item.id, status=item.status)


@router.post("/{approval_id}/deny", response_model=ApprovalDecisionResponse)
def deny(
    approval_id: str,
    approval_service: ApprovalService = Depends(get_approval_service),
    session: Session = Depends(get_db_session),
) -> ApprovalDecisionResponse:
    try:
        item = approval_service.decide(session, approval_id, approve=False)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApprovalDecisionResponse(id=item.id, status=item.status)
