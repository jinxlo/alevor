"""Risk oversight agent."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..api_adapter import LLMAdapter

logger = logging.getLogger(__name__)


class RiskAgent:
    """Analyzes risk metrics and generates alerts."""
    
    def __init__(self, llm_adapter: LLMAdapter, prompt_path: Optional[str] = None):
        """Initialize risk agent.
        
        Args:
            llm_adapter: LLM adapter instance
            prompt_path: Path to prompt template
        """
        self.llm = llm_adapter
        self.prompt_template = self._load_prompt(prompt_path)
    
    def _load_prompt(self, prompt_path: Optional[str]) -> str:
        """Load prompt template."""
        if prompt_path is None:
            prompt_path = Path(__file__).parent.parent / "prompts" / "risk_prompt.md"
        
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load prompt: {e}")
            return "Analyze risk metrics and identify issues."
    
    def analyze_risk(
        self,
        risk_metrics: Dict[str, Any],
        recent_trades: list[Dict[str, Any]]
    ) -> str:
        """Analyze risk and generate report.
        
        Args:
            risk_metrics: Risk metrics dictionary
            recent_trades: Recent trades
        
        Returns:
            Risk analysis text
        """
        prompt = f"""{self.prompt_template}

Analyze the following risk data:

Risk Metrics:
{self._format_dict(risk_metrics)}

Recent Trades:
{len(recent_trades)} trades in period

Provide risk analysis and alerts.
"""
        
        try:
            analysis = self.llm.generate(
                prompt,
                model="gpt-4",
                temperature=0.3,
                max_tokens=1500
            )
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing risk: {e}")
            return f"Error analyzing risk: {e}"
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary for prompt."""
        lines = []
        for key, value in data.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

