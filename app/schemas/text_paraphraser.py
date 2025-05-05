"""
Text Paraphraser Schema Models

This module defines the Pydantic models for text paraphrasing requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field, constr
from app.services.text_paraphraser import (
    ParaphraseStyle,
    ParaphraseIntensity,
    LengthOption,
)


class ParaphraseRequest(BaseModel):
    text: constr(min_length=10) = Field(..., description="The text to paraphrase")
    style: ParaphraseStyle = Field(
        default=ParaphraseStyle.CASUAL, description="The paraphrasing style"
    )
    intensity: ParaphraseIntensity = Field(
        default=ParaphraseIntensity.MEDIUM, description="The paraphrasing intensity"
    )
    length_option: LengthOption = Field(
        default=LengthOption.SAME, description="The desired output length"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The quick brown fox jumps over the lazy dog.",
                "style": "formal",
                "intensity": "medium",
                "length_option": "same",
            }
        }


class ParaphraseResponse(BaseModel):
    paraphrased_text: str = Field(..., description="The paraphrased text")

    class Config:
        json_schema_extra = {
            "example": {
                "paraphrased_text": "The swift brown fox leaps across the indolent canine."
            }
        }
