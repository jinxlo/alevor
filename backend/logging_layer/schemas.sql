-- Database schema for Alevor trading system

-- Trades table (live trading)
CREATE TABLE IF NOT EXISTS trades_live (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pair VARCHAR(50) NOT NULL,
    action_type VARCHAR(20) NOT NULL, -- 'OPEN' or 'CLOSE'
    entry_price DECIMAL(20, 8),
    exit_price DECIMAL(20, 8),
    size DECIMAL(20, 8) NOT NULL,
    stop_loss_pct DECIMAL(10, 6),
    take_profit_pct DECIMAL(10, 6),
    p DECIMAL(10, 6), -- Edge probability
    ev DECIMAL(20, 8), -- Expected value
    friction DECIMAL(10, 6),
    regime VARCHAR(20),
    pnl DECIMAL(20, 8),
    pnl_pct DECIMAL(10, 6),
    tx_hash VARCHAR(66),
    metadata JSONB
);

-- Trades table (sandbox/backtest)
CREATE TABLE IF NOT EXISTS trades_sandbox (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    pair VARCHAR(50) NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    entry_price DECIMAL(20, 8),
    exit_price DECIMAL(20, 8),
    size DECIMAL(20, 8) NOT NULL,
    stop_loss_pct DECIMAL(10, 6),
    take_profit_pct DECIMAL(10, 6),
    p DECIMAL(10, 6),
    ev DECIMAL(20, 8),
    friction DECIMAL(10, 6),
    regime VARCHAR(20),
    pnl DECIMAL(20, 8),
    pnl_pct DECIMAL(10, 6),
    metadata JSONB
);

-- Feature snapshots (for ML training)
CREATE TABLE IF NOT EXISTS features_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    pair VARCHAR(50) NOT NULL,
    features JSONB NOT NULL,
    regime VARCHAR(20),
    outcome DECIMAL(20, 8), -- Actual PnL for this snapshot
    metadata JSONB
);

-- Risk metrics
CREATE TABLE IF NOT EXISTS risk_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tvl DECIMAL(20, 8),
    open_positions_count INTEGER,
    total_exposure DECIMAL(20, 8),
    max_drawdown DECIMAL(10, 6),
    daily_pnl DECIMAL(20, 8),
    daily_trades INTEGER,
    metadata JSONB
);

-- Daily statistics
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_pnl DECIMAL(20, 8) DEFAULT 0,
    total_pnl_pct DECIMAL(10, 6) DEFAULT 0,
    win_rate DECIMAL(10, 6),
    avg_win DECIMAL(20, 8),
    avg_loss DECIMAL(20, 8),
    sharpe_ratio DECIMAL(10, 6),
    max_drawdown DECIMAL(10, 6),
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trades_live_timestamp ON trades_live(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_live_pair ON trades_live(pair);
CREATE INDEX IF NOT EXISTS idx_trades_sandbox_timestamp ON trades_sandbox(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_sandbox_pair ON trades_sandbox(pair);
CREATE INDEX IF NOT EXISTS idx_features_snapshots_timestamp ON features_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_features_snapshots_pair ON features_snapshots(pair);
CREATE INDEX IF NOT EXISTS idx_risk_metrics_timestamp ON risk_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);

