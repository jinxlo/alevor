"""Friction model for predicting effective friction F."""

import logging
import pickle
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class FrictionModel:
    """ML model to refine friction F prediction."""
    
    def __init__(self, artifact_path: Optional[str] = None):
        """Initialize friction model.
        
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
            logger.info(f"Loaded friction model from {artifact_path}")
        except Exception as e:
            logger.error(f"Error loading friction model: {e}")
            self.model = None
    
    def predict_friction(
        self,
        order_size: float,
        liquidity: float,
        volatility: float,
        base_friction: float
    ) -> float:
        """Predict effective friction F.
        
        Args:
            order_size: Order size in base units
            liquidity: Pool liquidity in USD
            volatility: Current volatility (as fraction)
            base_friction: Base friction from slippage.py
        
        Returns:
            Predicted friction F (as fraction)
        """
        if self.model is None:
            # Fallback to base friction
            return base_friction
        
        try:
            # Build feature vector: [order_size, liquidity, volatility, base_friction]
            features = np.array([[order_size, liquidity, volatility, base_friction]])
            
            prediction = self.model.predict(features)[0]
            friction = float(prediction)
            
            # Ensure friction is non-negative and reasonable
            friction = max(0.0, min(friction, 0.1))  # Cap at 10%
            
            return friction
        
        except Exception as e:
            logger.error(f"Error predicting friction: {e}")
            return base_friction

