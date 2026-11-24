# ==============================================================================
# OS-SimSuite: PowerShell Execution Wrapper for Windows
# ==============================================================================
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "          OS-SimSuite: Operating System Simulator" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Check Python command
$PyCmd = "python"
try {
    $version = & $PyCmd --version 2>&1
    Write-Host "[INFO] Detected $version" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python was not found in PATH." -ForegroundColor Red
    exit 1
}

# Ensure output directories exist
New-Item -ItemType Directory -Force -Path output/figures, output/traces, output/tables, output/reports | Out-Null

if ($args.Count -eq 0) {
    Write-Host "[INFO] Launching Interactive Terminal Dashboard..." -ForegroundColor Yellow
    & $PyCmd main.py --interactive
} else {
    & $PyCmd main.py $args
}
