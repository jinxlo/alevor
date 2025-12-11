"""Edge model for predicting trade win probability."""

import logging
import pickle
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class EdgeModel:
    """Predicts probability p of winning trade."""
    
    def __init__(self, artifact_path: Optional[str] = None):
        """Initialize edge model.
        
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
            logger.info(f"Loaded edge model from {artifact_path}")
        except Exception as e:
            logger.error(f"Error loading edge model: {e}")
            self.model = None
    
    def predict_edge(self, features: np.ndarray) -> float:
        """Predict probability of winning trade.
        
        Args:
            features: Feature vector
        
        Returns:
            Probability p in range [0, 1]
        """
        if self.model is None:
            logger.warning("Model not loaded, returning default probability 0.5")
            return 0.5
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            prediction = self.model.predict_proba(features)[0]
            
            # If binary classifier, return probability of positive class
            if len(prediction) == 2:
                return float(prediction[1])
            else:
                # For regression models, clamp to [0, 1]
                prob = float(prediction[0])
                return max(0.0, min(1.0, prob))
        
        except Exception as e:
            logger.error(f"Error predicting edge: {e}")
            return 0.5
