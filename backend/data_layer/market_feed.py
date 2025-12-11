"""Live market data feed for prices and pool reserves."""

import logging
from typing import Optional
from web3 import Web3
from web3.types import ChecksumAddress

logger = logging.getLogger(__name__)


class MarketFeed:
    """Fetches live market data from on-chain sources."""
    
    def __init__(self, web3_client, pairs_config: dict):
        """Initialize market feed.
        
        Args:
            web3_client: Web3 client instance
            pairs_config: Pairs configuration from config/pairs.yaml
        """
        self.web3 = web3_client
        self.pairs = pairs_config.get("pairs", [])
        self._pair_map = {pair["symbol"]: pair for pair in self.pairs}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for a trading pair.
        
        Args:
            symbol: Pair symbol (e.g., "MATIC/USDC")
        
        Returns:
            Price (quote/base) or None if unavailable
        """
        pair = self._pair_map.get(symbol)
        if not pair:
            logger.error(f"Pair not found: {symbol}")
            return None
        
        try:
            # Get reserves from pool
            pool_address = pair["dex"]["pool_address"]
            reserves = self._get_pool_reserves(pool_address, pair)
            
            if reserves is None:
                return None
            
            reserve_base, reserve_quote = reserves
            if reserve_base == 0:
                return None
            
            price = reserve_quote / reserve_base
            return price
        
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_pool_reserves(self, symbol: str) -> Optional[tuple[float, float]]:
        """Get pool reserves for a pair.
        
        Args:
            symbol: Pair symbol
        
        Returns:
            Tuple of (base_reserve, quote_reserve) or None
        """
        pair = self._pair_map.get(symbol)
        if not pair:
            return None
        
        pool_address = pair["dex"]["pool_address"]
        return self._get_pool_reserves(pool_address, pair)
    
    def _get_pool_reserves(
        self, 
        pool_address: ChecksumAddress, 
        pair: dict
    ) -> Optional[tuple[float, float]]:
        """Get reserves from pool contract.
        
        This is a simplified implementation. Actual implementation depends on
        the DEX (Uniswap V2/V3, etc.).
        
        Args:
            pool_address: Pool contract address
            pair: Pair configuration
        
        Returns:
            Tuple of (base_reserve, quote_reserve) or None
        """
        try:
            # Simplified: assumes Uniswap V2 style getReserves()
            # For V3, would need to query tick data
            pool_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getReserves",
                    "outputs": [
                        {"name": "_reserve0", "type": "uint112"},
                        {"name": "_reserve1", "type": "uint112"},
                        {"name": "_blockTimestampLast", "type": "uint32"}
                    ],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "token0",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "token1",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function"
                }
            ]
            
            pool_contract = self.web3.eth.contract(address=pool_address, abi=pool_abi)
            reserves = pool_contract.functions.getReserves().call()
            
            token0 = pool_contract.functions.token0().call()
            base_address = Web3.to_checksum_address(pair["tokens"][pair["base"]])
            
            # Determine which reserve is base and which is quote
            if token0.lower() == base_address.lower():
                reserve_base = reserves[0] / 1e18  # Adjust decimals as needed
                reserve_quote = reserves[1] / 1e6   # USDC typically 6 decimals
            else:
                reserve_base = reserves[1] / 1e18
                reserve_quote = reserves[0] / 1e6
            
            return (reserve_base, reserve_quote)
        
        except Exception as e:
            logger.error(f"Error getting reserves from pool {pool_address}: {e}")
            return None
    
    def get_spread(self, symbol: str) -> Optional[float]:
        """Get bid-ask spread (simplified - uses price impact as proxy).
        
        Args:
            symbol: Pair symbol
        
        Returns:
            Spread as fraction or None
        """
        # Simplified implementation
        # In production, would query order book or use recent trade data
        return 0.0001  # 0.01% default spread
