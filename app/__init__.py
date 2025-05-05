"""
AI Tool Nest - Application Package

This package contains the core application logic, including:
- API routes for JSON endpoints
- Web routes for HTML pages
- Business logic
- Configuration
"""

from fastapi import FastAPI
from app.api import api_router
from app.web import docs_router


def include_routers(app: FastAPI) -> None:
    """
    Include all application routers in the FastAPI application.

    This function sets up both API and web routes:
    - API routes (/v1/endpoints/*) for JSON endpoints
    - Web routes (/) for HTML documentation pages

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    # Include web routes first (for documentation)
    app.include_router(docs_router)

    # Include API routes
    app.include_router(api_router)
