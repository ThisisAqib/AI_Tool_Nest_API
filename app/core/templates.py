"""
Template Configuration Module

This module provides centralized template configuration and utilities
for the entire application. It initializes Jinja2 templates once and
provides template filters and global variables.
"""

from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from pathlib import Path
from app.core.config import settings, TEMPLATE_DIR


# Set up Jinja2 environment first
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)


def setup_template_filters(env: Environment):
    """
    Set up custom template filters for Jinja2.
    These filters will be available in all templates.

    Args:
        env (Environment): The Jinja2 environment
    """

    def format_date(date: datetime, format: str = "%Y-%m-%d") -> str:
        """Format a date using the specified format string."""
        return date.strftime(format)

    def truncate(text: str, length: int = 100) -> str:
        """Truncate text to the specified length."""
        return text[:length] + "..." if len(text) > length else text

    # Register filters
    env.filters["format_date"] = format_date
    env.filters["truncate"] = truncate


def setup_template_globals(env: Environment):
    """
    Set up global variables available in all templates.

    Args:
        env (Environment): The Jinja2 environment
    """
    env.globals.update(
        {
            "project_name": settings.PROJECT_NAME,
            "current_year": datetime.now().year,
            "version": settings.VERSION,
            "base_url": settings.BASE_URL,
        }
    )


def init_templates():
    """
    Initialize template configuration.
    This should be called once when the application starts.
    """
    # Set up filters and globals
    setup_template_filters(env)
    setup_template_globals(env)

    # Create FastAPI templates with our configured environment
    templates = Jinja2Templates(env=env)

    return templates


# Initialize templates and export
templates = init_templates()
