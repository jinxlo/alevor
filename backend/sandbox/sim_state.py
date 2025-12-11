"""Simulated state for sandbox/backtest."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class SimulatedState:
    """Tracks simulated portfolio state."""
    
    def __init__(self, initial_balance: float):
        """Initialize simulated state.
        
        Args:
            initial_balance: Starting balance in base currency
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.open_positions: Dict[str, dict] = {}
        self.closed_trades: List[dict] = []
        self.total_pnl = 0.0
    
    def add_position(self, position_id: str, position: dict) -> None:
        """Add an open position.
        
        Args:
            position_id: Position identifier
            position: Position dictionary
        """
        self.open_positions[position_id] = position
        self.balance -= position.get("size", 0.0)
    
    def close_position(self, position_id: str, exit_price: float) -> dict:
        """Close a position and calculate PnL.
        
        Args:
            position_id: Position identifier
            exit_price: Exit price
        
        Returns:
            Closed trade dictionary with PnL
        """
        position = self.open_positions.pop(position_id, None)
        if not position:
            return {}
        
        entry_price = position.get("entry_price")
        size = position.get("size")
        
        # Calculate PnL
        pnl = (exit_price - entry_price) * size
        pnl_pct = (exit_price / entry_price) - 1.0
        
        # Update balance
        self.balance += size + pnl
        self.total_pnl += pnl
        
        trade = {
            **position,
            "exit_price": exit_price,
            "pnl": pnl,
            "pnl_pct": pnl_pct
        }
        
        self.closed_trades.append(trade)
        return trade
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Get total portfolio value.
        
        Args:
            current_prices: Current prices by pair
        
        Returns:
            Total portfolio value
        """
        value = self.balance
        
        for position in self.open_positions.values():
            pair = position.get("pair")
            current_price = current_prices.get(pair)
            if current_price:
                entry_price = position.get("entry_price")
                size = position.get("size")
                unrealized_pnl = (current_price - entry_price) * size
                value += size + unrealized_pnl
        
        return value
