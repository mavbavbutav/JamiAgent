import json

from app.agents.orchestrator import AssistantOrchestrator
from app.services.approval_service import ApprovalService
from app.services.tool_registry import ToolRegistryService


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


def test_orchestrator_executes_tools_and_returns_follow_up_text():
    orchestrator = AssistantOrchestrator(
        openai_client=FakeOpenAIClient(),
        tool_registry=ToolRegistryService(),
        approval_service=ApprovalService(),
    )

    result = orchestrator.handle_message("conv_test", "What is after-hours support policy?")

    assert result.response_id == "resp_final"
    assert result.conversation_id == "conv_test"
    assert result.requires_approval is False
    assert "search_knowledge_base" in result.used_tools
    assert "on-call" in result.reply
