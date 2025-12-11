"""Simulated action data classes."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SimOpenAction:
    """Simulated open position action."""
    
    pair: str
    size: float
    entry_price: float
    stop_loss_pct: float
    take_profit_pct: float
    ev: Optional[float] = None
    p: Optional[float] = None
    friction: Optional[float] = None
    regime: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SimCloseAction:
    """Simulated close position action."""
    
    position_id: str
    pair: str
    reason: str
    exit_price: float
    pnl: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
