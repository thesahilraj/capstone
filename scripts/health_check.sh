#!/usr/bin/env bash
# ==============================================================================
# Health Check Script: Validates environment, Python version, and dependencies
# ==============================================================================
set -e

echo "[HEALTH-CHECK] Running OS-SimSuite Pre-Flight Diagnostics..."

# 1. Python version check
if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
else
    echo "[FAIL] Python runtime not found!"
    exit 1
fi

PY_VER=$($PY -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[OK] Python runtime: $($PY --version) (Version: $PY_VER)"

# 2. Dependency verification
echo "[HEALTH-CHECK] Verifying installed Python libraries..."
$PY -c '
required = ["numpy", "matplotlib", "tabulate", "reportlab", "pytest"]
missing = []
for pkg in required:
    try:
        __import__(pkg)
        print(f"  [OK] {pkg}")
    except ImportError:
        missing.append(pkg)
if missing:
    print(f"[FAIL] Missing required packages: {missing}")
    sys.exit(1)
'

# 3. Directory structure & permissions check
echo "[HEALTH-CHECK] Verifying directory integrity..."
for d in src/modules src/analytics src/utils docs/assets data output/figures output/traces output/reports tests; do
    if [ -d "$d" ]; then
        echo "  [OK] Directory exists: $d"
    else
        echo "  [WARN] Creating missing directory: $d"
        mkdir -p "$d"
    fi
done

echo "[HEALTH-CHECK] All diagnostic checks passed successfully!"
