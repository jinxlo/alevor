#!/bin/bash

# Run live trading engine

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Run live engine
python -m backend.engine_live.main_loop "$@"

