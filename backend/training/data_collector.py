"""Data collection script for training data preparation."""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from ..data_layer.binance_feed import BinanceFeed
from ..data_layer.historical_data import HistoricalDataLoader
from ..data_layer.features import FeatureBuilder
from ..data_layer.onchain_state import OnChainState
from ..logging_layer.db import Database
from ..logging_layer.trade_logger import TradeLogger

logger = logging.getLogger(__name__)


class DataCollector:
    """Collects historical data and prepares it for training."""
    
    def __init__(self, db: Database, binance_feed: BinanceFeed):
        """Initialize data collector.
        
        Args:
            db: Database instance
            binance_feed: Binance feed instance
        """
        self.db = db
        self.binance_feed = binance_feed
        self.historical_loader = HistoricalDataLoader(data_source="binance", binance_feed=binance_feed)
        self.feature_builder = FeatureBuilder()
        self.trade_logger = TradeLogger(db, mode="sandbox")
    
    def collect_historical_data(
        self,
        symbols: list[str],
        days_back: int = 90,
        interval_seconds: int = 300
    ) -> None:
        """Collect historical OHLCV data and store feature snapshots.
        
        Args:
            symbols: List of trading pair symbols
            days_back: Number of days to collect
            interval_seconds: Candle interval
        """
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days_back)).timestamp())
        
        logger.info(f"Collecting {days_back} days of data for {len(symbols)} symbols")
        
        for symbol in symbols:
            logger.info(f"Collecting data for {symbol}...")
            
            # Load OHLCV data
            df = self.historical_loader.load_ohlcv(
                symbol, start_time, end_time, interval_seconds
            )
            
            if df is None or df.empty:
                logger.warning(f"No data for {symbol}")
                continue
            
            # Process each candle to create feature snapshots
            for idx in range(50, len(df)):  # Start after enough history for indicators
                window_df = df.iloc[:idx+1]
                
                # Build features
                features = self.feature_builder.build_features(window_df)
                if features is None:
                    continue
                
                # Determine regime (simplified - would use actual regime model)
                # For now, use simple heuristic
                returns = window_df["close"].pct_change().dropna()
                volatility = returns.std()
                
                if volatility > 0.03:
                    regime = "NO_TRADE"
                elif abs(returns.iloc[-1]) > 0.02:
                    regime = "TREND"
                else:
                    regime = "RANGE"
                
                # Store feature snapshot
                features_dict = {f"feature_{i}": float(f) for i, f in enumerate(features)}
                
                self.trade_logger.log_decision(
                    pair=symbol,
                    features=features_dict,
                    regime=regime,
                    outcome=None  # Will be filled when we have trade outcomes
                )
            
            logger.info(f"Collected {len(df)} candles for {symbol}")


def main():
    """Main entry point for data collection."""
    import os
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize
    db = Database(os.getenv("DB_URL", "postgresql://localhost/alevor"))
    binance_feed = BinanceFeed()  # No API key needed for public endpoints
    
    collector = DataCollector(db, binance_feed)
    
    # Collect data for configured pairs
    config_path = Path(__file__).parent.parent.parent / "config" / "pairs.yaml"
    with open(config_path, "r") as f:
        pairs_config = yaml.safe_load(f)
    
    symbols = [pair["symbol"] for pair in pairs_config.get("pairs", [])]
    
    # Collect 90 days of historical data
    collector.collect_historical_data(symbols, days_back=90, interval_seconds=300)
    
    logger.info("Data collection complete!")


if __name__ == "__main__":
    main()

