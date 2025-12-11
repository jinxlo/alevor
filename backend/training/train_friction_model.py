"""Train friction prediction model."""

import logging
import pickle
from pathlib import Path
from typing import Optional
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from ..logging_layer.db import Database

logger = logging.getLogger(__name__)


def train_friction_model(
    db: Database,
    output_path: Optional[str] = None,
    test_size: float = 0.2,
    random_state: int = 42
) -> None:
    """Train friction model.
    
    Args:
        db: Database instance
        output_path: Path to save model
        test_size: Test set size fraction
        random_state: Random seed
    """
    logger.info("Preparing friction dataset...")
    
    # Query trades with friction observations
    query = """
        SELECT size, friction, pnl, pair
        FROM trades_sandbox
        WHERE action_type = 'CLOSE'
        AND friction IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 1000
    """
    
    try:
        rows = db.execute_query(query)
        
        if not rows or len(rows) < 100:
            logger.warning("Insufficient data for friction model")
            return
        
        X = []
        y = []
        
        for row in rows:
            # Features: [order_size, liquidity, volatility, base_friction]
            # Would need to fetch liquidity and volatility from other sources
            size = row.get("size", 0)
            base_friction = row.get("friction", 0)
            
            # Placeholder features
            features = np.array([
                size,
                100000.0,  # liquidity placeholder
                0.02,      # volatility placeholder
                base_friction
            ])
            
            X.append(features)
            
            # Target: actual realized friction (would calculate from trade outcome)
            # Simplified - using base friction as target
            y.append(base_friction)
        
        X = np.array(X)
        y = np.array(y)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Train
        logger.info("Training friction model...")
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=random_state
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Test MSE: {mse:.6f}")
        logger.info(f"Test R²: {r2:.4f}")
        
        # Save
        if output_path is None:
            output_path = Path(__file__).parent.parent / "models" / "artifacts" / "friction_model_v1.pkl"
        
        with open(output_path, "wb") as f:
            pickle.dump(model, f)
        
        logger.info(f"Model saved to {output_path}")
    
    except Exception as e:
        logger.error(f"Error training friction model: {e}")


def main():
    """Main entry point."""
    import os
    from ..logging_layer.db import Database
    
    logging.basicConfig(level=logging.INFO)
    
    db = Database(os.getenv("DB_URL"))
    train_friction_model(db)


if __name__ == "__main__":
    main()

