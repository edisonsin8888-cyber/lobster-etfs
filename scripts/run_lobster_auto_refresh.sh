#!/bin/bash

PROJECT_DIR="/Users/benson/Projects/lobster-etfs"
LOG_FILE="$PROJECT_DIR/reports/08_agent_ops/scheduler_run.log"

cd "$PROJECT_DIR" || exit 1

mkdir -p "$PROJECT_DIR/reports/08_agent_ops"

echo "======================================" >> "$LOG_FILE"
echo "Lobster scheduled run started at $(date)" >> "$LOG_FILE"

"$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/scripts/lobster_auto_refresh.py" >> "$LOG_FILE" 2>&1

echo "Lobster scheduled run finished at $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"