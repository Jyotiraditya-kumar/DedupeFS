#!/usr/bin/env bash
# DedupFS Web UI Launcher
set -e

PORT=${1:-5000}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================================="
echo "  Starting DedupFS Management Dashboard"
echo "  Project Root: ${PROJECT_DIR}"
echo "  Port: ${PORT}"
echo "======================================================="

cd "${PROJECT_DIR}"
python3 ui/app.py "${PORT}"

