#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"  # -> docs/

if ! command -v msgfmt >/dev/null 2>&1; then
  echo "Warning: msgfmt not found. Install gettext (Linux: apt-get install gettext, macOS: brew install gettext && brew link gettext --force)" >&2
fi

# 可选：自动生成 API 文档（注释掉就不生成）
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

# 兼容两种可能的目录：docs/locale/... 和 docs/source/locale/...
PO_BASES=("locale/zh_CN/LC_MESSAGES" "source/locale/zh_CN/LC_MESSAGES")

TOTAL=0
TRANS=0
FUZZY=0
UNTRANS=0

for base in "${PO_BASES[@]}"; do
  [ -d "$base" ] || continue
  tmpfile="$(mktemp)"
  find "$base" -type f -name '*.po' > "$tmpfile"
  while IFS= read -r po; do
    [ -f "$po" ] || continue
    STATS="$(msgfmt --statistics -o /dev/null "$po" 2>&1 || true)"
    # 例："2 translated messages, 0 fuzzy translations, 5 untranslated messages."
    t=$(printf '%s' "$STATS" | sed -n 's/.*\([0-9][0-9]*\) translated.*/\1/p' | head -n1)
    f=$(printf '%s' "$STATS" | sed -n 's/.*\([0-9][0-9]*\) fuzzy.*/\1/p' | head -n1)
    u=$(printf '%s' "$STATS" | sed -n 's/.*\([0-9][0-9]*\) untranslated.*/\1/p' | head -n1)
    [ -z "$t" ] && t=0; [ -z "$f" ] && f=0; [ -z "$u" ] && u=0
    echo " - $(basename "$po"): $STATS"
    TRANS=$((TRANS + t))
    FUZZY=$((FUZZY + f))
    UNTRANS=$((UNTRANS + u))
    TOTAL=$((TOTAL + t + f + u))
  done < "$tmpfile"
  rm -f "$tmpfile"
done

if [ "$TOTAL" -gt 0 ]; then
  PCT=$(( TRANS * 100 / TOTAL ))   # msgfmt 的 translated 已排除 fuzzy
else
  PCT=0
fi

echo "Summary: translated=$TRANS, fuzzy=$FUZZY, untranslated=$UNTRANS, total=$TOTAL"
echo "Progress: ${PCT}%"

# 回写 README（徽章 & 文本），用 GNU sed，大小写不敏感
# 1) 徽章：匹配 i18n zh-CN 的百分比（支持中间空格/下划线/连字符和 %25 或 %）
sed -E -i "s/(i18n[ %_-]?zh[ _-]?CN-)[0-9]+(%25|%)/\1${PCT}\2/I" ../README.md

# 2) 纯文本：Translation Progress: 0%
sed -E -i "s/(Translation Progress:[[:space:]]*)[0-9]+%/\1${PCT}%/I" ../README.md

echo "✅ Done."
echo "EN: $(pwd)/build/html/en"
echo "ZH: $(pwd)/build/html/zh"