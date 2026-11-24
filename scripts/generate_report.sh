#!/usr/bin/env bash
# ==============================================================================
# Generate Report Script: Compiles official submission PDF Report
# ==============================================================================
set -e

echo "[REPORT-GEN] Compiling Official Capstone Submission PDF Report..."

if command -v python3 &>/dev/null; then
    PY="python3"
else
    PY="python"
fi

$PY main.py --report

echo "[REPORT-GEN] Submission Report ready at: output/reports/OS_SimSuite_Final_Report.pdf"
