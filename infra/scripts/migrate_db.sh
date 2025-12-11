#!/bin/bash

# Run database migrations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Check for DB_URL
if [ -z "$DB_URL" ]; then
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "Error: DB_URL not set and .env file not found"
        exit 1
    fi
fi

# Run schema SQL
SCHEMA_FILE="$PROJECT_ROOT/backend/logging_layer/schemas.sql"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Error: Schema file not found: $SCHEMA_FILE"
    exit 1
fi

psql "$DB_URL" -f "$SCHEMA_FILE"

echo "Database migration completed"

