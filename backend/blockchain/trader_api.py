"""Trader contract API wrapper."""

import logging
from typing import Optional
from web3.contract import Contract

logger = logging.getLogger(__name__)


class TraderAPI:
    """Wrapper around Trader contract."""
    
    def __init__(self, trader_contract: Contract, web3_client):
        """Initialize trader API.
        
        Args:
            trader_contract: Trader contract instance
            web3_client: Web3Client instance
        """
        self.contract = trader_contract
        self.w3 = web3_client
    
    def open_position(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        amount_out_min: float,
        deadline: int
    ) -> Optional[str]:
        """Open a position (execute trade).
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount (in base units)
            amount_out_min: Minimum output (slippage protection)
            deadline: Transaction deadline (Unix timestamp)
        
        Returns:
            Transaction hash or None
        """
        try:
            amount_in_wei = int(amount_in * 1e18)  # Adjust decimals
            amount_out_min_wei = int(amount_out_min * 1e18)
            
            tx_data = self.contract.encodeABI(
                fn_name="executeTrade",
                args=[token_in, token_out, amount_in_wei, amount_out_min_wei, deadline]
            )
            tx_hash = self.w3.send_transaction(
                to=self.contract.address,
                data=tx_data,
                value=0
            )
            return tx_hash
        except Exception as e:
            logger.error(f"Error opening position: {e}")
            return None
    
    def close_position(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        amount_out_min: float,
        deadline: int
    ) -> Optional[str]:
        """Close a position (reverse trade).
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount
            amount_out_min: Minimum output
            deadline: Transaction deadline
        
        Returns:
            Transaction hash or None
        """
        try:
            amount_in_wei = int(amount_in * 1e18)
            amount_out_min_wei = int(amount_out_min * 1e18)
            
            tx_data = self.contract.encodeABI(
                fn_name="closePosition",
                args=[token_in, token_out, amount_in_wei, amount_out_min_wei, deadline]
            )
            tx_hash = self.w3.send_transaction(
                to=self.contract.address,
                data=tx_data,
                value=0
            )
            return tx_hash
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return None
    
    def request_capital(self, amount: float) -> Optional[str]:
        """Request capital from vault.
        
        Args:
            amount: Amount to request (in base units)
        
        Returns:
            Transaction hash or None
        """
        try:
            amount_wei = int(amount * 1e18)
            
            tx_data = self.contract.encodeABI(fn_name="requestCapital", args=[amount_wei])
            tx_hash = self.w3.send_transaction(
                to=self.contract.address,
                data=tx_data,
                value=0
            )
            return tx_hash
        except Exception as e:
            logger.error(f"Error requesting capital: {e}")
            return None

