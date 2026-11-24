#!/usr/bin/env bash
# ==============================================================================
# OS-SimSuite: Primary Bash Execution Wrapper & Orchestrator
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "          OS-SimSuite: Operating System Simulator"
echo "=================================================================="

# Check Python environment
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3.10+ is required but was not found in PATH."
    exit 1
fi

# Ensure output directories exist
mkdir -p output/figures output/traces output/tables output/reports

# Run health check if requested or on first run
if [[ "$1" == "--health" ]]; then
    bash scripts/health_check.sh
    exit $?
fi

# Pass-through arguments to main.py
if [ $# -eq 0 ]; then
    echo "[INFO] Launching Interactive Terminal Dashboard..."
    "$PY_CMD" main.py --interactive
else
    "$PY_CMD" main.py "$@"
fi
