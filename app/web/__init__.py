"""
Web Routes Package

This package contains web-facing routes that serve HTML pages and documentation,
as opposed to API endpoints that serve JSON responses.
"""

from app.web.docs import router as docs_router

__all__ = ["docs_router"]
