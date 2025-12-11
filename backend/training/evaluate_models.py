"""Model evaluation utilities."""

import logging
from typing import Dict, Any
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

logger = logging.getLogger(__name__)


def evaluate_regime_model(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
    """Evaluate regime model.
    
    Args:
        model: Trained regime model
        X_test: Test features
        y_test: Test labels
    
    Returns:
        Evaluation metrics dictionary
    """
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    report = classification_report(y_test, y_pred, output_dict=True)
    
    return {
        "accuracy": accuracy,
        "classification_report": report
    }


def evaluate_edge_model(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
    """Evaluate edge model.
    
    Args:
        model: Trained edge model
        X_test: Test features
        y_test: Test labels
    
    Returns:
        Evaluation metrics dictionary
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    return {
        "accuracy": accuracy,
        "auc": auc
    }


def compare_models(old_model, new_model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
    """Compare old and new models.
    
    Args:
        old_model: Old model instance
        new_model: New model instance
        X_test: Test features
        y_test: Test labels
    
    Returns:
        Comparison results
    """
    old_pred = old_model.predict(X_test)
    new_pred = new_model.predict(X_test)
    
    old_acc = accuracy_score(y_test, old_pred)
    new_acc = accuracy_score(y_test, new_pred)
    
    improvement = new_acc - old_acc
    
    return {
        "old_accuracy": old_acc,
        "new_accuracy": new_acc,
        "improvement": improvement,
        "improved": improvement > 0
    }

