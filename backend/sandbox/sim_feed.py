"""Simulated market data feed."""

import logging
from typing import Optional, Dict
import pandas as pd

from ..data_layer.historical_data import HistoricalDataLoader

logger = logging.getLogger(__name__)


class SimFeed:
    """Provides historical or simulated market data."""
    
    def __init__(self, historical_loader: HistoricalDataLoader):
        """Initialize simulated feed.
        
        Args:
            historical_loader: Historical data loader
        """
        self.historical_loader = historical_loader
        self.current_data: Dict[str, pd.DataFrame] = {}
    
    def get_price(self, symbol: str, timestamp: Optional[int] = None) -> Optional[float]:
        """Get price for a symbol.
        
        Args:
            symbol: Trading pair
            timestamp: Timestamp (for historical) or None for latest
        
        Returns:
            Price or None
        """
        if symbol not in self.current_data:
            return None
        
        df = self.current_data[symbol]
        if df.empty:
            return None
        
        if timestamp:
            # Get price at specific timestamp
            matching = df[df["timestamp"] == timestamp]
            if not matching.empty:
                return float(matching.iloc[0]["close"])
            return None
        else:
            # Get latest price
            return float(df.iloc[-1]["close"])
    
    def load_historical(self, symbol: str, start_ts: int, end_ts: int) -> bool:
        """Load historical data for a symbol.
        
        Args:
            symbol: Trading pair
            start_ts: Start timestamp
            end_ts: End timestamp
        
        Returns:
            True if successful
        """
        df = self.historical_loader.load_ohlcv(symbol, start_ts, end_ts, interval_seconds=300)
        if df is not None and not df.empty:
            self.current_data[symbol] = df
            return True
        return False
    
    def get_ohlcv(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get OHLCV data for a symbol.
        
        Args:
            symbol: Trading pair
        
        Returns:
            OHLCV DataFrame or None
        """
        return self.current_data.get(symbol)
