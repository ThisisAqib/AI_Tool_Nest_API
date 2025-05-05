"""
Documentation Routes Module

This module handles the documentation web routes for rendering the API documentation pages.
It is separate from the API endpoints to maintain a clear separation between API and web interfaces.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core.templates import templates

router = APIRouter(
    prefix="", tags=["documentation"], default_response_class=HTMLResponse
)


@router.get("/", name="documentation_home")
async def docs_home(request: Request) -> HTMLResponse:
    """
    Render the API documentation homepage.

    This route serves the single-page documentation that includes all API examples,
    authentication flows, and usage instructions.

    Args:
        request (Request): The incoming request object

    Returns:
        HTMLResponse: The rendered documentation page
    """
    return templates.TemplateResponse(
        "pages/home.html", {"request": request, "project_name": "AI Tool Nest API"}
    )
