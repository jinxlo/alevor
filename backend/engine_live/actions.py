"""Data classes for trading actions."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class OpenPositionAction:
    """Represents an action to open a new position."""

    pair: str
    size: float  # Position size in base units
    entry_price: float
    stop_loss_pct: float  # Stop loss as percentage (e.g., 0.01 for 1%)
    take_profit_pct: float  # Take profit as percentage (e.g., 0.04 for 4%)
    ev: Optional[float] = None  # Expected value
    p: Optional[float] = None  # Probability of winning
    friction: Optional[float] = None  # Estimated friction
    regime: Optional[str] = None  # Market regime (TREND/RANGE)
    metadata: Optional[Dict[str, Any]] = None  # Additional context


@dataclass
class ClosePositionAction:
    """Represents an action to close an existing position."""

    position_id: str
    pair: str
    reason: str  # "STOP_LOSS", "TAKE_PROFIT", "REGIME_CHANGE", etc.
    exit_price: float
    pnl: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

