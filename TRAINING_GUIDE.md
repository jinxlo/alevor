# Training Guide - How to Start Training Models

## Overview

This guide explains how to collect data and train the ML models for the Alevor trading system.

## Prerequisites

1. **Database Setup**
   ```bash
   # Run database migrations
   ./infra/scripts/migrate_db.sh
   ```

2. **Environment Variables**
   ```bash
   # Set in .env file
   DB_URL=postgresql://user:password@localhost:5432/alevor
   BINANCE_API_KEY=your_key_here  # Optional, for higher rate limits
   BINANCE_API_SECRET=your_secret_here  # Optional
   ```

3. **Install Dependencies**
   ```bash
   pip install -e .
   ```

## Step-by-Step Training Process

### Step 1: Collect Historical Data

First, we need to collect historical OHLCV data from Binance to build our training dataset.

```bash
python -m backend.training.data_collector
```

This script will:
- Fetch 90 days of historical data for all configured pairs
- Generate feature vectors for each candle
- Store feature snapshots in the database
- Label regimes (TREND/RANGE/NO_TRADE) using simple heuristics

**Note**: For initial training, you can use simple heuristics. Later, you can refine labels using actual trading outcomes.

### Step 2: Run Backtests (Optional but Recommended)

Before training, run backtests to generate trade outcomes:

```bash
python -m backend.sandbox.sim_loop
```

This will:
- Simulate trades using historical data
- Generate trade outcomes (wins/losses)
- Store results in `trades_sandbox` table

### Step 3: Train Models

Once you have data, train each model:

#### Train Regime Model
```bash
python -m backend.training.train_regime_model
```

This trains a classifier to predict market regime (TREND/RANGE/NO_TRADE).

#### Train Edge Model
```bash
python -m backend.training.train_edge_model
```

This trains a model to predict the probability of a winning trade.

#### Train Friction Model
```bash
python -m backend.training.train_friction_model
```

This trains a model to predict effective friction (slippage + fees).

#### Train Risk Model (Optional)
```bash
python -m backend.training.train_risk_model
```

This is optional and fine-tunes risk parameters.

### Step 4: Evaluate Models

```python
from backend.training.evaluate_models import evaluate_regime_model, evaluate_edge_model
# Use the evaluation functions to compare model performance
```

### Step 5: Deploy Models

Once trained, models are saved to `backend/models/artifacts/`:
- `regime_model_v1.pkl`
- `edge_model_v1.pkl`
- `friction_model_v1.pkl`
- `risk_model_v1.pkl` (optional)

The system will automatically load these when running the trading engine.

## Data Collection Workflow

### Initial Data Collection (Cold Start)

For the first training run, you have two options:

**Option A: Use Binance Historical Data (Recommended)**
```python
from backend.data_layer.binance_feed import BinanceFeed
from backend.training.data_collector import DataCollector
from backend.logging_layer.db import Database

# Initialize
db = Database()
binance = BinanceFeed()
collector = DataCollector(db, binance)

# Collect data
symbols = ["MATIC/USDC", "ETH/USDC"]
collector.collect_historical_data(symbols, days_back=180, interval_seconds=300)
```

**Option B: Use Your Own Data**
- Export CSV files with columns: `timestamp,open,high,low,close,volume`
- Implement CSV loader in `historical_data.py`
- Load and process

### Continuous Data Collection

For live trading, data is collected automatically:
- Each trading decision creates a feature snapshot
- Trade outcomes update the dataset
- Models can be retrained periodically with new data

## Training Tips

1. **Start with More Data**: Collect at least 90-180 days of historical data
2. **Use Multiple Pairs**: Train on diverse market conditions
3. **Validate on Out-of-Sample Data**: Keep 20% of data for validation
4. **Iterate**: Train → Evaluate → Deploy → Collect More Data → Retrain

## Troubleshooting

### "No data found for regime dataset"
- Run `data_collector.py` first to populate the database
- Check database connection
- Verify `features_snapshots` table has data

### "Model artifact not found"
- Train models first using training scripts
- Check `backend/models/artifacts/` directory
- Verify model files are named correctly

### "Binance API rate limit"
- Add API key/secret to `.env` for higher limits
- Reduce number of symbols or days
- Add delays between requests

## Next Steps

After training:
1. Run backtests to validate model performance
2. Deploy to sandbox environment
3. Monitor performance
4. Retrain with new data periodically

