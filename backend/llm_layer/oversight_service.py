"""Risk oversight service."""

import logging
from datetime import datetime, timedelta

from .agents.risk_agent import RiskAgent
from .api_adapter import LLMAdapter
from ..logging_layer.db import Database
from ..logging_layer.metrics import MetricsCalculator

logger = logging.getLogger(__name__)


class OversightService:
    """Service for risk oversight."""
    
    def __init__(self, db: Database, llm_adapter: LLMAdapter):
        """Initialize oversight service.
        
        Args:
            db: Database instance
            llm_adapter: LLM adapter instance
        """
        self.db = db
        self.metrics_calc = MetricsCalculator(db, mode="live")
        self.risk_agent = RiskAgent(llm_adapter)
    
    def run_risk_check(self) -> str:
        """Run risk check and generate report.
        
        Returns:
            Risk analysis text
        """
        # Get recent risk metrics
        query = """
            SELECT * FROM risk_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """
        risk_data = self.db.execute_query(query)
        
        # Get recent trades
        query = """
            SELECT * FROM trades_live
            WHERE timestamp >= %s
            ORDER BY timestamp DESC
            LIMIT 20
        """
        recent_trades = self.db.execute_query(
            query,
            (datetime.now() - timedelta(days=1),)
        )
        
        risk_metrics = risk_data[0] if risk_data else {}
        
        analysis = self.risk_agent.analyze_risk(
            risk_metrics=risk_metrics,
            recent_trades=recent_trades
        )
        
        return analysis
    
    def summarize_risk_state(self) -> str:
        """Get summary of current risk state.
        
        Returns:
            Risk summary
        """
        return self.run_risk_check()


def main():
    """Main entry point."""
    import os
    from ..logging_layer.db import Database
    
    logging.basicConfig(level=logging.INFO)
    
    db = Database(os.getenv("DB_URL"))
    llm_adapter = LLMAdapter()
    
    service = OversightService(db, llm_adapter)
    analysis = service.run_risk_check()
    print(analysis)


if __name__ == "__main__":
    main()

