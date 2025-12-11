"""Router for LLM agent requests."""

import logging
from typing import Optional

from .agents.reporting_agent import ReportingAgent
from .agents.risk_agent import RiskAgent
from .agents.explainer_agent import ExplainerAgent
from .agents.research_agent import ResearchAgent

logger = logging.getLogger(__name__)


class LLMRouter:
    """Routes requests to appropriate LLM agents."""
    
    def __init__(
        self,
        reporting_agent: ReportingAgent,
        risk_agent: RiskAgent,
        explainer_agent: ExplainerAgent,
        research_agent: Optional[ResearchAgent] = None
    ):
        """Initialize router.
        
        Args:
            reporting_agent: Reporting agent instance
            risk_agent: Risk agent instance
            explainer_agent: Explainer agent instance
            research_agent: Research agent instance (optional)
        """
        self.reporting_agent = reporting_agent
        self.risk_agent = risk_agent
        self.explainer_agent = explainer_agent
        self.research_agent = research_agent
    
    def route(self, task: str, **kwargs) -> str:
        """Route task to appropriate agent.
        
        Args:
            task: Task type ("report", "risk", "explain", "research")
            **kwargs: Task-specific arguments
        
        Returns:
            Agent response
        """
        task_lower = task.lower()
        
        if task_lower in ["report", "reporting", "daily_report", "weekly_report"]:
            return self.reporting_agent.generate_report(**kwargs)
        elif task_lower in ["risk", "oversight", "risk_check"]:
            return self.risk_agent.analyze_risk(**kwargs)
        elif task_lower in ["explain", "explainer", "explanation"]:
            return self.explainer_agent.explain(**kwargs)
        elif task_lower in ["research", "market_research"]:
            if self.research_agent:
                return self.research_agent.research(**kwargs)
            else:
                return "Research agent not available"
        else:
            logger.warning(f"Unknown task: {task}")
            return f"Unknown task: {task}"

