"""Deterministic slippage and fee calculation."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def calculate_base_slippage(
    amount_in: float,
    reserve_in: float,
    reserve_out: float,
    fee_bps: int = 30  # 0.3% = 30 basis points
) -> float:
    """Calculate expected slippage for a swap (constant product formula).
    
    Uses x * y = k formula (Uniswap V2 style).
    
    Args:
        amount_in: Input token amount
        reserve_in: Input token reserve
        reserve_out: Output token reserve
        fee_bps: Fee in basis points (default 30 = 0.3%)
    
    Returns:
        Slippage as a fraction (e.g., 0.001 = 0.1%)
    """
    if reserve_in == 0 or reserve_out == 0:
        logger.warning("Zero reserves, returning high slippage")
        return 0.1  # 10% slippage for illiquid pools
    
    fee_multiplier = 1 - (fee_bps / 10000)
    amount_in_after_fee = amount_in * fee_multiplier
    
    # Constant product: (x + dx) * (y - dy) = x * y
    # dy = (y * dx) / (x + dx)
    amount_out = (reserve_out * amount_in_after_fee) / (reserve_in + amount_in_after_fee)
    
    # Price impact = (expected_price - actual_price) / expected_price
    expected_price = reserve_out / reserve_in
    actual_price = amount_out / amount_in
    
    slippage = abs(expected_price - actual_price) / expected_price
    
    return slippage


def calculate_fee(amount: float, fee_bps: int = 30) -> float:
    """Calculate trading fee.
    
    Args:
        amount: Trade amount
        fee_bps: Fee in basis points
    
    Returns:
        Fee amount
    """
    return amount * (fee_bps / 10000)


def calculate_base_friction(
    amount_in: float,
    reserve_in: float,
    reserve_out: float,
    fee_bps: int = 30
) -> float:
    """Calculate base friction F_base (slippage + fees).
    
    Args:
        amount_in: Input token amount
        reserve_in: Input token reserve
        reserve_out: Output token reserve
        fee_bps: Fee in basis points
    
    Returns:
        Friction as a fraction of trade value
    """
    slippage = calculate_base_slippage(amount_in, reserve_in, reserve_out, fee_bps)
    fee_pct = fee_bps / 10000
    
    # Friction = slippage + fee (both as fractions)
    friction = slippage + fee_pct
    
    return friction
