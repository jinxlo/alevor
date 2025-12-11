"""Regime model for market regime classification."""

import logging
import pickle
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class RegimeModel:
    """Classifies market regime (TREND/RANGE/NO_TRADE)."""
    
    def __init__(self, artifact_path: Optional[str] = None):
        """Initialize regime model.
        
        Args:
            artifact_path: Path to model artifact (.pkl file)
        """
        self.model = None
        self.artifact_path = artifact_path
        
        if artifact_path:
            self.load(artifact_path)
    
    def load(self, artifact_path: str) -> None:
        """Load model from artifact.
        
        Args:
            artifact_path: Path to .pkl file
        """
        try:
            with open(artifact_path, "rb") as f:
                self.model = pickle.load(f)
            logger.info(f"Loaded regime model from {artifact_path}")
        except Exception as e:
            logger.error(f"Error loading regime model: {e}")
            self.model = None
    
    def predict_regime(self, features: np.ndarray) -> str:
        """Predict market regime.
        
        Args:
            features: Feature vector
        
        Returns:
            "TREND", "RANGE", or "NO_TRADE"
        """
        if self.model is None:
            logger.warning("Model not loaded, returning default NO_TRADE")
            return "NO_TRADE"
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            prediction = self.model.predict(features)[0]
            
            # Map prediction to regime string
            if isinstance(prediction, (int, np.integer)):
                regime_map = {0: "TREND", 1: "RANGE", 2: "NO_TRADE"}
                return regime_map.get(int(prediction), "NO_TRADE")
            else:
                return str(prediction).upper()
        
        except Exception as e:
            logger.error(f"Error predicting regime: {e}")
            return "NO_TRADE"
    
    def predict_proba(self, features: np.ndarray) -> dict[str, float]:
        """Get probability distribution over regimes.
        
        Args:
            features: Feature vector
        
        Returns:
            Dictionary mapping regime to probability
        """
        if self.model is None:
            return {"TREND": 0.0, "RANGE": 0.0, "NO_TRADE": 1.0}
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(features)[0]
                return {
                    "TREND": float(proba[0]),
                    "RANGE": float(proba[1]),
                    "NO_TRADE": float(proba[2]) if len(proba) > 2 else 0.0
                }
            else:
                # Fallback: return deterministic prediction
                regime = self.predict_regime(features)
                return {
                    "TREND": 1.0 if regime == "TREND" else 0.0,
                    "RANGE": 1.0 if regime == "RANGE" else 0.0,
                    "NO_TRADE": 1.0 if regime == "NO_TRADE" else 0.0
                }
        
        except Exception as e:
            logger.error(f"Error getting regime probabilities: {e}")
            return {"TREND": 0.0, "RANGE": 0.0, "NO_TRADE": 1.0}
