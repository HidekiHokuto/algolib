#!/usr/bin/env bash
set -euo pipefail

# 进入脚本所在目录（即 docs/）
cd "$(dirname "$0")"

echo "[1/4] Extract gettext templates..."
sphinx-build -b gettext source locale

echo "[2/4] Update/create PO files for zh_CN..."
sphinx-intl update -p locale -l zh_CN

echo "[3/4] Build EN site..."
sphinx-build -b html -D language=en source build/en

echo "[4/4] Build ZH site..."
sphinx-build -b html -D language=zh_CN source build/zh

echo "✅ Done."
echo "EN: $(pwd)/build/en"
echo "ZH: $(pwd)/build/zh"