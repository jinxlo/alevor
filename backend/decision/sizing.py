"""Position sizing logic."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PositionSizer:
    """Calculates position size based on risk parameters."""
    
    def __init__(self, risk_config: dict):
        """Initialize position sizer.
        
        Args:
            risk_config: Risk configuration from config/risk.yaml
        """
        self.max_risk_per_trade = risk_config.get("max_risk_per_trade", 0.005)
        self.min_position_pct = risk_config.get("position_size", {}).get("min_pct", 0.02)
        self.max_position_pct = risk_config.get("position_size", {}).get("max_pct", 0.05)
    
    def calculate_position_size(
        self,
        capital: float,
        stop_loss_pct: float
    ) -> float:
        """Calculate position size based on risk.
        
        Formula: position_size = (capital * risk_per_trade) / stop_loss_pct
        
        Args:
            capital: Available capital (TVL)
            stop_loss_pct: Stop loss as percentage (e.g., 0.01 = 1%)
        
        Returns:
            Position size in base units
        """
        if stop_loss_pct <= 0:
            logger.error("Stop loss percentage must be positive")
            return 0.0
        
        # Risk-based sizing
        risk_amount = capital * self.max_risk_per_trade
        position_size = risk_amount / stop_loss_pct
        
        # Enforce min/max position size constraints
        min_size = capital * self.min_position_pct
        max_size = capital * self.max_position_pct
        
        if position_size < min_size:
            logger.debug(f"Position size {position_size} below minimum {min_size}, using minimum")
            position_size = min_size
        elif position_size > max_size:
            logger.debug(f"Position size {position_size} above maximum {max_size}, using maximum")
            position_size = max_size
        
        return position_size
    
    def validate_position_size(
        self,
        position_size: float,
        capital: float
    ) -> bool:
        """Validate position size against constraints.
        
        Args:
            position_size: Proposed position size
            capital: Available capital
        
        Returns:
            True if valid, False otherwise
        """
        min_size = capital * self.min_position_pct
        max_size = capital * self.max_position_pct
        
        if position_size < min_size:
            logger.warning(f"Position size {position_size} below minimum {min_size}")
            return False
        
        if position_size > max_size:
            logger.warning(f"Position size {position_size} above maximum {max_size}")
            return False
        
        return True

