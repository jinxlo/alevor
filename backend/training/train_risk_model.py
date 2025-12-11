"""Train optional risk model."""

import logging
import pickle
from pathlib import Path
from typing import Optional
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from ..logging_layer.db import Database

logger = logging.getLogger(__name__)


def train_risk_model(
    db: Database,
    output_path: Optional[str] = None,
    test_size: float = 0.2,
    random_state: int = 42
) -> None:
    """Train risk model for dynamic parameter adjustment.
    
    Args:
        db: Database instance
        output_path: Path to save model
        test_size: Test set size fraction
        random_state: Random seed
    """
    logger.info("Preparing risk dataset...")
    
    # Query trades with outcomes and features
    query = """
        SELECT features, pnl, stop_loss_pct, take_profit_pct
        FROM trades_sandbox
        WHERE action_type = 'CLOSE'
        AND pnl IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 1000
    """
    
    try:
        rows = db.execute_query(query)
        
        if not rows or len(rows) < 100:
            logger.warning("Insufficient data for risk model")
            return
        
        X = []
        y = []
        
        for row in rows:
            # Features would include market conditions
            # Target: optimal SL/TP multipliers based on outcomes
            features = np.zeros(10)  # Placeholder
            X.append(features)
            
            # Target: [sl_mult, tp_mult, risk_mult]
            # Simplified - would calculate optimal multipliers
            y.append([1.0, 1.0, 1.0])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Train
        logger.info("Training risk model...")
        model = RandomForestRegressor(
            n_estimators=50,
            max_depth=5,
            random_state=random_state,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Test MSE: {mse:.4f}")
        logger.info(f"Test R²: {r2:.4f}")
        
        # Save
        if output_path is None:
            output_path = Path(__file__).parent.parent / "models" / "artifacts" / "risk_model_v1.pkl"
        
        with open(output_path, "wb") as f:
            pickle.dump(model, f)
        
        logger.info(f"Model saved to {output_path}")
    
    except Exception as e:
        logger.error(f"Error training risk model: {e}")


def main():
    """Main entry point."""
    import os
    from ..logging_layer.db import Database
    
    logging.basicConfig(level=logging.INFO)
    
    db = Database(os.getenv("DB_URL"))
    train_risk_model(db)


if __name__ == "__main__":
    main()

