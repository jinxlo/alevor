"""Simulated trade executor."""

import logging
from typing import Dict

from .sim_state import SimulatedState
from .sim_actions import SimOpenAction, SimCloseAction
from ..data_layer.slippage import calculate_base_friction

logger = logging.getLogger(__name__)


class SimExecutor:
    """Executes trades in simulated environment."""
    
    def __init__(self, state: SimulatedState, apply_slippage: bool = True):
        """Initialize simulator executor.
        
        Args:
            state: Simulated state
            apply_slippage: Whether to apply slippage
        """
        self.state = state
        self.apply_slippage = apply_slippage
    
    def execute_open(
        self,
        action: SimOpenAction,
        reserves: tuple[float, float],
        position_id: str
    ) -> bool:
        """Execute simulated open action.
        
        Args:
            action: Open action
            reserves: Pool reserves (base, quote)
            position_id: Position identifier
        
        Returns:
            True if successful
        """
        if self.state.balance < action.size:
            logger.warning(f"Insufficient balance for {action.pair}")
            return False
        
        # Apply slippage if enabled
        entry_price = action.entry_price
        if self.apply_slippage:
            friction = calculate_base_friction(
                action.size,
                reserves[0],
                reserves[1],
                fee_bps=30
            )
            # Adjust entry price by slippage
            entry_price = entry_price * (1 + friction)
        
        position = {
            "id": position_id,
            "pair": action.pair,
            "entry_price": entry_price,
            "size": action.size,
            "stop_loss_pct": action.stop_loss_pct,
            "take_profit_pct": action.take_profit_pct,
            "ev": action.ev,
            "p": action.p,
            "regime": action.regime
        }
        
        self.state.add_position(position_id, position)
        logger.info(f"Opened simulated position {position_id} for {action.pair}")
        return True
    
    def execute_close(
        self,
        action: SimCloseAction,
        reserves: tuple[float, float]
    ) -> Dict:
        """Execute simulated close action.
        
        Args:
            action: Close action
            reserves: Pool reserves
        
        Returns:
            Closed trade dictionary
        """
        # Apply slippage if enabled
        exit_price = action.exit_price
        if self.apply_slippage:
            position = self.state.open_positions.get(action.position_id)
            if position:
                size = position.get("size", 0)
                friction = calculate_base_friction(
                    size,
                    reserves[0],
                    reserves[1],
                    fee_bps=30
                )
                exit_price = exit_price * (1 - friction)
        
        trade = self.state.close_position(action.position_id, exit_price)
        if trade:
            logger.info(f"Closed simulated position {action.position_id}, PnL: {trade.get('pnl', 0)}")
        
        return trade
