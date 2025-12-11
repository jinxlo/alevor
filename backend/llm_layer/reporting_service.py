"""Reporting service endpoint."""

import logging
from datetime import datetime, timedelta

from .agents.reporting_agent import ReportingAgent
from .api_adapter import LLMAdapter
from ..logging_layer.db import Database
from ..logging_layer.metrics import MetricsCalculator

logger = logging.getLogger(__name__)


class ReportingService:
    """Service for generating reports."""
    
    def __init__(self, db: Database, llm_adapter: LLMAdapter):
        """Initialize reporting service.
        
        Args:
            db: Database instance
            llm_adapter: LLM adapter instance
        """
        self.db = db
        self.metrics_calc = MetricsCalculator(db, mode="live")
        self.reporting_agent = ReportingAgent(llm_adapter)
    
    def generate_daily_report(self) -> str:
        """Generate daily trading report.
        
        Returns:
            Report text
        """
        yesterday = datetime.now() - timedelta(days=1)
        stats = self.metrics_calc.get_daily_stats(yesterday)
        
        # Get recent trades
        query = """
            SELECT * FROM trades_live
            WHERE DATE(timestamp) = %s
            ORDER BY timestamp DESC
            LIMIT 50
        """
        trades = self.db.execute_query(query, (yesterday.date(),))
        
        report = self.reporting_agent.generate_report(
            metrics=stats,
            trades=trades,
            period="daily"
        )
        
        return report
    
    def generate_weekly_report(self) -> str:
        """Generate weekly trading report.
        
        Returns:
            Report text
        """
        week_start = datetime.now() - timedelta(days=7)
        
        # Aggregate weekly stats
        query = """
            SELECT 
                COUNT(*) as total_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM trades_live
            WHERE timestamp >= %s
            AND action_type = 'CLOSE'
        """
        stats = self.db.execute_query(query, (week_start,))
        
        if stats:
            metrics = stats[0]
        else:
            metrics = {}
        
        report = self.reporting_agent.generate_report(
            metrics=metrics,
            trades=[],
            period="weekly"
        )
        
        return report


def main():
    """Main entry point."""
    import os
    from ..logging_layer.db import Database
    
    logging.basicConfig(level=logging.INFO)
    
    db = Database(os.getenv("DB_URL"))
    llm_adapter = LLMAdapter()
    
    service = ReportingService(db, llm_adapter)
    report = service.generate_daily_report()
    print(report)


if __name__ == "__main__":
    main()

