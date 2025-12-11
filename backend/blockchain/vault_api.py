"""Vault contract API wrapper."""

import logging
from typing import Optional
from web3.contract import Contract

logger = logging.getLogger(__name__)


class VaultAPI:
    """Wrapper around Vault contract."""
    
    def __init__(self, vault_contract: Contract, web3_client):
        """Initialize vault API.
        
        Args:
            vault_contract: Vault contract instance
            web3_client: Web3Client instance
        """
        self.contract = vault_contract
        self.w3 = web3_client
    
    def get_tvl(self) -> Optional[float]:
        """Get total value locked.
        
        Returns:
            TVL in base units or None
        """
        try:
            total_assets = self.contract.functions.totalAssets().call()
            # Convert from wei (assuming 18 decimals, adjust as needed)
            return total_assets / 1e18
        except Exception as e:
            logger.error(f"Error getting TVL: {e}")
            return None
    
    def get_total_shares(self) -> Optional[int]:
        """Get total shares outstanding.
        
        Returns:
            Total shares or None
        """
        try:
            return self.contract.functions.totalShares().call()
        except Exception as e:
            logger.error(f"Error getting total shares: {e}")
            return None
    
    def deposit(self, amount: float) -> Optional[str]:
        """Deposit assets into vault.
        
        Args:
            amount: Amount to deposit (in base units)
        
        Returns:
            Transaction hash or None
        """
        try:
            amount_wei = int(amount * 1e18)  # Adjust decimals as needed
            
            tx_data = self.contract.encodeABI(fn_name="deposit", args=[amount_wei])
            tx_hash = self.w3.send_transaction(
                to=self.contract.address,
                data=tx_data,
                value=0
            )
            return tx_hash
        except Exception as e:
            logger.error(f"Error depositing: {e}")
            return None
    
    def withdraw(self, shares: int) -> Optional[str]:
        """Withdraw assets from vault.
        
        Args:
            shares: Number of shares to redeem
        
        Returns:
            Transaction hash or None
        """
        try:
            tx_data = self.contract.encodeABI(fn_name="withdraw", args=[shares])
            tx_hash = self.w3.send_transaction(
                to=self.contract.address,
                data=tx_data,
                value=0
            )
            return tx_hash
        except Exception as e:
            logger.error(f"Error withdrawing: {e}")
            return None

