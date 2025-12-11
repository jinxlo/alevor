"""Trade logging to database."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from .db import Database

logger = logging.getLogger(__name__)


class TradeLogger:
    """Logs trades and decisions to database."""
    
    def __init__(self, db: Database, mode: str = "live"):
        """Initialize trade logger.
        
        Args:
            db: Database instance
            mode: "live" or "sandbox"
        """
        self.db = db
        self.mode = mode
        self.table = "trades_live" if mode == "live" else "trades_sandbox"
    
    def log_open(
        self,
        pair: str,
        size: float,
        entry_price: float,
        stop_loss_pct: float,
        take_profit_pct: float,
        p: float,
        ev: float,
        friction: float,
        regime: str,
        tx_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """Log an open position.
        
        Args:
            pair: Trading pair
            size: Position size
            entry_price: Entry price
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
            p: Edge probability
            ev: Expected value
            friction: Friction value
            regime: Market regime
            tx_hash: Transaction hash (for live)
            metadata: Additional metadata
        
        Returns:
            Trade ID or None
        """
        query = f"""
            INSERT INTO {self.table} 
            (pair, action_type, entry_price, size, stop_loss_pct, take_profit_pct, 
             p, ev, friction, regime, tx_hash, metadata)
            VALUES (%s, 'OPEN', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        try:
            result = self.db.execute_query(
                query,
                (pair, entry_price, size, stop_loss_pct, take_profit_pct, 
                 p, ev, friction, regime, tx_hash, metadata)
            )
            if result:
                trade_id = result[0]["id"]
                logger.info(f"Logged open trade {trade_id} for {pair}")
                return trade_id
        except Exception as e:
            logger.error(f"Error logging open trade: {e}")
        
        return None
    
    def log_close(
        self,
        trade_id: int,
        exit_price: float,
        pnl: float,
        pnl_pct: float,
        reason: str,
        tx_hash: Optional[str] = None
    ) -> bool:
        """Log a closed position.
        
        Args:
            trade_id: Trade ID from log_open
            exit_price: Exit price
            pnl: Profit/loss
            pnl_pct: PnL as percentage
            reason: Close reason (STOP_LOSS, TAKE_PROFIT, etc.)
            tx_hash: Transaction hash (for live)
        
        Returns:
            True if successful
        """
        query = f"""
            UPDATE {self.table}
            SET action_type = 'CLOSE',
                exit_price = %s,
                pnl = %s,
                pnl_pct = %s,
                tx_hash = COALESCE(tx_hash, %s),
                metadata = COALESCE(metadata, '{{}}'::jsonb) || %s::jsonb
            WHERE id = %s
        """
        
        metadata = {"close_reason": reason}
        
        try:
            rows = self.db.execute_update(
                query,
                (exit_price, pnl, pnl_pct, tx_hash, metadata, trade_id)
            )
            if rows > 0:
                logger.info(f"Logged close for trade {trade_id}, PnL: {pnl}")
                return True
        except Exception as e:
            logger.error(f"Error logging close: {e}")
        
        return False
    
    def log_decision(
        self,
        pair: str,
        features: Dict[str, Any],
        regime: str,
        outcome: Optional[float] = None
    ) -> Optional[int]:
        """Log a decision snapshot (for ML training).
        
        Args:
            pair: Trading pair
            features: Feature vector
            regime: Market regime
            outcome: Actual outcome (PnL) if available
        
        Returns:
            Snapshot ID or None
        """
        query = """
            INSERT INTO features_snapshots 
            (timestamp, pair, features, regime, outcome)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        
        try:
            result = self.db.execute_query(
                query,
                (datetime.now(), pair, features, regime, outcome)
            )
            if result:
                return result[0]["id"]
        except Exception as e:
            logger.error(f"Error logging decision snapshot: {e}")
        
        return None

