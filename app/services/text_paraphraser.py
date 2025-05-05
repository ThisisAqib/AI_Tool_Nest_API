"""
Text Paraphrasing Service

This module provides text paraphrasing functionality using an external API.
"""

import json
from enum import Enum
from typing import Optional
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings


class ParaphraseStyle(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    SIMPLE = "simple"


class ParaphraseIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LengthOption(str, Enum):
    SAME = "same"
    SHORTER = "shorter"
    LONGER = "longer"


class TextParaphraserException(Exception):
    """Base exception for text paraphraser service"""

    pass


class TextParaphraser:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.GROK_API_KEY, base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL_NAME

    def _create_prompt(
        self,
        text: str,
        style: ParaphraseStyle,
        intensity: ParaphraseIntensity,
        length_option: LengthOption,
    ) -> str:
        base_prompt = """You are a helpful assistant that paraphrases text.

Your task:
1. Paraphrase the input text according to the specified style, intensity, and length option.
2. Make sure to keep the core meaning of the text accurate.
3. Make sure to keep the paraphrase in the same language as the input text."""

        style_guidelines = {
            ParaphraseStyle.FORMAL: """
Style: Formal
Use more sophisticated vocabulary and formal language structures.
Avoid contractions, slang, and casual expressions.
Maintain a professional and academic tone.""",
            ParaphraseStyle.CASUAL: """
Style: Casual
Use everyday language and a conversational tone.
Feel free to use contractions and common expressions.
Make the text sound natural and approachable.""",
            ParaphraseStyle.SIMPLE: """
Style: Simple
Use clear, straightforward language.
Simplify complex concepts and vocabulary.
Prioritize readability and ease of understanding.""",
        }

        intensity_guidelines = {
            ParaphraseIntensity.LOW: """
Intensity: Low
Make minimal changes to the original text.
Maintain most of the original structure and many original words.
Focus on replacing only some words with synonyms.""",
            ParaphraseIntensity.MEDIUM: """
Intensity: Medium
Make moderate changes to the original text.
Restructure some sentences while preserving key phrases.
Replace most common words with appropriate alternatives.""",
            ParaphraseIntensity.HIGH: """
Intensity: High
Make significant changes to the original text.
Completely restructure sentences and paragraphs.
Use entirely different phrasing while maintaining the core meaning.""",
        }

        length_guidelines = {
            LengthOption.SAME: """
Length: Same
Keep the paraphrased text approximately the same length as the original.""",
            LengthOption.SHORTER: """
Length: Shorter
Make the paraphrased text more concise than the original.
Remove unnecessary details while preserving the main points.""",
            LengthOption.LONGER: """
Length: Longer
Expand on the ideas in the original text.
Add appropriate elaboration or examples to extend the content.""",
        }

        output_format = """
**Output Requirements**:
Return ONLY valid JSON with the structure:
{
    "paraphrased_text": "Your paraphrased text here..."
}"""

        return f"{base_prompt}\n{style_guidelines[style]}\n{intensity_guidelines[intensity]}\n{length_guidelines[length_option]}\n{output_format}"

    async def paraphrase(
        self,
        text: str,
        style: ParaphraseStyle,
        intensity: ParaphraseIntensity = ParaphraseIntensity.MEDIUM,
        length_option: LengthOption = LengthOption.SAME,
    ) -> dict:
        """
        Paraphrase the given text using the specified style, intensity, and length option.

        Args:
            text: The text to paraphrase
            style: The paraphrasing style (formal, casual, or simple)
            intensity: The paraphrasing intensity level (low, medium, or high)
            length_option: The desired length of the output (same, shorter, or longer)

        Returns:
            dict: Contains 'paraphrased_text' with the result

        Raises:
            TextParaphraserException: If there's an error during paraphrasing
        """
        try:
            prompt = self._create_prompt(
                text=text, style=style, intensity=intensity, length_option=length_option
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            json_str = response.choices[0].message.content
            result = json.loads(json_str)

            # Validate response structure
            if "paraphrased_text" not in result:
                raise TextParaphraserException(
                    "Invalid response: missing 'paraphrased_text' field"
                )

            return result

        except json.JSONDecodeError as e:
            raise TextParaphraserException("Failed to parse paraphraser response")
        except Exception as e:
            raise TextParaphraserException(f"Paraphrasing failed: {str(e)}")


# Create a singleton instance
paraphraser = TextParaphraser()
