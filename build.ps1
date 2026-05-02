[CmdletBinding()]
param(
    [switch]$Clean,
    [switch]$NoBuild,
    [string]$Config = ".\NewWorld Config Manager.spec"
)

$ErrorActionPreference = "Stop"

$VENV_DIR = Join-Path $PSScriptRoot ".venv"
$PYTHON = Join-Path $VENV_DIR "Scripts\python.exe"
$PIPER = Join-Path $VENV_DIR "Scripts\pyinstaller.exe"

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-ErrorExit {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
    exit 1
}

# Check for venv
if (!(Test-Path $VENV_DIR)) {
    Write-ErrorExit "Virtual environment not found at '$VENV_DIR'.`nPlease create one with: python -m venv .venv"
}

# Check for python in venv
if (!(Test-Path $PYTHON)) {
    Write-ErrorExit "Python not found in virtual environment at '$PYTHON'."
}

# Install/verify dependencies
Write-Info "Verifying dependencies..."
& $PYTHON -m pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-ErrorExit "Failed to install dependencies. Check requirements.txt."
}
Write-Success "Dependencies verified."

# Clean if requested
if ($Clean) {
    Write-Warn "Cleaning build artifacts..."
    Remove-Item -Recurse -Force "dist", "build" -ErrorAction SilentlyContinue
    Remove-Item -Force "newworld_config_manager.egg-info" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "__pycache__" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "newworld_config_manager\__pycache__" -ErrorAction SilentlyContinue
    Write-Success "Clean complete."
}

# Build
if ($NoBuild) {
    Write-Info "Setup complete (skipping build)."
    exit 0
}

Write-Info "Building New World Config Manager..."

& $PIPER $Config --clean

if ($LASTEXITCODE -ne 0) {
    Write-ErrorExit "Build failed with exit code $LASTEXITCODE. Check output above for errors."
}

# Verify build output
if (Test-Path "dist\NewWorld Config Manager.exe") {
    $version = "N/A"
    if (Test-Path "VERSION") {
        $version = (Get-Content VERSION -Raw).Trim()
    }
    $exe = Get-Item "dist\NewWorld Config Manager.exe"
    Write-Success "`nBuild successful!"
    Write-Host "  Version : $version"
    Write-Host "  Output  : $($exe.FullName)"
    Write-Host "  Size    : $([math]::Round($exe.Length / 1MB, 2)) MB"
} else {
    Write-ErrorExit "Build output not found at dist\NewWorld Config Manager.exe!"
}