"""Tool wrappers package.

Each module in this package should expose a function that implements
a particular tool (e.g. get_daily_schedule, search_knowledge_base,
draft_email). These functions should strictly validate inputs and
return outputs matching the JSON schemas defined in `docs/tool-contracts.md`.
"""