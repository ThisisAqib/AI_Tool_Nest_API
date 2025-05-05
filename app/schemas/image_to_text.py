"""
Image to Text Schema Models

This module defines the Pydantic models for image to text requests and responses.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, HttpUrl
from app.services.image_to_text import ImageAnalysisMode, DetailLevel


class ImageUrlRequest(BaseModel):
    """Request model for image analysis using a URL."""

    image_url: HttpUrl = Field(..., description="URL of the image to analyze")
    mode: Optional[ImageAnalysisMode] = Field(
        default=ImageAnalysisMode.DESCRIPTION, description="Analysis mode"
    )
    detail_level: Optional[DetailLevel] = Field(
        default=DetailLevel.STANDARD, description="Level of detail in analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg",
                "mode": "description",
                "detail_level": "standard",
            }
        }


class ImageToTextResponse(BaseModel):
    """Response model for image analysis results."""

    analysis: str = Field(..., description="Analysis of the image content")
    structured_text: Optional[Dict] = Field(
        None, description="Structured text data for OCR mode"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "analysis": "The image shows a scenic landscape with mountains in the background and a lake in the foreground. The sky is blue with some clouds.",
                "structured_text": None,
            }
        }
