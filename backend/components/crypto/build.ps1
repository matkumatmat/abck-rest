$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Building k_crypto for Windows..." -ForegroundColor Cyan

# Check maturin
try {
    maturin --version | Out-Null
} catch {
    Write-Host "Installing maturin..." -ForegroundColor Yellow
    pip install maturin
}

# Check cargo
try {
    cargo --version | Out-Null
} catch {
    Write-Host "Error: Rust toolchain not found. Install from https://rustup.rs" -ForegroundColor Red
    exit 1
}

Write-Host "Running cargo tests..." -ForegroundColor Cyan
cargo test --release

Write-Host "Building wheel for Windows..." -ForegroundColor Cyan
maturin build --release --strip

Write-Host "Build complete. Wheels are in target/wheels/" -ForegroundColor Green
Get-ChildItem -Path "target/wheels/*.whl" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_.FullName }

Write-Host ""
Write-Host "To install locally:" -ForegroundColor Yellow
Write-Host "  pip install target/wheels/k_crypto-*.whl"
Write-Host ""
Write-Host "To install in editable mode (development):" -ForegroundColor Yellow
Write-Host "  pip install -e ."
