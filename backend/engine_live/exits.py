"""Exit detection logic."""

import logging
from typing import List, Optional
from datetime import datetime

from .actions import ClosePositionAction
from .state import EngineState

logger = logging.getLogger(__name__)


class ExitDetector:
    """Detects when positions should be closed."""
    
    def __init__(self, state: EngineState):
        """Initialize exit detector.
        
        Args:
            state: Engine state instance
        """
        self.state = state
    
    def check_stop_loss(
        self,
        position: dict,
        current_price: float
    ) -> Optional[ClosePositionAction]:
        """Check if stop loss is hit.
        
        Args:
            position: Position dictionary
            current_price: Current market price
        
        Returns:
            ClosePositionAction if SL hit, None otherwise
        """
        entry_price = position.get("entry_price")
        sl_pct = position.get("stop_loss_pct")
        
        if entry_price is None or sl_pct is None:
            return None
        
        sl_price = entry_price * (1 - sl_pct)
        
        if current_price <= sl_price:
            return ClosePositionAction(
                position_id=position.get("id"),
                pair=position.get("pair"),
                reason="STOP_LOSS",
                exit_price=current_price
            )
        
        return None
    
    def check_take_profit(
        self,
        position: dict,
        current_price: float
    ) -> Optional[ClosePositionAction]:
        """Check if take profit is hit.
        
        Args:
            position: Position dictionary
            current_price: Current market price
        
        Returns:
            ClosePositionAction if TP hit, None otherwise
        """
        entry_price = position.get("entry_price")
        tp_pct = position.get("take_profit_pct")
        
        if entry_price is None or tp_pct is None:
            return None
        
        tp_price = entry_price * (1 + tp_pct)
        
        if current_price >= tp_price:
            return ClosePositionAction(
                position_id=position.get("id"),
                pair=position.get("pair"),
                reason="TAKE_PROFIT",
                exit_price=current_price
            )
        
        return None
    
    def check_all_exits(
        self,
        current_prices: dict[str, float]
    ) -> List[ClosePositionAction]:
        """Check all open positions for exit conditions.
        
        Args:
            current_prices: Current prices by pair symbol
        
        Returns:
            List of ClosePositionAction objects
        """
        exit_actions = []
        
        for position_id, position in self.state.open_positions.items():
            pair = position.get("pair")
            current_price = current_prices.get(pair)
            
            if current_price is None:
                continue
            
            # Check stop loss
            sl_action = self.check_stop_loss(position, current_price)
            if sl_action:
                exit_actions.append(sl_action)
                continue
            
            # Check take profit
            tp_action = self.check_take_profit(position, current_price)
            if tp_action:
                exit_actions.append(tp_action)
        
        return exit_actions
