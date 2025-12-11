"""Feature engineering for ML models."""

import logging
import numpy as np
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


class FeatureBuilder:
    """Builds feature vectors from price history."""
    
    def __init__(self, lookback_periods: int = 100):
        """Initialize feature builder.
        
        Args:
            lookback_periods: Number of historical candles to use
        """
        self.lookback_periods = lookback_periods
    
    def build_features(self, ohlcv_df: pd.DataFrame) -> Optional[np.ndarray]:
        """Build feature vector from OHLCV data.
        
        Args:
            ohlcv_df: DataFrame with columns: timestamp, open, high, low, close, volume
        
        Returns:
            Feature vector as numpy array
        """
        if ohlcv_df.empty or len(ohlcv_df) < 50:
            logger.warning("Insufficient data for feature building")
            return None
        
        try:
            features = []
            
            # Price-based features
            close = ohlcv_df["close"].values
            high = ohlcv_df["high"].values
            low = ohlcv_df["low"].values
            volume = ohlcv_df["volume"].values
            
            # Returns
            returns = np.diff(close) / close[:-1]
            features.extend([
                returns[-1],  # Latest return
                np.mean(returns[-20:]),  # 20-period mean return
                np.std(returns[-20:]),  # 20-period volatility
            ])
            
            # Moving averages
            sma_20 = self._sma(close, 20)
            sma_50 = self._sma(close, 50)
            if sma_20 is not None and sma_50 is not None:
                features.extend([
                    close[-1] / sma_20[-1] - 1,  # Price vs SMA20
                    close[-1] / sma_50[-1] - 1,  # Price vs SMA50
                    sma_20[-1] / sma_50[-1] - 1,  # SMA20 vs SMA50
                ])
            
            # RSI
            rsi = self._rsi(close, 14)
            if rsi is not None:
                features.append(rsi[-1] / 100 - 0.5)  # Normalize to [-0.5, 0.5]
            
            # ATR (Average True Range)
            atr = self._atr(high, low, close, 14)
            if atr is not None:
                features.append(atr[-1] / close[-1])  # ATR as fraction of price
            
            # Volume features
            if len(volume) > 20:
                avg_volume = np.mean(volume[-20:])
                features.append(volume[-1] / avg_volume if avg_volume > 0 else 1.0)
            
            # Volatility (rolling std of returns)
            if len(returns) >= 20:
                features.append(np.std(returns[-20:]))
            
            return np.array(features)
        
        except Exception as e:
            logger.error(f"Error building features: {e}")
            return None
    
    def _sma(self, prices: np.ndarray, period: int) -> Optional[np.ndarray]:
        """Simple moving average."""
        if len(prices) < period:
            return None
        return pd.Series(prices).rolling(window=period).mean().values
    
    def _rsi(self, prices: np.ndarray, period: int = 14) -> Optional[np.ndarray]:
        """Relative Strength Index."""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = pd.Series(gains).rolling(window=period).mean().values
        avg_loss = pd.Series(losses).rolling(window=period).mean().values
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _atr(
        self, 
        high: np.ndarray, 
        low: np.ndarray, 
        close: np.ndarray, 
        period: int = 14
    ) -> Optional[np.ndarray]:
        """Average True Range."""
        if len(high) < period + 1:
            return None
        
        tr = np.maximum(
            high[1:] - low[1:],
            np.maximum(
                np.abs(high[1:] - close[:-1]),
                np.abs(low[1:] - close[:-1])
            )
        )
        
        atr = pd.Series(tr).rolling(window=period).mean().values
        return atr
