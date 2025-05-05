"""
Text Paraphraser API Routes

This module provides the API endpoints for text paraphrasing functionality.
"""

from time import time
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.text_paraphraser import paraphraser, TextParaphraserException
from app.schemas.text_paraphraser import ParaphraseRequest, ParaphraseResponse
from app.core.rate_limit import limiter
from app.core.database import get_session
from app.api.v1.endpoints.ai_tools.utils import (
    get_current_user_by_api_key,
    log_api_usage,
)

paraphraser_router = APIRouter()


@paraphraser_router.post(
    "/paraphrase", response_model=ParaphraseResponse, status_code=200
)
@limiter.limit("5/minute")  # Same rate limit as summarizer
async def paraphrase_text(
    request: Request,
    body: ParaphraseRequest,
    auth_data: tuple = Depends(get_current_user_by_api_key),
    session: AsyncSession = Depends(get_session),
) -> ParaphraseResponse:
    """
    Paraphrase text using the specified style, intensity, and length options.
    Rate limited to 5 requests per minute per IP address.
    Requires API key authentication via X-API-Key header.

    - **text**: The text to paraphrase
    - **style**: Paraphrasing style (formal, casual, or simple)
    - **intensity**: Paraphrasing intensity (low, medium, or high)
    - **length_option**: Desired length of output (same, shorter, or longer)
    """
    current_user, api_key_id = auth_data
    start_time = time()
    status_code = 200

    try:
        result = await paraphraser.paraphrase(
            text=body.text,
            style=body.style,
            intensity=body.intensity,
            length_option=body.length_option,
        )
        response = ParaphraseResponse(**result)

    except TextParaphraserException as e:
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
            endpoint="/paraphrase",
            method="POST",
            status_code=status_code,
            response_time=response_time,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            session=session,
        )

    return response
