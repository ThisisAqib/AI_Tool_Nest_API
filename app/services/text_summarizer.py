"""
Text Summarization Service

This module provides text summarization functionality using an external API.
"""

import json
from enum import Enum
from typing import List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings


class SummaryMode(str, Enum):
    PARAGRAPH = "paragraph"
    BULLET_POINTS = "bullet_points"
    CUSTOM = "custom"


class TextSummarizerException(Exception):
    """Base exception for text summarizer service"""

    pass


class TextSummarizer:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.GROK_API_KEY, base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL_NAME

    def _create_prompt(
        self,
        text: str,
        mode: SummaryMode,
        max_length: Optional[int] = None,
        custom_instructions: Optional[str] = None,
        extract_keywords: bool = False,
    ) -> str:
        base_prompt = """You are a helpful assistant that summarizes text.

Your task:
1. Summarize the input text according to the specified mode and requirements.
2. Make sure to keep the summary accurate and to the point.
3. Make sure to keep the summary in the same language as the text."""

        mode_specific = {
            SummaryMode.PARAGRAPH: f"""
Format the summary as a coherent paragraph.
Maximum length: {max_length if max_length else 'Not specified'}""",
            SummaryMode.BULLET_POINTS: """
Format the summary as bullet points, with each point starting with "• " (bullet point followed by a space).
Each bullet point should:
- Start on a new line
- Capture a single key idea
- Be concise and clear
- Use "• " as the bullet point character

Example format:
• First key point here
• Second key point here
• Third key point here""",
            SummaryMode.CUSTOM: f"""
Follow these custom formatting instructions:
{custom_instructions if custom_instructions else ''}

Make sure to:
- Follow the exact instructions specified.
""",
        }

        keyword_extraction = (
            """
Additionally, extract 5-7 key terms or phrases that best represent the main concepts in the text."""
            if extract_keywords
            else ""
        )

        output_format = (
            """
**Output Requirements**:
Return ONLY valid JSON with the structure:
{
    "summary": "Your summary text here..."
"""
            + (
                """,
    "keywords": ["term1", "term2", "term3"]"""
                if extract_keywords
                else ""
            )
            + """
}"""
        )

        return f"{base_prompt}\n{mode_specific[mode]}\n{keyword_extraction}\n{output_format}"

    async def summarize(
        self,
        text: str,
        mode: SummaryMode,
        max_length: Optional[int] = None,
        custom_instructions: Optional[str] = None,
        extract_keywords: bool = False,
    ) -> dict:
        """
        Summarize the given text using the specified mode and parameters.

        Args:
            text: The text to summarize
            mode: The summarization mode (paragraph, bullet_points, or custom)
            max_length: Optional maximum length for paragraph mode
            custom_instructions: Optional custom instructions for custom mode
            extract_keywords: Whether to extract key terms from the text

        Returns:
            dict: Contains 'summary' and optionally 'keywords' if extract_keywords is True

        Raises:
            TextSummarizerException: If there's an error during summarization
        """
        try:
            prompt = self._create_prompt(
                text=text,
                mode=mode,
                max_length=max_length,
                custom_instructions=custom_instructions,
                extract_keywords=extract_keywords,
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
            )

            json_str = response.choices[0].message.content
            result = json.loads(json_str)

            # Validate response structure
            if "summary" not in result:
                raise TextSummarizerException(
                    "Invalid response: missing 'summary' field"
                )

            if extract_keywords and "keywords" not in result:
                raise TextSummarizerException(
                    "Invalid response: missing 'keywords' field"
                )

            return result

        except json.JSONDecodeError as e:
            raise TextSummarizerException("Failed to parse summarizer response")
        except Exception as e:
            raise TextSummarizerException(f"Summarization failed: {str(e)}")


# Create a singleton instance
summarizer = TextSummarizer()
