from datetime import datetime
from pydantic import BaseModel


class ApprovalItem(BaseModel):
    id: str
    tool_name: str
    status: str
    created_at: datetime


class ApprovalDecisionResponse(BaseModel):
    id: str
    status: str
