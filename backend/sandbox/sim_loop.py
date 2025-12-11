"""Sandbox simulation loop."""

import logging
import yaml
from pathlib import Path
from datetime import datetime

from .sim_state import SimulatedState
from .sim_executor import SimExecutor
from .sim_feed import SimFeed
from ..data_layer.historical_data import HistoricalDataLoader
from ..data_layer.market_feed import MarketFeed
from ..decision.entry_logic import EntryLogic
from ..decision.exit_logic import ExitLogic
from ..models import load_models
from ..models.regime_model import RegimeModel
from ..models.edge_model import EdgeModel
from ..models.friction_model import FrictionModel
from ..decision.regime_logic import RegimeClassifier
from ..decision.sizing import PositionSizer
from ..decision.ev_calculator import EVCalculator
from ..logging_layer.db import Database
from ..logging_layer.trade_logger import TradeLogger

logger = logging.getLogger(__name__)


class SandboxEngine:
    """Sandbox/backtest trading engine."""
    
    def __init__(self, config_path: str):
        """Initialize sandbox engine.
        
        Args:
            config_path: Path to settings.sandbox.yaml
        """
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize components."""
        # Load configs
        risk_config_path = Path(__file__).parent.parent.parent / "config" / "risk.yaml"
        with open(risk_config_path, "r") as f:
            self.risk_config = yaml.safe_load(f)
        
        pairs_config_path = Path(__file__).parent.parent.parent / "config" / "pairs.yaml"
        with open(pairs_config_path, "r") as f:
            self.pairs_config = yaml.safe_load(f)
        
        models_config_path = Path(__file__).parent.parent.parent / "config" / "models.yaml"
        model_configs = load_models(str(models_config_path))
        
        # Models
        self.regime_model = RegimeModel(model_configs.get("regime_model", {}).get("artifact"))
        self.edge_model = EdgeModel(model_configs.get("edge_model", {}).get("artifact"))
        self.friction_model = FrictionModel(model_configs.get("friction_model", {}).get("artifact"))
        
        # Decision layer
        self.regime_classifier = RegimeClassifier(self.regime_model, self.risk_config)
        self.position_sizer = PositionSizer(self.risk_config)
        self.ev_calculator = EVCalculator()
        
        # Data
        self.historical_loader = HistoricalDataLoader()
        self.sim_feed = SimFeed(self.historical_loader)
        
        # State
        initial_balance = self.config.get("sandbox", {}).get("initial_balance", 100000.0)
        self.state = SimulatedState(initial_balance)
        self.executor = SimExecutor(self.state, apply_slippage=True)
        
        # Logging
        db_url = self.config.get("logging", {}).get("db_url", "postgresql://localhost/alevor")
        self.db = Database(db_url)
        self.trade_logger = TradeLogger(self.db, mode="sandbox")
        
        logger.info("Sandbox engine initialized")
    
    def run_backtest(self, start_ts: int, end_ts: int) -> dict:
        """Run backtest over time period.
        
        Args:
            start_ts: Start timestamp
            end_ts: End timestamp
        
        Returns:
            Backtest results dictionary
        """
        logger.info(f"Starting backtest from {start_ts} to {end_ts}")
        
        # Load historical data for all pairs
        for pair_config in self.pairs_config.get("pairs", []):
            symbol = pair_config["symbol"]
            self.sim_feed.load_historical(symbol, start_ts, end_ts)
        
        # Run simulation (simplified - would iterate over timestamps)
        # This is a placeholder for the actual backtest loop
        
        results = {
            "total_trades": len(self.state.closed_trades),
            "total_pnl": self.state.total_pnl,
            "final_balance": self.state.balance,
            "win_rate": self._calculate_win_rate()
        }
        
        return results
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate from closed trades."""
        if not self.state.closed_trades:
            return 0.0
        
        wins = sum(1 for trade in self.state.closed_trades if trade.get("pnl", 0) > 0)
        return wins / len(self.state.closed_trades)


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.sandbox.yaml"
    engine = SandboxEngine(str(config_path))
    
    # Example backtest
    start = int(datetime(2024, 1, 1).timestamp())
    end = int(datetime(2024, 1, 31).timestamp())
    results = engine.run_backtest(start, end)
    print(f"Backtest results: {results}")


if __name__ == "__main__":
    main()
