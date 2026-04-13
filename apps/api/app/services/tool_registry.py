from dataclasses import dataclass
from typing import Any, Callable

from app.tools.core import draft_email, get_daily_schedule, search_knowledge_base


@dataclass(frozen=True)
class ToolSpec:
    name: str
    level: int
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., dict]


class ToolRegistryService:
    """Registers tools and exposes OpenAI-compatible tool definitions."""

    def __init__(self) -> None:
        self._tools = {
            "get_daily_schedule": ToolSpec(
                name="get_daily_schedule",
                level=1,
                description="Retrieve the user's schedule for a specific date and timezone.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "ISO date, e.g. 2026-04-13"},
                        "timezone": {"type": "string", "description": "IANA timezone"},
                    },
                    "required": ["date", "timezone"],
                },
                handler=get_daily_schedule,
            ),
            "search_knowledge_base": ToolSpec(
                name="search_knowledge_base",
                level=1,
                description="Search knowledge base documents and return top matching snippets.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "scope": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 10},
                    },
                    "required": ["query"],
                },
                handler=search_knowledge_base,
            ),
            "draft_email": ToolSpec(
                name="draft_email",
                level=2,
                description="Draft an email from recipients, subject, and body.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "array", "items": {"type": "string"}},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["to", "subject", "body"],
                },
                handler=draft_email,
            ),
        }

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name]

    def execute(self, name: str, **kwargs: Any) -> dict:
        tool = self.get(name)
        return tool.handler(**kwargs)

    def openai_tool_definitions(self) -> list[dict[str, Any]]:
        definitions: list[dict[str, Any]] = []
        for spec in self._tools.values():
            definitions.append(
                {
                    "type": "function",
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.input_schema,
                }
            )
        return definitions
