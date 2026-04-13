from pydantic import BaseModel, Field


class ScheduleQuery(BaseModel):
    date: str
    timezone: str = Field(default="America/Chicago")


class KnowledgeQuery(BaseModel):
    query: str
    scope: str = Field(default="operations")
    top_k: int = Field(default=5, ge=1, le=10)


class DraftEmailRequest(BaseModel):
    to: list[str]
    subject: str
    body: str
