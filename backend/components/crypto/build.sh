#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building k_crypto for Linux..."

if ! command -v maturin &> /dev/null; then
    echo "Installing maturin..."
    pip install maturin
fi

if ! command -v cargo &> /dev/null; then
    echo "Error: Rust toolchain not found. Install from https://rustup.rs"
    exit 1
fi

echo "Running cargo tests..."
cargo test --release

echo "Building wheel for current platform..."
maturin build --release --strip

echo "Build complete. Wheels are in target/wheels/"
ls -la target/wheels/*.whl 2>/dev/null || echo "No wheels found"

echo ""
echo "To install locally:"
echo "  pip install target/wheels/k_crypto-*.whl"
echo ""
echo "To install in editable mode (development):"
echo "  pip install -e ."
