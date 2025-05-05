"""
AI Tools API Endpoints

This module provides all AI-powered tool endpoints.
"""

from fastapi import APIRouter

# Create the AI tools router
ai_tools_router = APIRouter()

# Import all tool-specific routers
from app.api.v1.endpoints.ai_tools.text_summarizer import summarizer_router
from app.api.v1.endpoints.ai_tools.text_paraphraser import paraphraser_router
from app.api.v1.endpoints.ai_tools.image_to_text import image_to_text_router

# Include tool routers
ai_tools_router.include_router(summarizer_router)
ai_tools_router.include_router(paraphraser_router)
ai_tools_router.include_router(image_to_text_router)
