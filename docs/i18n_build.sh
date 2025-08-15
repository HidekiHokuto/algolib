#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"  # -> docs/

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
  if [ -d "$base" ]; then
    # 遍历所有 .po 文件，用 msgfmt --statistics 逐个拿到三类计数并累加
    find "$base" -type f -name '*.po' | while IFS= read -r po; do
      STATS="$(msgfmt --statistics -o /dev/null "$po" 2>&1 || true)"
      # 可能的输出示例：
      # "2 translated messages, 0 fuzzy translations, 5 untranslated messages."
      t=$(printf '%s' "$STATS" | sed -n 's/.*\([0-9][0-9]*\) translated.*/\1/p' | head -n1)
      f=$(printf '%s' "$STATS" | sed -n 's/.*\([0-9][0-9]*\) fuzzy.*/\1/p' | head -n1)
      u=$(printf '%s' "$STATS" | sed -n 's/.*\([0-9][0-9]*\) untranslated.*/\1/p' | head -n1)
      [ -z "$t" ] && t=0
      [ -z "$f" ] && f=0
      [ -z "$u" ] && u=0
      TRANS=$((TRANS + t))
      FUZZY=$((FUZZY + f))
      UNTRANS=$((UNTRANS + u))
      TOTAL=$((TOTAL + t + f + u))
      echo " - $(basename "$po"): $STATS"
    done
  fi
done

if [ "$TOTAL" -gt 0 ]; then
  # 只把“非 fuzzy 的已翻译”算作进度
  # 由于 msgfmt 统计的 translated 本身已不含 fuzzy，这里直接用 TRANS/TOTAL
  PCT=$(( TRANS * 100 / TOTAL ))
else
  PCT=0
fi

echo "Summary: translated=$TRANS, fuzzy=$FUZZY, untranslated=$UNTRANS, total=$TOTAL"
echo "Progress: ${PCT}%"

# 回写 README：两种格式都兼容（svg 徽章和纯文本）
# 1) 徽章 URL 中的百分比（..-0%25-..）
sed -i.bak -E "s/(translation--)([0-9]+)%25/\1${PCT}%25/g" ../README.md || true
# 2) 文本中的 'Translation Progress: NN%'
sed -i.bak -E "s/(Translation Progress: )[0-9]+%/\1${PCT}%/g" ../README.md || true
rm -f ../README.md.bak

echo "✅ Done."
echo "EN: $(pwd)/build/html/en"
echo "ZH: $(pwd)/build/html/zh"