# Alevor Backend — AGENT IMPLEMENTATION GUIDE

This document is the **instruction manual for the coding agent** that will generate and maintain the contents of the backend files in this project.

The goal:

> Implement a **clean, testable, production-ready backend** for Alevor’s AI-driven trading system, strictly following this architecture and the rules below.

This spec covers **every file and folder** in the backend project structure.

---

## 1. Global Rules for the Agent

When generating or editing code in this repo, the agent must:

1. **Language & stack**
   - Python 3.11+ for backend.
   - Solidity ^0.8.x for smart contracts.
   - Use Python type hints everywhere.
   - Prefer standard library over extra dependencies unless clearly justified.

2. **Style & Quality**
   - Follow PEP 8.
   - Use `logging` instead of `print`.
   - Add docstrings to public functions and classes.
   - Functions should be small, focused, and testable.

3. **Config & Secrets**
   - Never hardcode secrets or keys.
   - Read runtime configuration from:
     - `.env` (via `os.getenv`)
     - `config/*.yaml`
   - Use **relative imports** inside `backend/`.

4. **Error Handling**
   - Fail fast for unrecoverable issues (raise exceptions).
   - For RPC / HTTP / DB calls:
     - Validate responses.
     - Use clear exception types.
   - Never silently swallow exceptions.

5. **Determinism & Reproducibility**
   - For ML training:
     - Set random seeds where possible.
     - Save artifacts under `backend/models/artifacts/`.
   - For backtesting:
     - Results must be deterministic given same inputs + config.

6. **Trading Logic Separation**
   - All trade decisions must go through:
     - `backend/decision/entry_logic.py`
     - `backend/decision/exit_logic.py`
     - `backend/decision/ev_calculator.py`
     - `backend/decision/sizing.py`
   - No direct trading decision logic in:
     - `blockchain/`
     - `data_layer/`
     - `logging_layer/`
     - `llm_layer/`.

---

## 2. Root-Level Files and Their Purpose

These files define the project metadata, tooling, and environment.

### `README.md`
- High-level documentation of:
  - What Alevor is.
  - How to set up and run the backend.
  - Quickstart commands (sandbox, live).
  - Links to AGENT.MD, docs, and diagrams.
- The agent should keep it:
  - Up-to-date with major architectural changes.
  - Clear for humans (not auto-generated clutter).

### `AGENT.MD`
- This file (the one you’re reading).
- Single source of truth for:
  - Responsibilities of each file.
  - Coding rules and conventions.
- Should be updated if architecture changes.

### `.env.example`
- Template for environment variables:
  - `RPC_URL_LIVE`
  - `RPC_URL_SANDBOX`
  - `DB_URL`
  - `PRIVATE_KEY_TRADER` (example, never real)
  - `OPENAI_API_KEY` (placeholder)
- Agent must:
  - Document required variables.
  - Never put real secrets here.
  - Keep names in sync with actual code.

### `pyproject.toml` / `requirements.txt`
- Python dependency management.
- One of them will be the canonical source; the other may mirror it.
- Should include:
  - core libs (e.g. `pydantic`, `sqlalchemy` or DB driver, `web3`, `numpy`, `pandas`, basic ML libs if needed)
  - testing libs (`pytest`).
- No unnecessary heavy dependencies.

### `foundry.toml` / `hardhat.config.js`
- Smart contract tooling configuration:
  - Networks (Polygon, testnets, local).
  - Compiler settings.
  - Paths for `contracts/src`, `contracts/test`.
- Only Solidity-related logic here.

---

## 3. `contracts/` — On-Chain Core

### `contracts/src/Vault.sol`
- Holds user deposits and issues “shares”.
- Tracks total TVL and total shares.
- Responsible for:
  - `deposit()` and `withdraw()`.
  - Converting between assets and shares.
  - Allowing Trader / Treasury to move funds only as permitted.

### `contracts/src/Trader.sol`
- Receives a **limited amount of capital** from the Vault (2–5% per trade).
- Executes swaps via DEX router (e.g. Uniswap-style).
- Returns principal + profit to Treasury.
- Must enforce:
  - Max capital per trade.
  - Proper authorization (only allowed caller can request trades).

