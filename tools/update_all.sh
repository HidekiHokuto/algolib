#!/usr/bin/env bash
set -euo pipefail

# Simple, safe updater for README badges (i18n progress + coverage) on a dedicated branch.
# - No stash/pop to avoid mixing build artifacts.
# - Only commits README.md and PO files (docs/source/locale/**).
# - Does not add coverage.xml (ignored by .gitignore).

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TARGET_BRANCH="docs/readme-update"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# Ensure working tree is clean before switching branches to avoid accidental carries
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "❌ Working tree not clean. Commit or stash your changes on '$CURRENT_BRANCH' first." >&2
  exit 1
fi

echo "🔀 Switching to ${TARGET_BRANCH}..."
git fetch origin --quiet || true
# Create the target branch from dev if it does not exist locally
if ! git rev-parse --verify --quiet "$TARGET_BRANCH" >/dev/null; then
  git checkout -b "$TARGET_BRANCH" origin/dev || git checkout -b "$TARGET_BRANCH" dev
else
  git checkout "$TARGET_BRANCH"
fi
# Fast-forward to remote if possible
(git pull --ff-only || true) >/dev/null 2>&1

echo "📖 Running i18n_build.sh (no repo writes by CI; local only)..."
zsh docs/i18n_build.sh

# Always regenerate coverage.xml to ensure it is fresh
echo "🧪 Running pytest to refresh coverage.xml..."
(pytest --cov=src/algolib --cov-report=xml:coverage.xml -q || true)

echo "📊 Updating coverage badge from coverage.xml..."
python tools/update_coverage_badge.py

# Stage only durable sources (README + PO files). Do not add coverage.xml.
echo "✅ Committing changes (README + PO files)..."
set +e
git add README.md docs/source/locale 2>/dev/null
if ! git diff --cached --quiet; then
  git commit -m "docs: update README badges (i18n + coverage)"
  git push origin "$TARGET_BRANCH"
else
  echo "ℹ️ Nothing to commit; README and PO files unchanged."
fi
set -e

# Return to original branch
echo "↩️ Switching back to ${CURRENT_BRANCH}..."
git checkout "$CURRENT_BRANCH"

echo "🎉 Done. Updates are on branch ${TARGET_BRANCH}."