"""
API v1 Endpoints

This module combines all v1 API endpoints into a single router.
"""

from fastapi import APIRouter, Request
from app.api.v1.endpoints.ai_tools.text_summarizer import summarizer_router
from app.api.v1.endpoints.ai_tools.text_paraphraser import paraphraser_router
from app.api.v1.endpoints.ai_tools.image_to_text import image_to_text_router
from app.core.rate_limit import limiter
from app.api.v1.endpoints import auth, api_keys

# Create the main endpoints router
endpoints_router = APIRouter()


@endpoints_router.get("/health", description="Health Check", tags=["health"])
@limiter.limit("5/minute")
async def health_check(request: Request):
    """
    Health check endpoint to verify API status.
    Rate limited to 5 requests per minute per IP address.
    """
    return {"status": "healthy"}


# Include all v1 endpoint routers
ai_tools_router = APIRouter()
ai_tools_router.include_router(summarizer_router)
ai_tools_router.include_router(paraphraser_router)
ai_tools_router.include_router(image_to_text_router)

endpoints_router.include_router(ai_tools_router, prefix="/ai-tools", tags=["ai-tools"])

# Include authentication endpoints
endpoints_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include API key management endpoints
endpoints_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