### `contracts/src/Treasury.sol`
- Receives capital + profit from Trader.
- Distributes **profit only**:
  - 75% → Vault (users).
  - 20% → protocol wallet (operational).
  - 5% → LiquidityEngine (ALV buyback & burn).
- Provides functions like:
  - `handleTradeResult(uint256 principal, uint256 profit)`.

### `contracts/src/LiquidityEngine.sol`
- Receives 5% of profit from Treasury.
- Buys ALV tokens on a configured DEX pair.
- Burns the purchased ALV.
- Handles:
  - DEX interaction.
  - `buyAndBurn()` logic.

### `contracts/src/ALVToken.sol`
- ERC20 token implementation:
  - fixed supply (no mint function after deploy).
  - no transfer tax.
  - full supply assigned to deployer or protocol for initial liquidity.
- Conforms to standard ERC20 interface.

### `contracts/src/interfaces/IVault.sol`
- Interface for Vault:
  - `deposit`, `withdraw`, `totalAssets`, `totalShares`, etc.

### `contracts/src/interfaces/ITrader.sol`
- Interface for Trader:
  - `executeTrade`, `closeTrade`, or suitable functions as design defines.

### `contracts/src/interfaces/ITreasury.sol`
- Interface describing the Treasury’s external functions (profit handling).

### `contracts/src/interfaces/ILiquidityEngine.sol`
- Interface exposing `buyAndBurn()` or similar functions.

### `contracts/test/`
- Contains unit and integration tests for Solidity contracts.
- Files may be:
  - `Vault.t.sol`
  - `Trader.t.sol`
  - `Treasury.t.sol`
  - `LiquidityEngine.t.sol`
  - `ALVToken.t.sol`
- Use Foundry (or relevant framework) to:
  - validate invariants.
  - check authorization.
  - simulate trade flows: deposit → trade → profit → distribution.

### `contracts/scripts/`
- Deployment and utility scripts:
  - `Deploy.s.sol` (Foundry) or equivalent.
  - Scripts to:
    - deploy contracts on testnet.
    - verify on block explorers.
    - wire dependencies (set Vault address in Trader, etc.).

---

## 4. `config/` — All Settings

### `config/settings.live.yaml`
- Live network configuration:
  - `rpc_url`
  - `chain_id`
  - `vault_address`
  - `trader_address`
  - `treasury_address`
  - `liquidity_engine_address`
- `mode: "live"`.

### `config/settings.sandbox.yaml`
- Sandbox/test configuration:
  - testnet or local RPC
  - test contract addresses
  - `mode: "sandbox"`.

### `config/risk.yaml`
Defines risk and exposure parameters:
- `max_risk_per_trade` (e.g. 0.005 = 0.5%).
- `position_size_min_pct`, `position_size_max_pct` (2–5%).
- `sl_range` (1–1.5%).
- `tp_range` (3–5%).
- per-pair or global constraints.
- EV thresholds (e.g. `min_ev`).

### `config/pairs.yaml`
- List of tradable pairs:
  - symbol (e.g. `MATIC/USDC`)
  - DEX pool address
  - fee tier
  - min liquidity thresholds.

### `config/models.yaml`
- Maps logical model names to artifacts:
  - `regime_model: regime_model_v1.pkl`
  - `edge_model: edge_model_v1.pkl`
  - `risk_model: risk_model_v1.pkl`
  - `friction_model: friction_model_v1.pkl`.

### `config/llm.yaml`
- LLM config:
  - provider name (e.g. `openai`)
  - model IDs for reporting, risk, explainer
  - default temperature, max tokens
  - routes for specific tasks.

---

## 5. `backend/` — Full Trading + AI Engine

### 5.1 `backend/engine_live/`

#### `backend/engine_live/__init__.py`
- Standard package initializer.
- May export:
  - `run_live_loop()` convenience function.

#### `backend/engine_live/main_loop.py`
- Orchestration of the live trading loop.
- Responsibilities:
  - Load config + models.
  - Pull market data and on-chain state.
  - Call decision layer (`entry_logic`, `exit_logic`).
  - Call blockchain APIs (`vault_api`, `trader_api`) to execute trades.
  - Use `logging_layer` to log actions and results.

#### `backend/engine_live/scheduler.py`
- Time control:
  - loop every N seconds/minutes.
  - can be a simple `while True` with `sleep`.
