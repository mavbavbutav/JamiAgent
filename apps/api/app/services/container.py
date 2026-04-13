from functools import lru_cache

from app.agents.orchestrator import AssistantOrchestrator
from app.config import Settings, get_settings
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.conversation_service import ConversationService
from app.services.openai_client import OpenAIClientService
from app.services.tool_registry import ToolRegistryService


@lru_cache
def get_tool_registry() -> ToolRegistryService:
    return ToolRegistryService()


@lru_cache
def get_approval_service() -> ApprovalService:
    return ApprovalService()


@lru_cache
def get_conversation_service() -> ConversationService:
    return ConversationService()


@lru_cache
def get_audit_service() -> AuditService:
    return AuditService()


@lru_cache
def get_openai_client() -> OpenAIClientService:
    settings: Settings = get_settings()
    return OpenAIClientService(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
    )


@lru_cache
def get_orchestrator() -> AssistantOrchestrator:
    return AssistantOrchestrator(
        openai_client=get_openai_client(),
        tool_registry=get_tool_registry(),
        approval_service=get_approval_service(),
    )
