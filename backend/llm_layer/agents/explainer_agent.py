"""Explainer agent for user-friendly explanations."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..api_adapter import LLMAdapter

logger = logging.getLogger(__name__)


class ExplainerAgent:
    """Explains trading decisions in simple terms."""
    
    def __init__(self, llm_adapter: LLMAdapter, prompt_path: Optional[str] = None):
        """Initialize explainer agent.
        
        Args:
            llm_adapter: LLM adapter instance
            prompt_path: Path to prompt template
        """
        self.llm = llm_adapter
        self.prompt_template = self._load_prompt(prompt_path)
    
    def _load_prompt(self, prompt_path: Optional[str]) -> str:
        """Load prompt template."""
        if prompt_path is None:
            prompt_path = Path(__file__).parent.parent / "prompts" / "explainer_prompt.md"
        
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load prompt: {e}")
            return "Explain trading decisions in simple terms."
    
    def explain(
        self,
        context: Dict[str, Any],
        question: Optional[str] = None
    ) -> str:
        """Explain a trading decision or situation.
        
        Args:
            context: Context dictionary (trade, decision, etc.)
            question: Optional specific question
        
        Returns:
            Explanation text
        """
        prompt = f"""{self.prompt_template}

Context:
{self._format_dict(context)}

{"Question: " + question if question else "Provide an explanation."}
"""
        
        try:
            explanation = self.llm.generate(
                prompt,
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=1000
            )
            return explanation
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"Error generating explanation: {e}"
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary for prompt."""
        lines = []
        for key, value in data.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

