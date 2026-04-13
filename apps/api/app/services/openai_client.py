"""OpenAI Responses API wrapper with local fallback mode."""

from __future__ import annotations

from uuid import uuid4

import requests


class OpenAIClientService:
    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4.1-mini") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def is_stub_mode(self) -> bool:
        return not self.api_key or self.api_key == "your-openai-api-key"

    def create_response(
        self,
        message: str,
        conversation_id: str | None = None,
        tools: list[dict] | None = None,
    ) -> dict:
        if self.is_stub_mode:
            return self._stub_response(message, conversation_id)

        payload: dict = {
            "model": self.model,
            "input": message,
        }
        if conversation_id:
            payload["conversation"] = conversation_id
        if tools:
            payload["tools"] = tools

        return self._post_response(payload, conversation_id)

    def create_response_with_tool_outputs(
        self,
        *,
        previous_response_id: str,
        tool_outputs: list[dict],
        conversation_id: str | None,
    ) -> dict:
        if self.is_stub_mode:
            return {
                "id": f"resp_{uuid4()}",
                "conversation_id": conversation_id or f"conv_{uuid4()}",
                "output_text": "[local-stub] Tool outputs accepted.",
                "tool_calls": [],
            }

        payload: dict = {
            "model": self.model,
            "previous_response_id": previous_response_id,
            "input": tool_outputs,
        }
        if conversation_id:
            payload["conversation"] = conversation_id
        return self._post_response(payload, conversation_id)

    def _post_response(self, payload: dict, conversation_id: str | None) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/responses",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            body = response.json()
        except requests.RequestException as exc:
            return {
                "id": f"resp_{uuid4()}",
                "conversation_id": conversation_id or f"conv_{uuid4()}",
                "output_text": f"[model-error] OpenAI request failed: {exc}",
                "tool_calls": [],
            }

        output_text = body.get("output_text") or self._extract_output_text(body)
        resolved_conversation_id = conversation_id or body.get("conversation") or f"conv_{uuid4()}"
        return {
            "id": body.get("id", f"resp_{uuid4()}"),
            "conversation_id": resolved_conversation_id,
            "output_text": output_text,
            "tool_calls": self._extract_tool_calls(body),
        }

    def _stub_response(self, message: str, conversation_id: str | None = None) -> dict:
        response_id = f"resp_{uuid4()}"
        return {
            "id": response_id,
            "conversation_id": conversation_id or f"conv_{uuid4()}",
            "output_text": (
                "[local-stub] I can help draft, summarize, and retrieve policy "
                "answers once OpenAI credentials are configured. "
                f"Echo: {message}"
            ),
            "tool_calls": [],
        }

    @staticmethod
    def _extract_output_text(body: dict) -> str:
        chunks: list[str] = []
        for item in body.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    chunks.append(content["text"])
        return "\n".join(chunks).strip() or ""

    @staticmethod
    def _extract_tool_calls(body: dict) -> list[dict]:
        calls: list[dict] = []
        for item in body.get("output", []):
            if item.get("type") != "function_call":
                continue
            calls.append(
                {
                    "id": item.get("id") or item.get("call_id") or f"call_{uuid4()}",
                    "name": item.get("name"),
                    "arguments": item.get("arguments", "{}"),
                }
            )
        return calls
