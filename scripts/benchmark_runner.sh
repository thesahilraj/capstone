#!/usr/bin/env bash
# ==============================================================================
# Automated Benchmark Runner: Runs multi-algorithm comparative suite across modules
# ==============================================================================
set -e

echo "=================================================================="
echo "          OS-SimSuite: Automated Batch Benchmark Runner           "
echo "=================================================================="

WORKLOAD="${1:-data/sample_workload.json}"
echo "[BENCHMARK] Executing full suite on workload: $WORKLOAD"

if command -v python3 &>/dev/null; then
    PY="python3"
else
    PY="python"
fi

$PY main.py --batch "$WORKLOAD"

echo "=================================================================="
echo "[SUCCESS] Benchmark completed! Generated artifacts:"
echo "  • Figures:  output/figures/"
echo "  • Traces:   output/traces/"
echo "  • Reports:  output/reports/OS_SimSuite_Final_Report.pdf"
echo "=================================================================="
