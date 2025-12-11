"""Main trading loop for live engine."""

import logging
import os
import yaml
from pathlib import Path

from .scheduler import TradingScheduler
from .state import EngineState
from .exits import ExitDetector
from ..data_layer.market_feed import MarketFeed
from ..data_layer.onchain_state import OnChainState
from ..data_layer.historical_data import HistoricalDataLoader
from ..decision.entry_logic import EntryLogic
from ..decision.exit_logic import ExitLogic
from ..blockchain.web3_client import Web3Client
from ..blockchain.contracts import ContractLoader
from ..blockchain.vault_api import VaultAPI
from ..blockchain.trader_api import TraderAPI
from ..models import load_models
from ..models.regime_model import RegimeModel
from ..models.edge_model import EdgeModel
from ..models.friction_model import FrictionModel
from ..models.risk_model import RiskModel
from ..decision.regime_logic import RegimeClassifier
from ..decision.sizing import PositionSizer
from ..decision.ev_calculator import EVCalculator
from ..logging_layer.db import Database
from ..logging_layer.trade_logger import TradeLogger

logger = logging.getLogger(__name__)


class LiveTradingEngine:
    """Main live trading engine."""
    
    def __init__(self, config_path: str):
        """Initialize live trading engine.
        
        Args:
            config_path: Path to settings.live.yaml
        """
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize all engine components."""
        # Web3 and contracts
        rpc_url = os.path.expandvars(self.config["rpc"]["url"])
        private_key = os.path.expandvars(self.config["wallet"]["trader_key"])
        
        self.web3_client = Web3Client(rpc_url, private_key)
        self.contract_loader = ContractLoader(self.web3_client)
        
        # Load contracts
        contract_addresses = {
            "Vault": self.config["contracts"]["vault"],
            "Trader": self.config["contracts"]["trader"],
            "Treasury": self.config["contracts"]["treasury"]
        }
        contracts = self.contract_loader.load_contracts(contract_addresses)
        
        self.vault_api = VaultAPI(contracts["vault"], self.web3_client)
        self.trader_api = TraderAPI(contracts["trader"], self.web3_client)
        
        # Data layer
        pairs_config_path = Path(__file__).parent.parent.parent / "config" / "pairs.yaml"
        with open(pairs_config_path, "r") as f:
            pairs_config = yaml.safe_load(f)
        
        self.market_feed = MarketFeed(self.web3_client, pairs_config)
        self.onchain_state = OnChainState(self.web3_client, contracts)
        self.historical_loader = HistoricalDataLoader()
        
        # Load models
        models_config_path = Path(__file__).parent.parent.parent / "config" / "models.yaml"
        model_configs = load_models(str(models_config_path))
        
        self.regime_model = RegimeModel(model_configs.get("regime_model", {}).get("artifact"))
        self.edge_model = EdgeModel(model_configs.get("edge_model", {}).get("artifact"))
        self.friction_model = FrictionModel(model_configs.get("friction_model", {}).get("artifact"))
        self.risk_model = RiskModel(model_configs.get("risk_model", {}).get("artifact"))
        
        # Load risk config
        risk_config_path = Path(__file__).parent.parent.parent / "config" / "risk.yaml"
        with open(risk_config_path, "r") as f:
            self.risk_config = yaml.safe_load(f)
        
        # Decision layer
        self.regime_classifier = RegimeClassifier(self.regime_model, self.risk_config)
        self.position_sizer = PositionSizer(self.risk_config)
        self.ev_calculator = EVCalculator()
        
        self.entry_logic = EntryLogic(
            self.edge_model,
            self.friction_model,
            self.regime_classifier,
            self.ev_calculator,
            self.position_sizer,
            self.risk_config
        )
        
        self.exit_logic = ExitLogic(self.risk_config)
        
        # State and exits
        self.state = EngineState()
        self.exit_detector = ExitDetector(self.state)
        
        # Logging
        db_url = os.path.expandvars(self.config["logging"]["db_url"])
        self.db = Database(db_url)
        self.trade_logger = TradeLogger(self.db, mode="live")
        
        logger.info("Live trading engine initialized")
    
    def run_iteration(self) -> None:
        """Run one iteration of the trading loop."""
        try:
            # 1. Get current market data
            tvl = self.onchain_state.get_tvl()
            if tvl is None or tvl <= 0:
                logger.warning("TVL is zero or unavailable, skipping iteration")
                return
            
            # 2. Check exits for open positions
            current_prices = {}
            for pair_config in self.market_feed.pairs:
                symbol = pair_config["symbol"]
                price = self.market_feed.get_price(symbol)
                if price:
                    current_prices[symbol] = price
            
            exit_actions = self.exit_detector.check_all_exits(current_prices)
            for action in exit_actions:
                self._execute_close(action)
            
            # 3. Evaluate entries for enabled pairs
            for pair_config in self.market_feed.pairs:
                if not pair_config.get("enabled", True):
                    continue
                
                symbol = pair_config["symbol"]
                
                # Check cooldown
                cooldown = self.risk_config.get("cooldowns", {}).get("per_pair", 3600)
                if self.state.is_in_cooldown(symbol, cooldown):
                    continue
                
                # Get historical data
                # (Simplified - would fetch actual historical data)
                # For now, skip entry evaluation
                # entry_action = self.entry_logic.evaluate_entry(...)
                # if entry_action:
                #     self._execute_open(entry_action)
        
        except Exception as e:
            logger.error(f"Error in trading loop iteration: {e}", exc_info=True)
    
    def _execute_open(self, action) -> None:
        """Execute open position action."""
        # Implementation would call trader_api and log
        logger.info(f"Would open position: {action}")
    
    def _execute_close(self, action) -> None:
        """Execute close position action."""
        # Implementation would call trader_api and log
        logger.info(f"Would close position: {action}")
    
    def run(self, interval_seconds: int = 60) -> None:
        """Run the trading engine.
        
        Args:
            interval_seconds: Loop interval
        """
        scheduler = TradingScheduler(interval_seconds)
        scheduler.run_loop(self.run_iteration)


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.live.yaml"
    engine = LiveTradingEngine(str(config_path))
    engine.run(interval_seconds=60)


if __name__ == "__main__":
    main()
