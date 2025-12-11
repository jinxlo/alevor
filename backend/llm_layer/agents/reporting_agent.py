"""Reporting agent for daily/weekly reports."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..api_adapter import LLMAdapter

logger = logging.getLogger(__name__)


class ReportingAgent:
    """Generates trading reports using LLM."""
    
    def __init__(self, llm_adapter: LLMAdapter, prompt_path: Optional[str] = None):
        """Initialize reporting agent.
        
        Args:
            llm_adapter: LLM adapter instance
            prompt_path: Path to prompt template
        """
        self.llm = llm_adapter
        self.prompt_template = self._load_prompt(prompt_path)
    
    def _load_prompt(self, prompt_path: Optional[str]) -> str:
        """Load prompt template."""
        if prompt_path is None:
            prompt_path = Path(__file__).parent.parent / "prompts" / "reporting_prompt.md"
        
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load prompt: {e}")
            return "Generate a trading report based on the provided metrics."
    
    def generate_report(
        self,
        metrics: Dict[str, Any],
        trades: list[Dict[str, Any]],
        period: str = "daily"
    ) -> str:
        """Generate trading report.
        
        Args:
            metrics: Performance metrics
            trades: List of trades
            period: Report period ("daily" or "weekly")
        
        Returns:
            Generated report text
        """
        prompt = f"""{self.prompt_template}

Generate a {period} trading report with the following data:

Metrics:
{self._format_metrics(metrics)}

Recent Trades:
{self._format_trades(trades[:10])}

Generate a comprehensive report.
"""
        
        try:
            report = self.llm.generate(
                prompt,
                model="gpt-4",
                temperature=0.7,
                max_tokens=2000
            )
            return report
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Error generating report: {e}"
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for prompt."""
        lines = []
        for key, value in metrics.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _format_trades(self, trades: list[Dict[str, Any]]) -> str:
        """Format trades for prompt."""
        if not trades:
            return "No trades"
        
        lines = []
        for trade in trades:
            lines.append(f"- {trade.get('pair')}: PnL {trade.get('pnl', 0)}")
        return "\n".join(lines)

