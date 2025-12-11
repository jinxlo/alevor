"""Read on-chain state from smart contracts."""

import logging
from typing import Optional
from web3 import Web3

logger = logging.getLogger(__name__)


class OnChainState:
    """Reads on-chain state from vault and trader contracts."""
    
    def __init__(self, web3_client, contracts: dict):
        """Initialize on-chain state reader.
        
        Args:
            web3_client: Web3 client instance
            contracts: Contract instances dict (vault, trader, etc.)
        """
        self.web3 = web3_client
        self.vault = contracts.get("vault")
        self.trader = contracts.get("trader")
    
    def get_tvl(self) -> Optional[float]:
        """Get total value locked in vault.
        
        Returns:
            TVL in base units (e.g., USDC) or None
        """
        if not self.vault:
            logger.error("Vault contract not initialized")
            return None
        
        try:
            total_assets = self.vault.functions.totalAssets().call()
            # Convert from wei to human-readable (assuming 18 decimals, adjust as needed)
            return total_assets / 1e18
        except Exception as e:
            logger.error(f"Error getting TVL: {e}")
            return None
    
    def get_total_shares(self) -> Optional[int]:
        """Get total shares outstanding.
        
        Returns:
            Total shares or None
        """
        if not self.vault:
            return None
        
        try:
            return self.vault.functions.totalShares().call()
        except Exception as e:
            logger.error(f"Error getting total shares: {e}")
            return None
    
    def get_max_capital_per_trade(self) -> Optional[float]:
        """Get maximum capital allowed per trade.
        
        Returns:
            Max capital in base units or None
        """
        if not self.trader:
            return None
        
        try:
            max_capital = self.trader.functions.maxCapitalPerTrade().call()
            return max_capital / 1e18  # Adjust decimals
        except Exception as e:
            logger.error(f"Error getting max capital per trade: {e}")
            return None
    
    def get_open_positions(self) -> list[dict]:
        """Get list of open positions (if tracked on-chain).
        
        Returns:
            List of position dictionaries
        """
        # Placeholder - actual implementation depends on contract design
        # Positions might be tracked in a mapping or events
        logger.warning("get_open_positions not fully implemented")
        return []
