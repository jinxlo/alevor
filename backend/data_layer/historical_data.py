"""Historical OHLCV data loading for ML and backtests."""

import logging
from typing import Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class HistoricalDataLoader:
    """Loads historical OHLCV data from various sources."""
    
    def __init__(self, data_source: str = "binance", binance_feed=None):
        """Initialize historical data loader.
        
        Args:
            data_source: Source type ("csv", "db", "api", "binance")
            binance_feed: BinanceFeed instance (required if data_source="binance")
        """
        self.data_source = data_source
        self.binance_feed = binance_feed
    
    def load_ohlcv(
        self,
        symbol: str,
        start_ts: int,
        end_ts: int,
        interval_seconds: int = 300
    ) -> Optional[pd.DataFrame]:
        """Load OHLCV data for a time window.
        
        Args:
            symbol: Pair symbol
            start_ts: Start timestamp
            end_ts: End timestamp
            interval_seconds: Candle interval (default 300 = 5min)
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        if self.data_source == "csv":
            return self._load_from_csv(symbol, start_ts, end_ts, interval_seconds)
        elif self.data_source == "db":
            return self._load_from_db(symbol, start_ts, end_ts, interval_seconds)
        elif self.data_source == "api":
            return self._load_from_api(symbol, start_ts, end_ts, interval_seconds)
        elif self.data_source == "binance":
            return self._load_from_binance(symbol, start_ts, end_ts, interval_seconds)
        else:
            logger.error(f"Unknown data source: {self.data_source}")
            return None
    
    def _load_from_csv(
        self,
        symbol: str,
        start_ts: int,
        end_ts: int,
        interval_seconds: int
    ) -> Optional[pd.DataFrame]:
        """Load from CSV file.
        
        Expected CSV format:
        timestamp,open,high,low,close,volume
        """
        # Placeholder - would read from actual CSV file
        logger.warning("CSV loading not implemented - returning empty DataFrame")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    
    def _load_from_db(
        self,
        symbol: str,
        start_ts: int,
        end_ts: int,
        interval_seconds: int
    ) -> Optional[pd.DataFrame]:
        """Load from database."""
        # Placeholder - would query database
        logger.warning("DB loading not implemented - returning empty DataFrame")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    
    def _load_from_api(
        self,
        symbol: str,
        start_ts: int,
        end_ts: int,
        interval_seconds: int
    ) -> Optional[pd.DataFrame]:
        """Load from external API (e.g., DEX aggregator)."""
        # Placeholder - would call external API
        logger.warning("API loading not implemented - returning empty DataFrame")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    
    def _load_from_binance(
        self,
        symbol: str,
        start_ts: int,
        end_ts: int,
        interval_seconds: int
    ) -> Optional[pd.DataFrame]:
        """Load from Binance API.
        
        Args:
            symbol: Pair symbol (e.g., "MATIC/USDC")
            start_ts: Start timestamp
            end_ts: End timestamp
            interval_seconds: Candle interval
        
        Returns:
            DataFrame with OHLCV data
        """
        if not self.binance_feed:
            logger.error("Binance feed not initialized")
            return None
        
        # Normalize symbol
        binance_symbol = self.binance_feed.normalize_symbol(symbol)
        if not binance_symbol:
            logger.error(f"Could not normalize symbol: {symbol}")
            return None
        
        # Get interval string
        interval_str = self.binance_feed.get_interval_string(interval_seconds)
        
        # Binance has a limit of 1000 klines per request
        # We need to chunk large requests
        all_data = []
        current_start = start_ts
        max_klines_per_request = 1000
        
        while current_start < end_ts:
            # Calculate how many klines we can get in this request
            time_range = end_ts - current_start
            klines_in_range = time_range // interval_seconds
            limit = min(klines_in_range, max_klines_per_request)
            
            df = self.binance_feed.get_klines(
                symbol=binance_symbol,
                interval=interval_str,
                start_time=current_start,
                end_time=end_ts,
                limit=limit
            )
            
            if df is None or df.empty:
                break
            
            all_data.append(df)
            
            # Move start time forward
            if len(df) < limit:
                break  # No more data available
            
            current_start = int(df["timestamp"].iloc[-1]) + interval_seconds
        
        if not all_data:
            logger.warning(f"No data retrieved from Binance for {symbol}")
            return None
        
        # Combine all chunks
        result_df = pd.concat(all_data, ignore_index=True)
        result_df = result_df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
        
        # Filter to exact time range
        result_df = result_df[
            (result_df["timestamp"] >= start_ts) & 
            (result_df["timestamp"] <= end_ts)
        ]
        
        return result_df.reset_index(drop=True)
    
    def get_feature_window(
        self,
        symbol: str,
        timestamp: int,
        lookback_periods: int = 100,
        interval_seconds: int = 300
    ) -> Optional[pd.DataFrame]:
        """Get feature window ending at given timestamp.
        
        Args:
            symbol: Pair symbol
            timestamp: End timestamp
            lookback_periods: Number of candles to look back
            interval_seconds: Candle interval
        
        Returns:
            DataFrame with historical candles
        """
        start_ts = timestamp - (lookback_periods * interval_seconds)
        return self.load_ohlcv(symbol, start_ts, timestamp, interval_seconds)
