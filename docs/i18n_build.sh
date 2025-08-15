#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"  # -> docs/

# 可选：自动生成 API 文档
if command -v sphinx-apidoc >/dev/null 2>&1; then
  echo "[0/7] Generate API docs..."
  sphinx-apidoc -f -o source/api ../src/algolib
fi

echo "[1/7] Extract gettext templates..."
sphinx-build -b gettext source locale

echo "[2/7] Update/create PO files for zh_CN..."
sphinx-intl update -p locale -l zh_CN

echo "[3/7] Build EN site..."
sphinx-build -b html -D language=en    source build/html/en

echo "[4/7] Build ZH site..."
sphinx-build -b html -D language=zh_CN source build/html/zh

echo "[5/7] Create root index.html..."
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

echo "[6/7] Disable Jekyll..."
touch build/html/.nojekyll

echo "[7/7] Compute zh_CN translation progress & update README..."
# 统计所有 zh_CN .po：翻译/模糊/未翻译
total=0; trans=0; fuzzy=0; untrans=0

# 兼容两种常见布局：docs/locale/... 或 docs/source/locale/...
mapfile -t PO_FILES < <(find . -type f -path "./locale/zh_CN/LC_MESSAGES/*.po" -o -path "./source/locale/zh_CN/LC_MESSAGES/*.po" | sort)
if [ ${#PO_FILES[@]} -eq 0 ]; then
  echo "No zh_CN .po files found; progress remains 0%."
else
  for f in "${PO_FILES[@]}"; do
    # msgfmt --statistics 输出到 stderr，例如：
    #   12 translated messages, 3 fuzzy translations, 5 untranslated messages.
    stats="$(msgfmt --statistics -o /dev/null "$f" 2>&1 || true)"
    t=$(echo "$stats" | sed -n 's/.*\([0-9][0-9]*\) translated.*/\1/p')
    fu=$(echo "$stats" | sed -n 's/.*\([0-9][0-9]*\) fuzzy.*/\1/p')
    u=$(echo "$stats" | sed -n 's/.*\([0-9][0-9]*\) untranslated.*/\1/p')
    t=${t:-0}; fu=${fu:-0}; u=${u:-0}
    trans=$((trans + t))
    fuzzy=$((fuzzy + fu))
    untrans=$((untrans + u))
  done
  total=$((trans + fuzzy + untrans))
fi

pct=0
if [ "$total" -gt 0 ]; then
  # 四舍五入为整数百分比
  pct=$(awk -v a="$trans" -v b="$total" 'BEGIN{ printf("%d", (a*100.0/b)+0.5) }')
fi

# 回写 README：两处——文字百分比 & 徽章中的百分比（%25 要 URL 编码）
# 这些替换依赖 README 中的占位写法（见下文 README 修改）
if [ -f ../README.md ]; then
  sed -i -E "s/(ZH Translation Progress:\s*)[0-9]+%/\\1${pct}%/" ../README.md
  sed -i -E "s#(i18n_zh--CN-)[0-9]+%25#\\1${pct}%25#" ../README.md
  echo "Updated README progress to ${pct}% (translated=${trans}, fuzzy=${fuzzy}, untranslated=${untrans}, total=${total})."
else
  echo "README.md not found at repo root; skipped progress update."
fi

echo "✅ Done."
echo "EN: $(pwd)/build/html/en"
echo "ZH: $(pwd)/build/html/zh"