#!/usr/bin/env bash
set -euo pipefail

# 切到项目根目录
cd "$(dirname "$0")/.."

echo "📖 Running i18n_build.sh..."
zsh docs/i18n_build.sh

echo "📊 Updating coverage badge..."
python tools/update_coverage_badge.py

echo "✅ All updates complete. Don't forget to:"
echo "   git add README.md docs/source/locale coverage.xml"
echo "   git commit -m \"docs: update i18n progress and coverage badge\""
echo "   git push"