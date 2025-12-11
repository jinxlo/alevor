"""Expected Value (EV) calculator for trade decisions."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EVCalculator:
    """Calculates expected value: EV = (p * W) - ((1 - p) * L) - F"""
    
    def calculate_ev(
        self,
        p: float,
        win_amount: float,
        loss_amount: float,
        friction: float
    ) -> float:
        """Calculate expected value.
        
        Args:
            p: Probability of winning (0-1)
            win_amount: Profit if trade wins (W)
            loss_amount: Loss if trade loses (L, positive value)
            friction: Effective friction F (as fraction of trade value)
        
        Returns:
            Expected value
        """
        if not (0 <= p <= 1):
            logger.warning(f"Invalid probability p={p}, clamping to [0, 1]")
            p = max(0.0, min(1.0, p))
        
        if win_amount < 0 or loss_amount < 0:
            logger.error("Win and loss amounts must be non-negative")
            return -float("inf")
        
        # EV = (p * W) - ((1 - p) * L) - F
        expected_win = p * win_amount
        expected_loss = (1 - p) * loss_amount
        ev = expected_win - expected_loss - friction
        
        return ev
    
    def calculate_ev_from_sl_tp(
        self,
        p: float,
        entry_price: float,
        sl_pct: float,
        tp_pct: float,
        position_size: float,
        friction: float
    ) -> tuple[float, dict]:
        """Calculate EV from SL/TP parameters.
        
        Args:
            p: Probability of winning
            entry_price: Entry price
            sl_pct: Stop loss as percentage (e.g., 0.01 = 1%)
            tp_pct: Take profit as percentage (e.g., 0.04 = 4%)
            position_size: Position size in base units
            friction: Effective friction F
        
        Returns:
            Tuple of (EV, debug_info dict)
        """
        sl_price = entry_price * (1 - sl_pct)
        tp_price = entry_price * (1 + tp_pct)
        
        loss_amount = position_size * sl_pct
        win_amount = position_size * tp_pct
        
        # Friction applies to trade value
        friction_cost = position_size * friction
        
        ev = self.calculate_ev(p, win_amount, loss_amount, friction_cost)
        
        debug_info = {
            "p": p,
            "win_amount": win_amount,
            "loss_amount": loss_amount,
            "friction": friction_cost,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "ev": ev
        }
        
        return ev, debug_info

