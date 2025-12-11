# Alevor — AI-Driven Trading System

Alevor is an automated trading system that combines machine learning models, on-chain smart contracts, and LLM-powered intelligence to execute profitable trades while managing risk and distributing profits to users.

## Architecture Overview

- **On-Chain Core**: Smart contracts (Vault, Trader, Treasury, LiquidityEngine) handle deposits, trades, and profit distribution
- **Backend Engine**: Python-based ML trading engine with live and sandbox modes
- **Decision Layer**: ML models (regime, edge, friction) + EV calculator for trade decisions
- **LLM Layer**: Multi-agent system for reporting, risk oversight, and explanations

## Quick Start

### Prerequisites

- Python 3.11+
- Foundry (for Solidity contracts)
- PostgreSQL (for logging layer)
- Node.js (optional, for Hardhat alternative)

### Setup

1. **Clone and install dependencies**:
   ```bash
   git clone https://github.com/jinxlo/alevor.git
   cd alevor
   pip install -e .
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your RPC URLs, private keys, DB URL, etc.
   ```

3. **Configure settings**:
   - Edit `config/settings.live.yaml` for live trading
   - Edit `config/settings.sandbox.yaml` for sandbox/testing
   - Edit `config/risk.yaml` for risk parameters
   - Edit `config/pairs.yaml` for tradable pairs

4. **Deploy contracts** (testnet first):
   ```bash
   cd contracts
   forge build
   forge script scripts/Deploy.s.sol --rpc-url <RPC_URL> --broadcast
   ```

5. **Initialize database**:
   ```bash
   ./infra/scripts/migrate_db.sh
   ```

### Running

**Sandbox/Backtest Mode**:
```bash
./infra/scripts/run_sandbox.sh
# or
python -m backend.sandbox.sim_loop
```

**Live Trading Mode**:
```bash
./infra/scripts/run_live.sh
# or
python -m backend.engine_live.main_loop
```

**Training Models**:
```bash
python -m backend.training.train_regime_model
python -m backend.training.train_edge_model
python -m backend.training.train_friction_model
```

**LLM Services**:
```bash
python -m backend.llm_layer.reporting_service  # Generate daily report
python -m backend.llm_layer.oversight_service   # Run risk check
```

## Project Structure

```
alevor/
├── contracts/          # Solidity smart contracts
├── config/             # YAML configuration files
├── backend/            # Python trading engine
│   ├── engine_live/    # Live trading loop
│   ├── sandbox/        # Sandbox/backtest engine
│   ├── data_layer/     # Market data ingestion
│   ├── models/         # ML model inference
│   ├── decision/       # Trade decision logic
│   ├── blockchain/     # Web3 adapters
│   ├── logging_layer/  # DB logging & metrics
│   ├── llm_layer/      # LLM agents & services
│   └── training/       # Model training pipeline
└── infra/              # Docker & deployment scripts
```

## Documentation

- **[AGENT.md](AGENT.md)**: Complete implementation guide and architecture specification
- **Config Files**: See `config/*.yaml` for detailed configuration options

## Key Features

- **Risk Management**: 0.5% risk per trade, 2-5% position size limits, SL/TP enforcement
- **Profit Distribution**: 75% to users, 20% to protocol, 5% to ALV buyback & burn
- **ML-Powered**: Regime classification, edge prediction, friction modeling
- **EV-Based Decisions**: Expected value calculation with slippage and fees
- **LLM Intelligence**: Automated reporting, risk oversight, trade explanations

## Development

See [AGENT.md](AGENT.md) for detailed implementation guidelines, file responsibilities, and coding standards.

## License

[Add your license here]

