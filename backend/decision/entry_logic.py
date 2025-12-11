"""Entry logic for trade decisions."""

import logging
from typing import Optional, List
import numpy as np

from ..models.edge_model import EdgeModel
from ..models.friction_model import FrictionModel
from ..data_layer.features import FeatureBuilder
from ..data_layer.slippage import calculate_base_friction
from .ev_calculator import EVCalculator
from .sizing import PositionSizer
from .regime_logic import RegimeClassifier
from ..engine_live.actions import OpenPositionAction

logger = logging.getLogger(__name__)


class EntryLogic:
    """Determines when to enter trades."""
    
    def __init__(
        self,
        edge_model: EdgeModel,
        friction_model: FrictionModel,
        regime_classifier: RegimeClassifier,
        ev_calculator: EVCalculator,
        position_sizer: PositionSizer,
        risk_config: dict
    ):
        """Initialize entry logic.
        
        Args:
            edge_model: Edge model instance
            friction_model: Friction model instance
            regime_classifier: Regime classifier instance
            ev_calculator: EV calculator instance
            position_sizer: Position sizer instance
            risk_config: Risk configuration
        """
        self.edge_model = edge_model
        self.friction_model = friction_model
        self.regime_classifier = regime_classifier
        self.ev_calculator = ev_calculator
        self.position_sizer = position_sizer
        self.risk_config = risk_config
        self.feature_builder = FeatureBuilder()
    
    def evaluate_entry(
        self,
        symbol: str,
        price: float,
        ohlcv_df,
        reserves: tuple[float, float],
        capital: float
    ) -> Optional[OpenPositionAction]:
        """Evaluate whether to enter a trade.
        
        Args:
            symbol: Trading pair symbol
            price: Current price
            ohlcv_df: OHLCV DataFrame
            reserves: Tuple of (base_reserve, quote_reserve)
            capital: Available capital (TVL)
        
        Returns:
            OpenPositionAction if entry conditions met, None otherwise
        """
        try:
            # 1. Check regime
            regime = self.regime_classifier.classify_regime(ohlcv_df)
            if not self.regime_classifier.is_tradable(regime):
                logger.debug(f"Regime {regime} not tradable for {symbol}")
                return None
            
            # 2. Build features
            features = self.feature_builder.build_features(ohlcv_df)
            if features is None:
                return None
            
            # 3. Get edge probability
            p = self.edge_model.predict_edge(features)
            
            # 4. Get SL/TP from config
            sl_pct = self.risk_config.get("sl_range", {}).get("default", 0.01)
            tp_pct = self.risk_config.get("tp_range", {}).get("default", 0.04)
            
            # 5. Calculate position size
            position_size = self.position_sizer.calculate_position_size(capital, sl_pct)
            
            # 6. Calculate base friction
            base_friction = calculate_base_friction(
                position_size,
                reserves[0],
                reserves[1],
                fee_bps=30
            )
            
            # 7. Refine friction with ML model
            volatility = np.std(ohlcv_df["close"].pct_change().dropna()) if len(ohlcv_df) > 1 else 0.01
            liquidity = reserves[0] * price + reserves[1]  # Approximate USD liquidity
            friction = self.friction_model.predict_friction(
                position_size,
                liquidity,
                volatility,
                base_friction
            )
            
            # 8. Calculate EV
            ev, debug_info = self.ev_calculator.calculate_ev_from_sl_tp(
                p,
                price,
                sl_pct,
                tp_pct,
                position_size,
                friction
            )
            
            # 9. Check EV threshold
            min_ev = self.risk_config.get("ev", {}).get("min_ev", 0.001)
            if ev < min_ev:
                logger.debug(f"EV {ev} below threshold {min_ev} for {symbol}")
                return None
            
            # 10. Create action
            action = OpenPositionAction(
                pair=symbol,
                size=position_size,
                entry_price=price,
                stop_loss_pct=sl_pct,
                take_profit_pct=tp_pct,
                ev=ev,
                p=p,
                friction=friction,
                regime=regime,
                metadata=debug_info
            )
            
            return action
        
        except Exception as e:
            logger.error(f"Error evaluating entry for {symbol}: {e}")
            return None

