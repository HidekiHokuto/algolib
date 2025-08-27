#!/usr/bin/env bash
set -euo pipefail
ROOT="$(dirname "$0")/.."
cd "$ROOT"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "🔀 Switching to docs/readme-update branch..."
git stash push -u -m "temp-update" || true
git checkout docs/readme-update

echo "📖 Running i18n_build.sh..."
zsh docs/i18n_build.sh

echo "📊 Updating coverage badge..."
python tools/update_coverage_badge.py

echo "✅ Committing changes..."
git add README.md docs/source/locale coverage.xml || true
git commit -m "docs: update README badges (i18n + coverage)" || true
git push origin docs/readme-update

echo "↩️ Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH"
git stash pop || true

echo "✅ Done. Updates pushed to docs/readme-update"