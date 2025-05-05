"""
Image to Text Service

This module provides image analysis functionality using Groq's Vision API.
"""

import base64
import json
import io
from enum import Enum
from typing import Optional, Union, BinaryIO
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings


class ImageAnalysisMode(str, Enum):
    DESCRIPTION = "description"
    OCR = "ocr"
    DETAILED = "detailed"


class DetailLevel(str, Enum):
    BRIEF = "brief"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class ImageToTextException(Exception):
    """Base exception for image to text service"""

    pass


class ImageToTextService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.GROK_API_KEY, base_url=settings.OPENAI_BASE_URL
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def _create_prompt(self, mode: ImageAnalysisMode, detail_level: DetailLevel) -> str:
        """Create the appropriate prompt based on mode and detail level."""

        base_prompts = {
            ImageAnalysisMode.DESCRIPTION: "Describe what you see in this image.",
            ImageAnalysisMode.OCR: "Extract all text visible in this image.",
            ImageAnalysisMode.DETAILED: "Analyze this image in detail.",
        }

        detail_modifiers = {
            DetailLevel.BRIEF: "Keep it brief and concise.",
            DetailLevel.STANDARD: "Provide a standard level of detail.",
            DetailLevel.COMPREHENSIVE: "Provide comprehensive details about everything you can identify.",
        }

        # Special instructions for OCR mode
        if mode == ImageAnalysisMode.OCR:
            ocr_specifics = {
                DetailLevel.BRIEF: "Extract only the main text, ignoring minor details.",
                DetailLevel.STANDARD: "Extract all readable text, maintaining basic structure.",
                DetailLevel.COMPREHENSIVE: "Extract all text with precise layout information, including positions and formatting.",
            }
            return f"{base_prompts[mode]} {ocr_specifics[detail_level]}"

        return f"{base_prompts[mode]} {detail_modifiers[detail_level]}"

    async def _encode_image(self, image_file: BinaryIO) -> str:
        """Encode image file to base64."""
        try:
            # Ensure we're at the beginning of the file
            image_file.seek(0)

            # Read the entire file content
            # No await here - regular synchronous read for standard file objects
            image_data = image_file.read()

            if not image_data:
                raise ImageToTextException("Empty image file received")

            # Encode to base64
            return base64.b64encode(image_data).decode("utf-8")
        except Exception as e:
            raise ImageToTextException(f"Failed to encode image: {str(e)}")

    async def analyze_image(
        self,
        image_source: Union[str, BinaryIO],
        mode: ImageAnalysisMode = ImageAnalysisMode.DESCRIPTION,
        detail_level: DetailLevel = DetailLevel.STANDARD,
        is_url: bool = False,
    ) -> dict:
        """
        Analyze an image using the specified mode and detail level.

        Args:
            image_source: Either an image URL (str) or a file-like object containing image data
            mode: The analysis mode (description, ocr, or detailed)
            detail_level: The level of detail in the response
            is_url: Whether the image_source is a URL or a file

        Returns:
            dict: Contains 'analysis' with the result

        Raises:
            ImageToTextException: If there's an error during analysis
        """
        try:
            prompt = self._create_prompt(mode, detail_level)

            # Prepare the image content based on source type
            if is_url:
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": image_source},
                }
            else:
                # Handle file case safely
                try:
                    # Encode file to base64
                    base64_image = await self._encode_image(image_source)
                    image_content = {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }
                except Exception as e:
                    raise ImageToTextException(
                        f"Failed to process image file: {str(e)}"
                    )

            # Create the API request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}, image_content],
                    }
                ],
                temperature=0.2,  # Lower temperature for more consistent results
            )

            analysis_text = response.choices[0].message.content

            # Format response based on mode
            if (
                mode == ImageAnalysisMode.OCR
                and detail_level == DetailLevel.COMPREHENSIVE
            ):
                # Attempt to structure OCR results
                try:
                    # Create a more structured response for OCR when possible
                    lines = analysis_text.strip().split("\n")
                    return {
                        "analysis": analysis_text,
                        "structured_text": {"lines": lines, "line_count": len(lines)},
                    }
                except Exception:
                    # If structuring fails, return plain text
                    return {"analysis": analysis_text}
            else:
                return {"analysis": analysis_text}

        except ImageToTextException as e:
            # Re-raise specific exceptions
            raise
        except Exception as e:
            raise ImageToTextException(f"Image analysis failed: {str(e)}")


# Create a singleton instance
image_analyzer = ImageToTextService()
