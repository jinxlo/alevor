"""LLM API adapter for OpenAI and other providers."""

import logging
import os
from typing import Optional, Dict, Any
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMAdapter:
    """Adapter for LLM API calls."""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """Initialize LLM adapter.
        
        Args:
            provider: LLM provider ("openai", etc.)
            api_key: API key (default: from OPENAI_API_KEY env var)
        """
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key not provided")
        
        if provider == "openai":
            self.client = OpenAI(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate text using LLM.
        
        Args:
            prompt: Input prompt
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

