"""Full historical backtesting engine."""

import logging
from datetime import datetime
from typing import Dict, Any

from ..sandbox.sim_loop import SandboxEngine

logger = logging.getLogger(__name__)


def run_backtest(
    config_path: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Run full historical backtest.
    
    Args:
        config_path: Path to sandbox config
        start_date: Backtest start date
        end_date: Backtest end date
    
    Returns:
        Backtest results dictionary
    """
    logger.info(f"Starting backtest from {start_date} to {end_date}")
    
    engine = SandboxEngine(config_path)
    
    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    
    results = engine.run_backtest(start_ts, end_ts)
    
    logger.info(f"Backtest completed: {results}")
    return results


def main():
    """Main entry point."""
    from pathlib import Path
    
    logging.basicConfig(level=logging.INFO)
    
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.sandbox.yaml"
    
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)
    
    results = run_backtest(str(config_path), start, end)
    print(f"Backtest results: {results}")


if __name__ == "__main__":
    main()

