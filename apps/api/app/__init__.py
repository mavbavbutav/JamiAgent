"""Main package for the professional assistant API.

This package exposes the FastAPI application and organizes the modules for
the agent orchestrator, tool wrappers, route handlers, models and services.

The actual implementation of the agent logic, tool integrations and
knowledge retrieval should be added in the respective subpackages.
"""

from .main import app  # noqa: F401