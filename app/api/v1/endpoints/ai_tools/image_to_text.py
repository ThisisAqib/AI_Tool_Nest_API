"""
Image-to-Text API Routes

This module provides the API endpoints for converting images to text descriptions using AI.
"""

from time import time
import asyncio
import os
import tempfile
from fastapi import APIRouter, HTTPException, Request, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.services.image_to_text import (
    image_analyzer,
    ImageToTextException,
    ImageAnalysisMode,
    DetailLevel,
)
from app.schemas.image_to_text import ImageToTextResponse, ImageUrlRequest
from app.core.rate_limit import limiter
from app.core.database import get_session
from app.api.v1.endpoints.ai_tools.utils import (
    get_current_user_by_api_key,
    log_api_usage,
)

image_to_text_router = APIRouter()

# Maximum file size (4MB)
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB in bytes

# Allowed MIME types
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]


@image_to_text_router.post("/image-to-text", response_model=ImageToTextResponse)
@limiter.limit("5/minute")
async def image_to_text(
    request: Request,
    image_url: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    mode: Optional[str] = Form("description"),
    detail_level: Optional[str] = Form("standard"),
    auth_data: tuple = Depends(get_current_user_by_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    Convert an image to text description using AI.
    Accepts either an image URL or an uploaded image file.
    Rate limited to 5 requests per minute per IP address.
    Requires API key authentication via X-API-Key header.

    - **image_url**: URL of the image to analyze (optional if image_file is provided)
    - **image_file**: Uploaded image file (optional if image_url is provided)
    - **mode**: Processing mode (description, ocr, detailed)
    - **detail_level**: Level of detail in the output (brief, standard, comprehensive)
    """
    current_user, api_key_id = auth_data
    start_time = time()
    status_code = 200
    temp_file_path = None

    # Check for JSON content type and handle it
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        try:
            image_url = body.get("image_url")
            if not image_url:
                status_code = 422
                raise HTTPException(
                    status_code=422,
                    detail="JSON request must include 'image_url' field",
                )

            # Get mode and detail_level from JSON or use defaults
            mode_str = body.get("mode", "description")
            detail_level_str = body.get("detail_level", "standard")

            # Convert strings to enums
            mode_enum = ImageAnalysisMode(mode_str)
            detail_level_enum = DetailLevel(detail_level_str)

            image_file = None
        except ValueError as e:
            status_code = 422
            raise HTTPException(
                status_code=422, detail=f"Invalid mode or detail_level: {str(e)}"
            )
    else:
        # Convert string parameters to enums
        try:
            mode_enum = ImageAnalysisMode(mode)
            detail_level_enum = DetailLevel(detail_level)
        except ValueError as e:
            status_code = 422
            raise HTTPException(
                status_code=422, detail=f"Invalid mode or detail_level: {str(e)}"
            )

    # Validate that exactly one image source is provided
    if (image_url is None and image_file is None) or (
        image_url is not None and image_file is not None
    ):
        status_code = 400
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Exactly one of image_url or image_file must be provided."
            },
        )

    try:
        # Process based on the provided image source
        if image_url:
            result = await image_analyzer.analyze_image(
                image_source=image_url,
                mode=mode_enum,
                detail_level=detail_level_enum,
                is_url=True,
            )
        else:  # image_file is provided
            # Validate file content type
            if image_file.content_type not in ALLOWED_MIME_TYPES:
                status_code = 415
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {image_file.content_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
                )

            # Save uploaded file to a temporary file
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".jpg"
                ) as temp_file:
                    temp_file_path = temp_file.name
                    # Write the uploaded file content to the temporary file
                    content = await image_file.read()
                    if len(content) > MAX_FILE_SIZE:
                        status_code = 413
                        raise HTTPException(
                            status_code=413,
                            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.1f}MB",
                        )
                    temp_file.write(content)

                # Open the temporary file and analyze it
                with open(temp_file_path, "rb") as image_file_obj:
                    result = await image_analyzer.analyze_image(
                        image_source=image_file_obj,
                        mode=mode_enum,
                        detail_level=detail_level_enum,
                        is_url=False,
                    )

            finally:
                # Clean up the temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        response = ImageToTextResponse(**result)

    except ImageToTextException as e:
        status_code = 422
        raise HTTPException(status_code=422, detail=str(e))
    except asyncio.TimeoutError:
        status_code = 504
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        status_code = 500
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Log API key usage
        response_time = time() - start_time
        await log_api_usage(
            api_key_id=api_key_id,
            endpoint="/image-to-text",
            method="POST",
            status_code=status_code,
            response_time=response_time,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            session=session,
        )

    return response
