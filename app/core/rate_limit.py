"""
Rate Limiting Configuration Module

This module provides rate limiting configuration for the FastAPI application
using slowapi for controlling request rates per client IP.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Any

# Create a limiter instance with default configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    strategy="fixed-window",  # Alternative: "moving-window"
)


def get_limiter() -> Any:
    """
    Get the configured rate limiter instance.

    Returns:
        Limiter: The configured rate limiter instance
    """
    return limiter
