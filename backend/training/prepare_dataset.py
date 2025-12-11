"""Prepare training datasets from logs."""

import logging
import pandas as pd
import numpy as np
from typing import Optional, Tuple

from ..logging_layer.db import Database

logger = logging.getLogger(__name__)


class DatasetPreparer:
    """Prepares ML training datasets from trade logs."""
    
    def __init__(self, db: Database):
        """Initialize dataset preparer.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def prepare_regime_dataset(self, lookback_days: int = 90) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Prepare dataset for regime model training.
        
        Args:
            lookback_days: Days of data to use
        
        Returns:
            Tuple of (X, y) or None
        """
        # Query features snapshots with regime labels
        query = """
            SELECT features, regime, timestamp, pair
            FROM features_snapshots
            WHERE timestamp >= NOW() - INTERVAL '%s days'
            AND regime IS NOT NULL
            ORDER BY timestamp
        """
        
        try:
            rows = self.db.execute_query(query, (lookback_days,))
            
            if not rows:
                logger.warning("No data found for regime dataset")
                return None
            
            X = []
            y = []
            
            for row in rows:
                features = row["features"]
                regime = row["regime"]
                
                # Convert features dict to array
                if isinstance(features, dict):
                    feature_vec = np.array(list(features.values()))
                else:
                    feature_vec = np.array(features)
                
                X.append(feature_vec)
                
                # Map regime to integer
                regime_map = {"TREND": 0, "RANGE": 1, "NO_TRADE": 2}
                y.append(regime_map.get(regime.upper(), 2))
            
            return np.array(X), np.array(y)
        
        except Exception as e:
            logger.error(f"Error preparing regime dataset: {e}")
            return None
    
    def prepare_edge_dataset(self, lookback_days: int = 90) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Prepare dataset for edge model training.
        
        Args:
            lookback_days: Days of data to use
        
        Returns:
            Tuple of (X, y) or None
        """
        # Query trades with outcomes
        query = """
            SELECT features, pnl, pnl_pct
            FROM trades_sandbox
            WHERE timestamp >= NOW() - INTERVAL '%s days'
            AND action_type = 'CLOSE'
            AND pnl IS NOT NULL
            ORDER BY timestamp
        """
        
        try:
            rows = self.db.execute_query(query, (lookback_days,))
            
            if not rows:
                logger.warning("No data found for edge dataset")
                return None
            
            X = []
            y = []
            
            for row in rows:
                # Would need to reconstruct features from trade data
                # This is simplified
                pnl_pct = row.get("pnl_pct", 0)
                is_win = 1 if pnl_pct > 0 else 0
                
                # Placeholder - would extract actual features
                X.append(np.zeros(10))  # Dummy features
                y.append(is_win)
            
            return np.array(X), np.array(y)
        
        except Exception as e:
            logger.error(f"Error preparing edge dataset: {e}")
            return None