- Should support:
  - graceful shutdown.
  - configuration of frequency.

#### `backend/engine_live/state.py`
- In-memory process state:
  - open positions (mirroring DB/on-chain).
  - per-pair cooldown timers.
  - trades per day/session.
- Does **not** decide trades, only tracks them.

#### `backend/engine_live/actions.py`
- Data classes / types for:
  - `OpenPositionAction`
  - `ClosePositionAction`
- Contains:
  - pair
  - size
  - SL
  - TP
  - metadata (EV, p, etc.).
- No logic; purely data representation.

#### `backend/engine_live/exits.py`
- Uses:
  - `onchain_state`
  - market prices
  - position data
- Decides when:
  - SL is hit.
  - TP is hit.
  - time-based exits or regime change exit applies.
- Returns `ClosePositionAction` objects.

---

### 5.2 `backend/sandbox/`

#### `backend/sandbox/__init__.py`
- Standard package initializer.

#### `backend/sandbox/sim_loop.py`
- Drives sandbox or backtest run:
  - iterates over historical candles.
  - uses same decision logic as live engine.
  - but executes in `sim_executor` rather than on-chain.

#### `backend/sandbox/sim_state.py`
- Tracks:
  - simulated balance.
  - simulated positions.
  - simulated PnL.

#### `backend/sandbox/sim_actions.py`
- Equivalent to `engine_live/actions.py`, but:
  - may include additional fields for simulation diagnostics.

#### `backend/sandbox/sim_executor.py`
- Applies open/close actions to simulated portfolio using:
  - historical prices.
  - slippage model.
- Computes PnL for each closed trade.

#### `backend/sandbox/sim_feed.py`
- Supplies:
  - historical OHLCV windows for each step.
- May also:
  - simulate latency and slippage if needed.

---

### 5.3 `backend/data_layer/`

#### `backend/data_layer/__init__.py`
- Package initializer.

#### `backend/data_layer/market_feed.py`
- Functions/classes to fetch:
  - current price for each pair.
  - pool reserves from the DEX.
- For sandbox/live:
  - uses RPC or external APIs as configured.

#### `backend/data_layer/historical_data.py`
- Loading historical OHLCV:
  - from CSV, Parquet, DB, or external API.
- Provides:
  - time-aligned windows for ML and backtests.

#### `backend/data_layer/onchain_state.py`
- Uses `web3_client` and `contracts` to read:
  - vault TVL.
  - total shares.
  - other relevant on-chain data (if needed).

#### `backend/data_layer/features.py`
- Builds feature vectors from:
  - price history.
  - volatility metrics.
  - momentum indicators.
  - regime indicators.
- Output:
  - numpy arrays / pandas data structures ready for ML models.

#### `backend/data_layer/slippage.py`
- Deterministic calculation of:
  - expected slippage for given order size and pool reserves.
  - DEX trading fees.
- Output:
  - base friction estimate `F_base`.

#### `backend/data_layer/utils_time.py`
- Time utilities:
  - conversions between timestamps.
  - aligning bars/candles.
  - day/week boundaries.

---

### 5.4 `backend/models/`

#### `backend/models/__init__.py`
- Package initializer.
- May expose helpers like:
  - `load_models(config)`.

#### `backend/models/regime_model.py`
- Loads regime model artifact.
- Public function:
  - `predict_regime(features) -> str`
    - returns `"TREND"`, `"RANGE"`, or `"NO_TRADE"`.

#### `backend/models/edge_model.py`
- Loads edge model artifact.
- Public function:
  - `predict_edge(features) -> float`
    - probability `p` of a winning trade (0–1).

#### `backend/models/risk_model.py`
- Optional dynamic risk model.
- Public function:
  - `suggest_risk_params(features) -> RiskParams`
    - may suggest SL/TP multipliers or fine adjustments.

#### `backend/models/friction_model.py`
- ML model to refine friction F.
- Inputs:
  - order size
  - pair liquidity
  - volatility
  - base friction from `slippage.py`
- Public function:
  - `predict_friction(context) -> float`.

#### `backend/models/artifacts/`
- Contains:
  - `regime_model_v1.pkl`
  - `edge_model_v1.pkl`
  - `risk_model_v1.pkl`
  - `friction_model_v1.pkl`
