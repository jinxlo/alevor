"""Exit logic for closing positions."""

import logging
from typing import Optional, List
from datetime import datetime

from ..engine_live.actions import ClosePositionAction
from ..engine_live.state import EngineState

logger = logging.getLogger(__name__)


class ExitLogic:
    """Determines when to exit positions."""
    
    def __init__(self, risk_config: dict):
        """Initialize exit logic.
        
        Args:
            risk_config: Risk configuration
        """
        self.risk_config = risk_config
    
    def check_exits(
        self,
        open_positions: List[dict],
        current_prices: dict[str, float],
        regime_changes: dict[str, str]
    ) -> List[ClosePositionAction]:
        """Check if any positions should be closed.
        
        Args:
            open_positions: List of open position dictionaries
            current_prices: Current prices by symbol
            regime_changes: Regime changes by symbol (if any)
        
        Returns:
            List of ClosePositionAction objects
        """
        exit_actions = []
        
        for position in open_positions:
            symbol = position.get("pair")
            entry_price = position.get("entry_price")
            sl_pct = position.get("stop_loss_pct")
            tp_pct = position.get("take_profit_pct")
            current_price = current_prices.get(symbol)
            
            if current_price is None or entry_price is None:
                continue
            
            # Check stop loss
            if sl_pct and current_price <= entry_price * (1 - sl_pct):
                action = ClosePositionAction(
                    position_id=position.get("id"),
                    pair=symbol,
                    reason="STOP_LOSS",
                    exit_price=current_price
                )
                exit_actions.append(action)
                continue
            
            # Check take profit
            if tp_pct and current_price >= entry_price * (1 + tp_pct):
                action = ClosePositionAction(
                    position_id=position.get("id"),
                    pair=symbol,
                    reason="TAKE_PROFIT",
                    exit_price=current_price
                )
                exit_actions.append(action)
                continue
            
            # Check regime change
            if symbol in regime_changes:
                new_regime = regime_changes[symbol]
                if new_regime == "NO_TRADE":
                    action = ClosePositionAction(
                        position_id=position.get("id"),
                        pair=symbol,
                        reason="REGIME_CHANGE",
                        exit_price=current_price
                    )
                    exit_actions.append(action)
        
        return exit_actions

