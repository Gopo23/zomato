"""
Groq LLM integration service.

Constructs prompts, calls the Groq API, and parses
structured JSON recommendations.

Implementation: Phase 3
"""

import json
import logging
import asyncio
from typing import Any, Dict, List

from groq import AsyncGroq
from groq import APIError

from models.schemas import Recommendation

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, settings):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    async def get_recommendations(self, prompt: str) -> List[Recommendation]:
        """Calls Groq, parses JSON, and retries on failure."""
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Calling Groq LLM (attempt {attempt + 1}/{max_retries + 1})...")
                response = await self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"},
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from LLM")
                    
                parsed_json = json.loads(content)
                
                # Handle case where LLM wraps the array in a dict (e.g. {"recommendations": [...]})
                # even though we asked for a JSON array, because JSON mode often requires an object root
                if isinstance(parsed_json, dict):
                    # Find the first array value
                    for key, value in parsed_json.items():
                        if isinstance(value, list):
                            parsed_json = value
                            break
                    else:
                        # if no array found, fallback to wrapping it in list if it looks like a single item
                        if "rank" in parsed_json:
                            parsed_json = [parsed_json]
                        else:
                            raise ValueError("Could not find a list of recommendations in the JSON response")

                if not isinstance(parsed_json, list):
                    raise ValueError(f"Expected a JSON array, got {type(parsed_json)}")
                
                # Validate with Pydantic
                recommendations = [Recommendation(**item) for item in parsed_json]
                return recommendations

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parsing/validation error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    logger.error("Max retries reached for LLM parsing.")
                    return [] # Graceful fallback
            except APIError as e:
                logger.warning(f"Groq API error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    logger.error("Max retries reached for LLM API.")
                    return []
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.exception(f"Unexpected error calling LLM: {e}")
                return []
        
        return []

    async def check_connection(self) -> bool:
        """Verify the API key and connectivity."""
        try:
            # Send a tiny request just to check auth
            await self.client.chat.completions.create(
                messages=[{"role": "user", "content": "hello"}],
                model=self.model,
                max_tokens=5,
            )
            return True
        except Exception as e:
            logger.error(f"LLM connection check failed: {e}")
            return False
