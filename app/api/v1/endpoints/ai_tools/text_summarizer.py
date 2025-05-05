"""
Text Summarizer API Routes

This module provides the API endpoints for text summarization functionality.
"""

from time import time
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.text_summarizer import summarizer, TextSummarizerException
from app.schemas.text_summarizer import SummarizeRequest, SummarizeResponse
from app.core.rate_limit import limiter
from app.core.database import get_session
from app.api.v1.endpoints.ai_tools.utils import (
    get_current_user_by_api_key,
    log_api_usage,
)

summarizer_router = APIRouter()


@summarizer_router.post("/summarize", response_model=SummarizeResponse, status_code=200)
@limiter.limit(
    "5/minute"
)  # More conservative limit for resource-intensive summarization
async def summarize_text(
    request: Request,
    body: SummarizeRequest,
    auth_data: tuple = Depends(get_current_user_by_api_key),
    session: AsyncSession = Depends(get_session),
) -> SummarizeResponse:
    """
    Summarize text using the specified mode and parameters.
    Rate limited to 5 requests per minute per IP address.
    Requires API key authentication via X-API-Key header.

    - **text**: The text to summarize
    - **mode**: Summarization mode (paragraph, bullet_points, or custom)
    - **max_length**: Optional maximum length for paragraph mode
    - **custom_instructions**: Optional custom instructions for custom mode
    - **extract_keywords**: Whether to extract key terms from the text
    """
    current_user, api_key_id = auth_data
    start_time = time()
    status_code = 200

    try:
        result = await summarizer.summarize(
            text=body.text,
            mode=body.mode,
            max_length=body.max_length,
            custom_instructions=body.custom_instructions,
            extract_keywords=body.extract_keywords,
        )
        response = SummarizeResponse(**result)

    except TextSummarizerException as e:
        status_code = 422
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        status_code = 500
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Log API key usage
        response_time = time() - start_time
        await log_api_usage(
            api_key_id=api_key_id,
            endpoint="/summarize",
            method="POST",
            status_code=status_code,
            response_time=response_time,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            session=session,
        )

    return response
