"""ML model inference layer."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def load_models(config_path: str) -> Dict[str, any]:
    """Load all models from configuration.
    
    Args:
        config_path: Path to models.yaml
    
    Returns:
        Dictionary of model instances
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    models = {}
    artifacts_dir = Path(__file__).parent / "artifacts"
    
    for model_name, model_config in config.get("models", {}).items():
        artifact_file = artifacts_dir / model_config["artifact"]
        
        if not artifact_file.exists():
            if model_config.get("optional", False):
                logger.warning(f"Optional model {model_name} not found, skipping")
                continue
            else:
                logger.error(f"Model artifact not found: {artifact_file}")
                continue
        
        # Models are loaded lazily by their respective modules
        models[model_name] = {
            "artifact": str(artifact_file),
            "version": model_config.get("version"),
            "config": model_config
        }
    
    return models
