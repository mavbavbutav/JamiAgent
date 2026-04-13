import json

from app.agents.orchestrator import AssistantOrchestrator
from app.services.approval_service import ApprovalService
from app.services.tool_call_service import ToolCallService
from app.services.tool_registry import ToolRegistryService, ToolSpec


class FakeOpenAIClient:
    def create_response(self, message, conversation_id=None, tools=None):
        assert tools, "tools should be provided to model"
        return {
            "id": "resp_initial",
            "conversation_id": conversation_id or "conv_test",
            "output_text": "",
            "tool_calls": [
                {
                    "id": "call_1",
                    "name": "search_knowledge_base",
                    "arguments": json.dumps({"query": "after-hours support", "scope": "operations", "top_k": 1}),
                }
            ],
        }

    def create_response_with_tool_outputs(self, *, previous_response_id, tool_outputs, conversation_id):
        assert previous_response_id == "resp_initial"
        assert tool_outputs and tool_outputs[0]["type"] == "function_call_output"
        return {
            "id": "resp_final",
            "conversation_id": conversation_id,
            "output_text": "Use the after-hours SOP and page the on-call lead.",
            "tool_calls": [],
        }


class FakeApprovalOpenAIClient:
    def create_response(self, message, conversation_id=None, tools=None):
        return {
            "id": "resp_high_risk",
            "conversation_id": conversation_id or "conv_test",
            "output_text": "",
            "tool_calls": [
                {
                    "id": "call_hr",
                    "name": "send_email",
                    "arguments": json.dumps({"to": ["ops@example.com"], "subject": "hi", "body": "x"}),
                }
            ],
        }


class HighRiskRegistry(ToolRegistryService):
    def __init__(self):
        super().__init__()
        self._tools["send_email"] = ToolSpec(
            name="send_email",
            level=3,
            description="Send an email.",
            input_schema={"type": "object", "properties": {"to": {"type": "array"}}},
            handler=lambda **_: {"status": "sent"},
        )


def test_orchestrator_executes_tools_and_returns_follow_up_text():
    orchestrator = AssistantOrchestrator(
        openai_client=FakeOpenAIClient(),
        tool_registry=ToolRegistryService(),
        approval_service=ApprovalService(),
        tool_call_service=ToolCallService(),
    )

    result = orchestrator.handle_message("conv_test", "What is after-hours support policy?")

    assert result.response_id == "resp_final"
    assert result.conversation_id == "conv_test"
    assert result.requires_approval is False
    assert "search_knowledge_base" in result.used_tools
    assert "on-call" in result.reply


def test_orchestrator_blocks_high_risk_tools_before_execution():
    orchestrator = AssistantOrchestrator(
        openai_client=FakeApprovalOpenAIClient(),
        tool_registry=HighRiskRegistry(),
        approval_service=ApprovalService(),
        tool_call_service=ToolCallService(),
    )

    result = orchestrator.handle_message("conv_test", "Send an email update")

    assert result.requires_approval is True
    assert result.approval_id is None
    assert result.used_tools == []
