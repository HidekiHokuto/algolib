#!/usr/bin/env bash
set -euo pipefail

# 进入脚本所在目录（即 docs/）
cd "$(dirname "$0")"

echo "[1/4] Extract gettext templates..."
sphinx-build -b gettext source locale

echo "[2/4] Update/create PO files for zh_CN..."
sphinx-intl update -p locale -l zh_CN

echo "[3/4] Build EN site..."
sphinx-build -b html -D language=en source build/html/en

echo "[4/4] Build ZH site..."
sphinx-build -b html -D language=zh_CN source build/html/zh

# 创建语言选择首页
cat > build/html/index.html <<'HTML'
<!doctype html><meta charset="utf-8">
<title>algolib docs</title>
<h1>Select language / 选择语言</h1>
<p><a href="./en/">English</a> | <a href="./zh/">简体中文</a></p>
HTML

# 禁用 Jekyll
touch build/html/.nojekyll

echo "✅ Done."
echo "EN: $(pwd)/build/html/en"
echo "ZH: $(pwd)/build/html/zh"