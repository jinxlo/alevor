"""Train edge prediction model."""

import logging
import pickle
from pathlib import Path
from typing import Optional
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

from .prepare_dataset import DatasetPreparer
from ..logging_layer.db import Database

logger = logging.getLogger(__name__)


def train_edge_model(
    db: Database,
    output_path: Optional[str] = None,
    test_size: float = 0.2,
    random_state: int = 42
) -> None:
    """Train edge prediction model.
    
    Args:
        db: Database instance
        output_path: Path to save model
        test_size: Test set size fraction
        random_state: Random seed
    """
    logger.info("Preparing edge dataset...")
    preparer = DatasetPreparer(db)
    data = preparer.prepare_edge_dataset()
    
    if data is None:
        logger.error("Failed to prepare dataset")
        return
    
    X, y = data
    
    logger.info(f"Dataset shape: {X.shape}, positive class: {np.sum(y)}/{len(y)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Train model
    logger.info("Training edge model...")
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=random_state
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    logger.info(f"Test accuracy: {accuracy:.4f}")
    logger.info(f"Test AUC: {auc:.4f}")
    
    # Save model
    if output_path is None:
        output_path = Path(__file__).parent.parent / "models" / "artifacts" / "edge_model_v1.pkl"
    
    with open(output_path, "wb") as f:
        pickle.dump(model, f)
    
    logger.info(f"Model saved to {output_path}")


def main():
    """Main entry point."""
    import os
    from ..logging_layer.db import Database
    
    logging.basicConfig(level=logging.INFO)
    
    db = Database(os.getenv("DB_URL"))
    train_edge_model(db)


if __name__ == "__main__":
    main()

