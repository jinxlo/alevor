"""In-memory process state for live engine."""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EngineState:
    """Tracks in-memory state for the trading engine."""
    
    def __init__(self):
        """Initialize engine state."""
        self.open_positions: Dict[str, dict] = {}  # position_id -> position dict
        self.cooldowns: Dict[str, datetime] = {}  # pair -> last trade time
        self.trades_today: int = 0
        self.last_trade_time: Optional[datetime] = None
        self.daily_pnl: float = 0.0
    
    def add_position(self, position_id: str, position: dict) -> None:
        """Add an open position.
        
        Args:
            position_id: Unique position identifier
            position: Position dictionary
        """
        self.open_positions[position_id] = position
        logger.debug(f"Added position {position_id} for {position.get('pair')}")
    
    def remove_position(self, position_id: str) -> Optional[dict]:
        """Remove a closed position.
        
        Args:
            position_id: Position identifier
        
        Returns:
            Removed position dict or None
        """
        position = self.open_positions.pop(position_id, None)
        if position:
            logger.debug(f"Removed position {position_id}")
        return position
    
    def get_positions_by_pair(self, pair: str) -> List[dict]:
        """Get all open positions for a pair.
        
        Args:
            pair: Trading pair
        
        Returns:
            List of position dictionaries
        """
        return [
            pos for pos in self.open_positions.values()
            if pos.get("pair") == pair
        ]
    
    def is_in_cooldown(self, pair: str, cooldown_seconds: int) -> bool:
        """Check if pair is in cooldown period.
        
        Args:
            pair: Trading pair
            cooldown_seconds: Cooldown period in seconds
        
        Returns:
            True if in cooldown
        """
        last_trade = self.cooldowns.get(pair)
        if last_trade is None:
            return False
        
        elapsed = (datetime.now() - last_trade).total_seconds()
        return elapsed < cooldown_seconds
    
    def set_cooldown(self, pair: str) -> None:
        """Set cooldown for a pair.
        
        Args:
            pair: Trading pair
        """
        self.cooldowns[pair] = datetime.now()
    
    def can_trade(self, global_cooldown_seconds: int) -> bool:
        """Check if global cooldown allows trading.
        
        Args:
            global_cooldown_seconds: Global cooldown period
        
        Returns:
            True if can trade
        """
        if self.last_trade_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_trade_time).total_seconds()
        return elapsed >= global_cooldown_seconds
    
    def record_trade(self) -> None:
        """Record that a trade was executed."""
        self.trades_today += 1
        self.last_trade_time = datetime.now()
    
    def reset_daily(self) -> None:
        """Reset daily counters (call at start of day)."""
        self.trades_today = 0
        self.daily_pnl = 0.0
