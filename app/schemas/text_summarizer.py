"""
Text Summarizer Schema Models

This module defines the Pydantic models for text summarization requests and responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, constr
from app.services.text_summarizer import SummaryMode


class SummarizeRequest(BaseModel):
    text: constr(min_length=100) = Field(..., description="The text to summarize")
    mode: SummaryMode = Field(
        default=SummaryMode.PARAGRAPH, description="The summarization mode"
    )
    max_length: Optional[int] = Field(
        None, ge=20, le=1000, description="Maximum length for paragraph mode"
    )
    custom_instructions: Optional[str] = Field(
        None, description="Custom instructions for custom mode"
    )
    extract_keywords: bool = Field(
        default=False, description="Whether to extract key terms from the text"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Your long text to summarize goes here...",
                "mode": "paragraph",
                "max_length": 150,
                "extract_keywords": True,
            }
        }


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="The generated summary")
    keywords: Optional[List[str]] = Field(
        None, description="Extracted key terms from the text"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "A concise summary of the input text...",
                "keywords": ["key term 1", "key term 2", "key term 3"],
            }
        }
