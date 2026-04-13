"""Service layer package.

Services encapsulate complex interactions with external APIs (OpenAI, Gmail,
calendar providers), manage knowledge bases, handle approvals and provide
reusable utility functions. Use dependency injection in FastAPI to provide
service instances to your routes and agent orchestrator.
"""