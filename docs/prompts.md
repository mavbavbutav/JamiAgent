# Prompt Layers and Policies

This document describes how prompts are structured in the assistant and outlines guidance for maintaining prompt stability, caching and retrieval policies.

## Prompt Layers

Prompts are constructed from several stable layers. Keeping these layers consistent ensures that OpenAI’s prompt caching can reuse compiled prefixes and reduce latency and cost.

1. **System Prompt (Identity and Policy)** – defines the assistant’s identity (e.g. “You are John’s professional operations assistant”) and the non‑negotiable rules: be accurate, cite sources, never send emails without approval, etc. This should rarely change.
2. **Domain Policy** – contextual instructions for a specific domain such as email drafting, meeting preparation or knowledge retrieval. For example, when drafting emails the assistant should be concise, preserve names, dates and commitments exactly and adopt a warm yet professional tone.
3. **Tool Descriptions** – a description of available tools and when they should be invoked. Each tool is defined by its name, description, input schema and output schema. This layer should be stable whenever possible to benefit from caching.
4. **Workspace/Profile Context** – the user’s preferences (tone, timezone, summary style) and workspace‑specific settings (project names, team members). This layer changes infrequently.
5. **Conversation Context** – recent messages and important summary notes to maintain continuity. The conversation state is stored via the OpenAI Conversations API and is compacted to control context length.
6. **User Input** – the current user message that triggered the request.

## Prompt Caching

OpenAI’s prompt caching improves performance when the initial part of the prompt is identical across requests. To leverage this:

- Keep layers 1–3 identical across requests whenever possible. Do not include dynamic data (timestamps, random IDs) in these layers.
- Only insert dynamic variables (timezone, user name, conversation state) after the stable prefix.
- Use the same model version (e.g. gpt‑5.4) across calls to maximise reuse.

## Retrieval and Citation

When answering questions that rely on internal documents, the assistant must:

1. Use the `search_knowledge_base` tool to retrieve relevant excerpts.
2. Include citations in the response using footnote‑style markers (e.g. [1], [2]) that map to document sources.
3. Distinguish between facts directly supported by the sources and inferences or recommendations.
4. Decline to answer or ask clarifying questions if the retrieved material does not support a confident answer.

## Safety and Approval

The assistant should adhere strictly to safety guidelines:

- Never fabricate citations or claim that information came from a source when it did not.
- Never take direct side‑effect actions (sending emails, booking appointments, deleting data) without an explicit user request and, for level‑3 tools, an approval token from the user.
- Respect user preferences and privacy by not storing personal data in prompts unnecessarily.

Additional safety measures include moderating user inputs and model outputs using OpenAI’s Moderation API and sanitising retrieved data before including it in prompts to prevent prompt injection.