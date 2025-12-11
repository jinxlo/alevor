"""Research agent for market context."""

import logging
from typing import Dict, Any

from ..api_adapter import LLMAdapter

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Provides market research and context summaries."""
    
    def __init__(self, llm_adapter: LLMAdapter):
        """Initialize research agent.
        
        Args:
            llm_adapter: LLM adapter instance
        """
        self.llm = llm_adapter
    
    def research(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Research a market topic.
        
        Args:
            topic: Research topic
            context: Optional context data
        
        Returns:
            Research summary
        """
        prompt = f"""Provide a brief market research summary on: {topic}
        
        Focus on:
        - Current market conditions
        - Relevant trends
        - Potential impacts on trading
        
        Keep it concise and actionable.
        """
        
        try:
            summary = self.llm.generate(
                prompt,
                model="gpt-4",
                temperature=0.6,
                max_tokens=1500
            )
            return summary
        except Exception as e:
            logger.error(f"Error generating research: {e}")
            return f"Error generating research: {e}"

