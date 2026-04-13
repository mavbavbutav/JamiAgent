import json

from app.schemas.chat import ChatSendResponse
from app.services.approval_service import ApprovalService
from app.services.openai_client import OpenAIClientService
from app.services.tool_registry import ToolRegistryService


class AssistantOrchestrator:
    """Coordinates chat turns, model responses, tool execution, and approvals."""

    def __init__(
        self,
        openai_client: OpenAIClientService,
        tool_registry: ToolRegistryService,
        approval_service: ApprovalService,
    ) -> None:
        self.openai_client = openai_client
        self.tool_registry = tool_registry
        self.approval_service = approval_service

    def handle_message(self, conversation_id: str | None, message: str) -> ChatSendResponse:
        used_tools: list[str] = []

        model_response = self.openai_client.create_response(
            message,
            conversation_id,
            tools=self.tool_registry.openai_tool_definitions(),
        )

        tool_calls = model_response.get("tool_calls", [])
        if not tool_calls:
            return ChatSendResponse(
                conversation_id=model_response["conversation_id"],
                response_id=model_response["id"],
                reply=model_response["output_text"] or "",
                used_tools=used_tools,
                requires_approval=False,
            )

        tool_outputs: list[dict] = []
        for call in tool_calls:
            tool_name = call.get("name")
            if not tool_name:
                continue
            spec = self.tool_registry.get(tool_name)
            args = json.loads(call.get("arguments") or "{}")

            if spec.level >= 3:
                return ChatSendResponse(
                    conversation_id=model_response["conversation_id"],
                    response_id=model_response["id"],
                    reply=f"Action '{tool_name}' requires approval.",
                    used_tools=used_tools,
                    requires_approval=True,
                )

            result = self.tool_registry.execute(tool_name, **args)
            used_tools.append(tool_name)
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call["id"],
                    "output": json.dumps(result),
                }
            )

        follow_up = self.openai_client.create_response_with_tool_outputs(
            previous_response_id=model_response["id"],
            tool_outputs=tool_outputs,
            conversation_id=model_response["conversation_id"],
        )

        return ChatSendResponse(
            conversation_id=follow_up["conversation_id"],
            response_id=follow_up["id"],
            reply=follow_up.get("output_text") or model_response.get("output_text") or "",
            used_tools=used_tools,
            requires_approval=False,
        )
