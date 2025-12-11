"""Regime classification logic."""

import logging
from typing import Optional
import numpy as np

from ..models.regime_model import RegimeModel
from ..data_layer.features import FeatureBuilder

logger = logging.getLogger(__name__)


class RegimeClassifier:
    """Classifies market regime and determines tradability."""
    
    def __init__(self, regime_model: RegimeModel, risk_config: dict):
        """Initialize regime classifier.
        
        Args:
            regime_model: Regime model instance
            risk_config: Risk configuration
        """
        self.regime_model = regime_model
        self.risk_config = risk_config
        self.feature_builder = FeatureBuilder()
    
    def classify_regime(
        self,
        ohlcv_df,
        volatility: Optional[float] = None,
        liquidity: Optional[float] = None
    ) -> str:
        """Classify market regime.
        
        Args:
            ohlcv_df: OHLCV DataFrame
            volatility: Current volatility (optional)
            liquidity: Pool liquidity (optional)
        
        Returns:
            "TREND", "RANGE", or "NO_TRADE"
        """
        try:
            # Build features
            features = self.feature_builder.build_features(ohlcv_df)
            if features is None:
                logger.warning("Could not build features, returning NO_TRADE")
                return "NO_TRADE"
            
            # Get model prediction
            regime = self.regime_model.predict_regime(features)
            
            # Additional checks for NO_TRADE
            if regime != "NO_TRADE":
                # Check liquidity threshold
                if liquidity is not None:
                    min_liquidity = self.risk_config.get("pairs", {}).get("min_liquidity_usd", 100000)
                    if liquidity < min_liquidity:
                        logger.info(f"Insufficient liquidity: {liquidity} < {min_liquidity}")
                        return "NO_TRADE"
                
                # Check volatility (if too high, might be NO_TRADE)
                if volatility is not None and volatility > 0.1:  # 10% volatility threshold
                    logger.info(f"Volatility too high: {volatility}")
                    return "NO_TRADE"
            
            return regime
        
        except Exception as e:
            logger.error(f"Error classifying regime: {e}")
            return "NO_TRADE"
    
    def is_tradable(self, regime: str) -> bool:
        """Check if regime is tradable.
        
        Args:
            regime: Market regime
        
        Returns:
            True if tradable, False otherwise
        """
        return regime in ["TREND", "RANGE"]

