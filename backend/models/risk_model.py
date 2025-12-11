"""Optional risk model for dynamic risk parameter adjustments."""

import logging
import pickle
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class RiskParams:
    """Risk parameters suggested by risk model."""
    
    def __init__(
        self,
        sl_multiplier: float = 1.0,
        tp_multiplier: float = 1.0,
        risk_multiplier: float = 1.0
    ):
        """Initialize risk parameters.
        
        Args:
            sl_multiplier: Multiplier for stop loss (e.g., 1.2 = 20% wider SL)
            tp_multiplier: Multiplier for take profit
            risk_multiplier: Multiplier for position size risk
        """
        self.sl_multiplier = sl_multiplier
        self.tp_multiplier = tp_multiplier
        self.risk_multiplier = risk_multiplier


class RiskModel:
    """Optional model for fine-tuning risk parameters."""
    
    def __init__(self, artifact_path: Optional[str] = None):
        """Initialize risk model.
        
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
            logger.info(f"Loaded risk model from {artifact_path}")
        except Exception as e:
            logger.error(f"Error loading risk model: {e}")
            self.model = None
    
    def suggest_risk_params(self, features: np.ndarray) -> RiskParams:
        """Suggest risk parameter adjustments.
        
        Args:
            features: Feature vector
        
        Returns:
            RiskParams with suggested multipliers
        """
        if self.model is None:
            # Return default (no adjustment)
            return RiskParams()
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # Model outputs [sl_mult, tp_mult, risk_mult]
            prediction = self.model.predict(features)[0]
            
            if len(prediction) >= 3:
                return RiskParams(
                    sl_multiplier=float(prediction[0]),
                    tp_multiplier=float(prediction[1]),
                    risk_multiplier=float(prediction[2])
                )
            else:
                return RiskParams()
        
        except Exception as e:
            logger.error(f"Error suggesting risk params: {e}")
            return RiskParams()
