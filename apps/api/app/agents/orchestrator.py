import json

from sqlalchemy.orm import Session

from app.schemas.chat import ChatSendResponse
from app.services.approval_service import ApprovalService
from app.services.openai_client import OpenAIClientService
from app.services.tool_call_service import ToolCallService
from app.services.tool_registry import ToolRegistryService


class AssistantOrchestrator:
    """Coordinates chat turns, model responses, tool execution, and approvals."""

    def __init__(
        self,
        openai_client: OpenAIClientService,
        tool_registry: ToolRegistryService,
        approval_service: ApprovalService,
        tool_call_service: ToolCallService,
    ) -> None:
        self.openai_client = openai_client
        self.tool_registry = tool_registry
        self.approval_service = approval_service
        self.tool_call_service = tool_call_service

    def handle_message(
        self,
        conversation_id: str | None,
        message: str,
        *,
        session: Session | None = None,
    ) -> ChatSendResponse:
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

        normalized_calls: list[tuple[dict, dict, int]] = []
        for call in tool_calls:
            tool_name = call.get("name")
            if not tool_name:
                continue
            spec = self.tool_registry.get(tool_name)
            try:
                args = json.loads(call.get("arguments") or "{}")
            except json.JSONDecodeError:
                return ChatSendResponse(
                    conversation_id=model_response["conversation_id"],
                    response_id=model_response["id"],
                    reply=f"Tool '{tool_name}' returned invalid arguments JSON.",
                    used_tools=used_tools,
                    requires_approval=False,
                )
            normalized_calls.append((call, args, spec.level))

        high_risk = [entry for entry in normalized_calls if entry[2] >= 3]
        if high_risk:
            approval_id: str | None = None
            if session is not None:
                first_call, first_args, _ = high_risk[0]
                tool_call_row = self.tool_call_service.create_requested(
                    session,
                    conversation_id=model_response["conversation_id"],
                    tool_name=first_call["name"],
                    arguments=first_args,
                    requires_approval=True,
                )
                pending = self.approval_service.create_pending(
                    session,
                    tool_name=first_call["name"],
                    payload={
                        "tool_call_id": tool_call_row.id,
                        "tool_call": first_call,
                        "arguments": first_args,
                    },
                )
                approval_id = pending.id

            return ChatSendResponse(
                conversation_id=model_response["conversation_id"],
                response_id=model_response["id"],
                reply="One or more requested actions require approval before execution.",
                used_tools=used_tools,
                requires_approval=True,
                approval_id=approval_id,
            )

        tool_outputs: list[dict] = []
        for call, args, _ in normalized_calls:
            tool_name = call["name"]
            tool_call_id: str | None = None
            if session is not None:
                tool_call = self.tool_call_service.create_requested(
                    session,
                    conversation_id=model_response["conversation_id"],
                    tool_name=tool_name,
                    arguments=args,
                    requires_approval=False,
                )
                tool_call_id = tool_call.id

            try:
                result = self.tool_registry.execute(tool_name, **args)
            except Exception as exc:
                if session is not None and tool_call_id is not None:
                    self.tool_call_service.mark_failed(session, tool_call_id, str(exc))
                raise

            if session is not None and tool_call_id is not None:
                self.tool_call_service.mark_completed(session, tool_call_id, result)

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
