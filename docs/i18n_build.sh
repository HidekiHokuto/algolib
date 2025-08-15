#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"  # -> docs/

# 可选：自动生成 API 文档（注释掉就不生成）
if command -v sphinx-apidoc >/dev/null 2>&1; then
  echo "[0/6] Generate API docs..."
  sphinx-apidoc -f -o source/api ../src/algolib
fi

echo "[1/6] Extract gettext templates..."
sphinx-build -b gettext source locale

echo "[2/6] Update/create PO files for zh_CN..."
sphinx-intl update -p locale -l zh_CN

echo "[3/6] Build EN site..."
sphinx-build -b html -D language=en    source build/html/en

echo "[4/6] Build ZH site..."
sphinx-build -b html -D language=zh_CN source build/html/zh

echo "[5/6] Create root index.html..."
mkdir -p build/html
cat > build/html/index.html <<'HTML'
<!doctype html><meta charset="utf-8">
<title>algolib docs</title>
<style>
  body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; padding: 2rem; line-height: 1.6; }
  a { text-decoration: none; }
  .btn { display:inline-block; padding:.6rem 1rem; border:1px solid #ccc; border-radius:8px; margin-right:1rem; }
</style>
<h1>algolib documentation</h1>
<p>Select language / 选择语言：</p>
<p>
  <a class="btn" href="./en/">English</a>
  <a class="btn" href="./zh/">简体中文</a>
</p>
HTML

echo "[6/6] Disable Jekyll..."
touch build/html/.nojekyll

echo "✅ Done."
echo "EN: $(pwd)/build/html/en"
echo "ZH: $(pwd)/build/html/zh"