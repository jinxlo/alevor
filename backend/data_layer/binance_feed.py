"""Binance API integration for market data."""

import logging
import time
from typing import Optional, Dict
import pandas as pd
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class BinanceFeed:
    """Fetches market data from Binance API."""
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    # Map our symbols to Binance symbols
    SYMBOL_MAP = {
        "MATIC/USDC": "MATICUSDC",
        "ETH/USDC": "ETHUSDC",
        "BTC/USDC": "BTCUSDC",
        "BNB/USDC": "BNBUSDC",
    }
    
    # Interval mapping (seconds -> Binance interval)
    INTERVAL_MAP = {
        60: "1m",
        300: "5m",
        900: "15m",
        3600: "1h",
        14400: "4h",
        86400: "1d",
    }
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize Binance feed.
        
        Args:
            api_key: Binance API key (optional for public endpoints)
            api_secret: Binance API secret (optional for public endpoints)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-MBX-APIKEY": api_key})
    
    def get_klines(
        self,
        symbol: str,
        interval: str = "5m",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> Optional[pd.DataFrame]:
        """Get kline/candlestick data from Binance.
        
        Args:
            symbol: Trading pair (e.g., "MATICUSDC")
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
            limit: Number of klines to return (max 1000)
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        url = f"{self.BASE_URL}/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": min(limit, 1000)
        }
        
        if start_time:
            params["startTime"] = start_time * 1000  # Convert to milliseconds
        if end_time:
            params["endTime"] = end_time * 1000
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ])
            
            # Convert timestamp from milliseconds to seconds
            df["timestamp"] = df["timestamp"] // 1000
            
            # Convert price/volume columns to float
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            
            # Select and reorder columns
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            
            return df
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching klines from Binance: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing Binance data: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol.
        
        Args:
            symbol: Trading pair (e.g., "MATICUSDC")
        
        Returns:
            Current price or None
        """
        url = f"{self.BASE_URL}/ticker/price"
        params = {"symbol": symbol.upper()}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data["price"])
        except Exception as e:
            logger.error(f"Error fetching price from Binance: {e}")
            return None
    
    def get_24h_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24-hour ticker statistics.
        
        Args:
            symbol: Trading pair
        
        Returns:
            Dictionary with ticker data or None
        """
        url = f"{self.BASE_URL}/ticker/24hr"
        params = {"symbol": symbol.upper()}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching 24h ticker from Binance: {e}")
            return None
    
    def normalize_symbol(self, symbol: str) -> Optional[str]:
        """Convert our symbol format to Binance format.
        
        Args:
            symbol: Our format (e.g., "MATIC/USDC")
        
        Returns:
            Binance format (e.g., "MATICUSDC") or None
        """
        return self.SYMBOL_MAP.get(symbol, symbol.replace("/", "").upper())
    
    def get_interval_string(self, interval_seconds: int) -> str:
        """Convert interval in seconds to Binance interval string.
        
        Args:
            interval_seconds: Interval in seconds
        
        Returns:
            Binance interval string (e.g., "5m")
        """
        return self.INTERVAL_MAP.get(interval_seconds, "5m")

