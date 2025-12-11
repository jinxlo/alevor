"""PnL calculation utilities."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PnLCalculator:
    """Calculates profit and loss for trades."""
    
    @staticmethod
    def calculate_pnl(
        entry_price: float,
        exit_price: float,
        size: float,
        is_long: bool = True
    ) -> tuple[float, float]:
        """Calculate PnL for a trade.
        
        Args:
            entry_price: Entry price
            exit_price: Exit price
            size: Position size
            is_long: True for long position, False for short
        
        Returns:
            Tuple of (absolute PnL, PnL percentage)
        """
        if is_long:
            pnl = (exit_price - entry_price) * size
            pnl_pct = (exit_price / entry_price) - 1.0
        else:
            pnl = (entry_price - exit_price) * size
            pnl_pct = (entry_price / exit_price) - 1.0
        
        return pnl, pnl_pct
    
    @staticmethod
    def calculate_cumulative_pnl(trades: list[dict]) -> float:
        """Calculate cumulative PnL from list of trades.
        
        Args:
            trades: List of trade dictionaries with 'pnl' key
        
        Returns:
            Cumulative PnL
        """
        return sum(trade.get("pnl", 0.0) for trade in trades)
    
    @staticmethod
    def calculate_win_rate(trades: list[dict]) -> float:
        """Calculate win rate.
        
        Args:
            trades: List of closed trades with 'pnl' key
        
        Returns:
            Win rate as fraction (0-1)
        """
        if not trades:
            return 0.0
        
        winning_trades = sum(1 for trade in trades if trade.get("pnl", 0) > 0)
        return winning_trades / len(trades)