- Agent:
  - never edits these manually.
  - only via training scripts.

---

### 5.5 `backend/decision/`

#### `backend/decision/__init__.py`
- Package initializer.

#### `backend/decision/regime_logic.py`
- Combines:
  - `regime_model` outputs.
  - volatility and liquidity measures.
- Decides whether:
  - pair is tradable currently.
  - should be in `"NO_TRADE"` mode.

#### `backend/decision/entry_logic.py`
- For each pair:
  - builds features.
  - obtains `p` from `edge_model`.
  - calls `ev_calculator`.
  - checks risk constraints (from `risk.yaml` and `sizing.py`).
- If conditions are met:
  - returns one or more `OpenPositionAction`.

#### `backend/decision/exit_logic.py`
- Logic to:
  - combine info from `exits.py`, `onchain_state`, and prices.
- Decides when to:
  - close positions proactively.
- Returns `ClosePositionAction`.

#### `backend/decision/sizing.py`
- Implements:
  ```text
  position_size = (capital * risk_per_trade) / stop_loss_pct
````

* Enforces:

  * risk per trade ≤ 0.5% TVL.
  * position size between 2–5% TVL.
* No IO, no network calls.

#### `backend/decision/ev_calculator.py`

* Computes:

  ```text
  EV = (p * W) - ((1 - p) * L) - F
  ```
* `W` and `L` derived from SL/TP parameters.
* `F` is:

  * base friction from `slippage.py`
  * plus adjustment from `friction_model.py`.
* Returns numeric EV and optionally debug info.

---

### 5.6 `backend/blockchain/`

#### `backend/blockchain/__init__.py`

* Package initializer.

#### `backend/blockchain/web3_client.py`

* Creates and manages web3 client:

  * network RPC from `settings.*.yaml`.
  * account from private key (via `.env`).
* Provides:

  * basic send transaction / call helpers.

#### `backend/blockchain/contracts.py`

* Loads ABIs and contract addresses.
* Returns contract instances for:

  * Vault
  * Trader
  * Treasury
  * LiquidityEngine.

#### `backend/blockchain/vault_api.py`

* Wrapper around Vault contract.
* Methods:

  * `get_tvl()`
  * `get_total_shares()`
  * `deposit()`, `withdraw()` if needed.

#### `backend/blockchain/trader_api.py`

* Wrapper around Trader contract.
* Methods:

  * `open_position(pair, amount, sl, tp)`
  * `close_position(position_id)` (or equivalent logic).

---

### 5.7 `backend/logging_layer/`

#### `backend/logging_layer/__init__.py`

* Package initializer.

#### `backend/logging_layer/db.py`

* DB connection management:

  * connect using `DB_URL` from env/config.
  * handle pooling (if needed).

#### `backend/logging_layer/schemas.sql`

* SQL schema definitions:

  * `trades_live`
  * `trades_sandbox`
  * `features_snapshots`
  * `risk_metrics`
  * `daily_stats` or similar.
* Agent should keep this in sync with actual usage.

#### `backend/logging_layer/trade_logger.py`

* APIs to log:

  * each decision (entry, exit).
  * context: p, W, L, F, EV, SL, TP.
  * realized PnL after close.

#### `backend/logging_layer/pnl_calculator.py`

* Computes:

  * per-trade PnL given entry/exit prices and sizes.
  * aggregated PnL for a period.

#### `backend/logging_layer/metrics.py`

* Higher-level metrics:

  * per-pair win rate.
  * per-regime performance.
  * drawdowns.
  * volatility of returns.

---

### 5.8 `backend/llm_layer/`

#### `backend/llm_layer/__init__.py`

* Package initializer.

#### `backend/llm_layer/prompts/reporting_prompt.md`

* Prompt template for reporting agent:

  * describes style and structure of daily/weekly reports.

#### `backend/llm_layer/prompts/risk_prompt.md`

* Prompt template for risk agent:

  * focuses on anomalies, drawdowns, risk limit violations.

#### `backend/llm_layer/prompts/explainer_prompt.md`

* Prompt template for explainer agent:

  * explains trades and strategy behavior to non-technical users.

#### `backend/llm_layer/agents/reporting_agent.py`

* Reads:

  * logs + metrics.
* Produces:

  * natural language reports using LLM.

#### `backend/llm_layer/agents/risk_agent.py`

* Reads:

  * risk metrics, drawdowns, unusual PnL patterns.
* Produces:

  * alerts and summaries.

#### `backend/llm_layer/agents/explainer_agent.py`

* Given:

  * specific trades or time windows.
* Produces:

  * simple-language explanations and Q&A style outputs.

#### `backend/llm_layer/agents/research_agent.py`

* Optionally:

  * summarizes external market context (if data is provided).
* Not required for core trading; complementary.

#### `backend/llm_layer/router.py`

* Simple dispatcher:

  * routes tasks to `reporting_agent`, `risk_agent`, `explainer_agent`, etc.

#### `backend/llm_layer/reporting_service.py`

* Exposes functions:

  * `generate_daily_report()`
  * `generate_weekly_report()`
* Intended to be callable from CLI, cron, or future API.

#### `backend/llm_layer/oversight_service.py`

* Exposes functions:

  * `run_risk_check()`
  * `summarize_risk_state()`

#### `backend/llm_layer/api_adapter.py`

* Wrapper around LLM API:

  * loads API key from env.
  * handles retries, timeouts.
  * centralizes LLM calls.

---

### 5.9 `backend/training/`

#### `backend/training/__init__.py`

* Package initializer.

#### `backend/training/prepare_dataset.py`

* Reads:

  * `logging_layer` DB or raw OHLCV.
* Produces:

  * training datasets:

    * regime labels.
    * trade outcomes for edge model.
    * friction observations (expected vs realized).

#### `backend/training/train_regime_model.py`

* Trains the regime classifier.
* Saves:

  * `regime_model_v1.pkl`.

#### `backend/training/train_edge_model.py`

* Trains the edge model (probability p of success).
* Saves:

  * `edge_model_v1.pkl`.

#### `backend/training/train_risk_model.py`

* (Optional) trains risk model for fine-tuning SL/TP or exposure.
* Saves:

  * `risk_model_v1.pkl`.

#### `backend/training/train_friction_model.py`

* Trains friction model:

  * predicting real F from order size, liquidity, volatility.
* Saves:

  * `friction_model_v1.pkl`.

#### `backend/training/evaluate_models.py`

* Compares:

  * new vs old models on validation sets.
* Criteria:

  * EV improvement.
  * stability.
  * robustness.

#### `backend/training/backtest.py`

* Runs full backtests:

  * uses `sandbox` + models + decision layer.
* Outputs:

  * backtest metrics (may write to DB or files).

---

## 6. `infra/` — Infrastructure

### `infra/docker-compose.yml`

* Defines services:

  * `db`: Postgres container.
  * `backend`: Python backend service.
  * optional LLM proxy if needed.
* Configures networks and volumes.

### `infra/Dockerfile.backend`

* Builds backend runtime:

  * installs Python dependencies.
  * copies `backend/`, `config/`, and root files needed.
* Sets:

  * working directory.
  * default command (can be overridden).

### `infra/scripts/run_sandbox.sh`

* Shell script:

  * activates environment (if needed).
  * runs sandbox/backtest entrypoint.
  * e.g.: `python -m backend.sandbox.sim_loop` or `backtest.py`.

### `infra/scripts/run_live.sh`

* Shell script:

  * activates environment.
  * runs live engine loop.
  * e.g.: `python -m backend.engine_live.main_loop`.

### `infra/scripts/migrate_db.sh`

* Shell script:

  * applies `schemas.sql` to target DB.
  * can be used on first run or upgrades.

---

## 7. How to Use This Spec

When asking the agent for code:

1. Always specify:

   * exact file path (e.g. `backend/data_layer/slippage.py`)
   * what you want (initial implementation, refactor, tests, etc.).

2. The agent must:

   * follow the responsibilities listed here.
   * keep each file focused on its role.
   * avoid leaking logic across layers.

This AGENT.MD should be **kept in sync** whenever:

* new files are added, or
* responsibilities change.

It is the **authoritative blueprint** for the Alevor backend.

```

---

This version now explicitly covers **every single file and folder** in the current backend project structure:

- Root files  
- All `contracts/*` (including `test` and `scripts`)  
- All `config/*`  
- All `backend/*` submodules and their files  
- All `infra/*` scripts and configs  

```
