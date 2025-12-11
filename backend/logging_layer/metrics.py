"""Aggregated metrics calculation."""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .db import Database

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculates aggregated trading metrics."""
    
    def __init__(self, db: Database, mode: str = "live"):
        """Initialize metrics calculator.
        
        Args:
            db: Database instance
            mode: "live" or "sandbox"
        """
        self.db = db
        self.mode = mode
        self.table = "trades_live" if mode == "live" else "trades_sandbox"
    
    def get_pair_metrics(self, pair: str, days: int = 30) -> Dict:
        """Get metrics for a specific pair.
        
        Args:
            pair: Trading pair
            days: Number of days to look back
        
        Returns:
            Dictionary of metrics
        """
        start_date = datetime.now() - timedelta(days=days)
        
        query = f"""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                AVG(CASE WHEN pnl > 0 THEN pnl ELSE NULL END) as avg_win,
                AVG(CASE WHEN pnl < 0 THEN pnl ELSE NULL END) as avg_loss
            FROM {self.table}
            WHERE pair = %s 
            AND timestamp >= %s
            AND action_type = 'CLOSE'
        """
        
        try:
            result = self.db.execute_query(query, (pair, start_date))
            if result:
                row = result[0]
                total = row["total_trades"] or 0
                wins = row["winning_trades"] or 0
                win_rate = wins / total if total > 0 else 0.0
                
                return {
                    "pair": pair,
                    "total_trades": total,
                    "winning_trades": wins,
                    "win_rate": win_rate,
                    "total_pnl": float(row["total_pnl"] or 0),
                    "avg_pnl": float(row["avg_pnl"] or 0),
                    "avg_win": float(row["avg_win"] or 0),
                    "avg_loss": float(row["avg_loss"] or 0)
                }
        except Exception as e:
            logger.error(f"Error calculating pair metrics: {e}")
        
        return {}
    
    def get_regime_metrics(self, regime: str, days: int = 30) -> Dict:
        """Get metrics for a specific regime.
        
        Args:
            regime: Market regime
            days: Number of days to look back
        
        Returns:
            Dictionary of metrics
        """
        start_date = datetime.now() - timedelta(days=days)
        
        query = f"""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM {self.table}
            WHERE regime = %s 
            AND timestamp >= %s
            AND action_type = 'CLOSE'
        """
        
        try:
            result = self.db.execute_query(query, (regime, start_date))
            if result:
                row = result[0]
                total = row["total_trades"] or 0
                wins = row["winning_trades"] or 0
                
                return {
                    "regime": regime,
                    "total_trades": total,
                    "winning_trades": wins,
                    "win_rate": wins / total if total > 0 else 0.0,
                    "total_pnl": float(row["total_pnl"] or 0),
                    "avg_pnl": float(row["avg_pnl"] or 0)
                }
        except Exception as e:
            logger.error(f"Error calculating regime metrics: {e}")
        
        return {}
    
    def get_daily_stats(self, date: Optional[datetime] = None) -> Dict:
        """Get daily statistics.
        
        Args:
            date: Date to query (default: today)
        
        Returns:
            Dictionary of daily stats
        """
        if date is None:
            date = datetime.now()
        
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        query = f"""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM {self.table}
            WHERE timestamp >= %s AND timestamp < %s
            AND action_type = 'CLOSE'
        """
        
        try:
            result = self.db.execute_query(query, (start, end))
            if result:
                row = result[0]
                total = row["total_trades"] or 0
                wins = row["winning_trades"] or 0
                
                return {
                    "date": date.date(),
                    "total_trades": total,
                    "winning_trades": wins,
                    "win_rate": wins / total if total > 0 else 0.0,
                    "total_pnl": float(row["total_pnl"] or 0),
                    "avg_pnl": float(row["avg_pnl"] or 0)
                }
        except Exception as e:
            logger.error(f"Error calculating daily stats: {e}")
        
        return {}

