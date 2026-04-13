# Tool Contracts

This document specifies the inputs and outputs for each tool exposed to the assistant. Tools encapsulate external side effects or retrieval operations and must adhere to strict schemas. The model uses OpenAI function calling to request tool invocations.

## Tool Levels

Tools are categorised into three levels based on their potential side effects:

1. **Read‑only Tools (Level 1)** – safe to execute immediately. Examples: retrieving calendar events, searching documents, listing tasks.
2. **Drafting Tools (Level 2)** – produce drafts or summaries that are not directly executed. Examples: drafting an email or meeting agenda.
3. **Side‑effect Tools (Level 3)** – modify external state (send an email, schedule a meeting, delete a file). These require user approval before execution.

## Example Tool Definitions

### `get_daily_schedule` (Level 1)

**Description**: Retrieves the user’s calendar events for a specific date.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "date": { "type": "string", "format": "date", "description": "The date for which to fetch events (YYYY‑MM‑DD)." },
    "timezone": { "type": "string", "description": "IANA timezone identifier." }
  },
  "required": ["date", "timezone"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": { "type": "string" },
          "start": { "type": "string", "format": "date‑time" },
          "end": { "type": "string", "format": "date‑time" },
          "location": { "type": "string", "nullable": true }
        },
        "required": ["title", "start", "end"]
      }
    }
  },
  "required": ["events"]
}
```

### `search_knowledge_base` (Level 1)

**Description**: Searches the knowledge base for documents matching a query and returns top relevant snippets.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": { "type": "string", "description": "Semantic search query." },
    "scope": { "type": "string", "description": "Search scope: evergreen, operational, project." },
    "top_k": { "type": "integer", "minimum": 1, "maximum": 10, "default": 5 }
  },
  "required": ["query"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "document_id": { "type": "string" },
          "snippet": { "type": "string" },
          "metadata": { "type": "object" }
        },
        "required": ["document_id", "snippet"]
      }
    }
  },
  "required": ["results"]
}
```

### `draft_email` (Level 2)

**Description**: Generates a draft email given recipients, subject and body guidelines.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "to": { "type": "array", "items": { "type": "string", "format": "email" } },
    "cc": { "type": "array", "items": { "type": "string", "format": "email" }, "nullable": true },
    "bcc": { "type": "array", "items": { "type": "string", "format": "email" }, "nullable": true },
    "subject": { "type": "string" },
    "body": { "type": "string" }
  },
  "required": ["to", "subject", "body"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "draft": { "type": "string", "description": "Plain‑text body of the drafted email." }
  },
  "required": ["draft"]
}
```

### `send_email` (Level 3)

**Description**: Sends an email message. This tool requires approval before execution.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "to": { "type": "array", "items": { "type": "string", "format": "email" } },
    "cc": { "type": "array", "items": { "type": "string", "format": "email" }, "nullable": true },
    "bcc": { "type": "array", "items": { "type": "string", "format": "email" }, "nullable": true },
    "subject": { "type": "string" },
    "body": { "type": "string" },
    "reply_to_message_id": { "type": "string", "nullable": true }
  },
  "required": ["to", "subject", "body"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["pending", "sent", "failed"] },
    "message_id": { "type": "string", "nullable": true },
    "error": { "type": "string", "nullable": true }
  },
  "required": ["status"]
}
```

## Implementation Notes

- Each tool should validate its input using Pydantic or JSON Schema before execution.
- Level 3 tools should never execute immediately. They must create a pending approval record and wait until the user explicitly approves the action.
- The agent orchestrator should map tool call results back into the model’s conversation to continue reasoning.
- All tool executions, including failures, should be recorded in the audit log with timestamps and user IDs.