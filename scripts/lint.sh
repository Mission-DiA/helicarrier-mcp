#!/bin/bash
set -e
cd "$(dirname "$0")/.."

EXIT_CODE=0

echo "=== Helicarrier MCP Lint Check ==="
echo ""

echo "Running ruff..."
poetry run ruff check . || EXIT_CODE=1

echo ""
echo "Running mypy..."
poetry run mypy helicarrier_mcp || EXIT_CODE=1

echo ""
echo "Running bandit..."
poetry run bandit -r helicarrier_mcp -ll || EXIT_CODE=1

echo ""
if [ $EXIT_CODE -eq 0 ]; then
  echo "All checks passed!"
else
  echo "Lint checks FAILED"
fi
exit $EXIT_CODE
