#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"  # -> docs/

if ! command -v msgfmt >/dev/null 2>&1; then
  echo "Warning: msgfmt not found. Install gettext (Linux: apt-get install gettext, macOS: brew install gettext && brew link gettext --force)" >&2
fi

API_DIR="source/api"
echo "[0/7] Generate API docs..."
rm -rf "$API_DIR"               # 关键：清掉旧的 .rst（避免残留 algolib.maths.complex）
mkdir -p "$API_DIR"

sphinx-apidoc -f -o "$API_DIR" ../src/algolib

# --- Strip any automodule directives and Module contents section from package page ---
PKG_RST="$API_DIR/algolib.physics.rst"
if [ -f "$PKG_RST" ]; then
  if [[ "$(uname)" == "Darwin" ]]; then
    # macOS (BSD sed)
    sed -i '' '/^\.\. automodule:: algolib\.physics/,/^$/d' "$PKG_RST"
    sed -i '' '/^Module contents$/,/^[^ ].*/d' "$PKG_RST"
  else
    # Linux (GNU sed, for CI)
    sed -i '/^\.\. automodule:: algolib\.physics/,/^$/d' "$PKG_RST"
    sed -i '/^Module contents$/,/^[^ ].*/d' "$PKG_RST"
  fi
fi


# --- Remove ALL automodule blocks for algolib.physics from the package page ---
PKG_RST="$API_DIR/algolib.physics.rst"
if [ -f "$PKG_RST" ]; then
  echo "[0/7] Strip automodule blocks from $PKG_RST"
  python3 - <<'PY'
from pathlib import Path
p = Path("docs/source/api/algolib.physics.rst")
if not p.exists():
    p = Path("source/api/algolib.physics.rst")
if not p.exists():
    raise SystemExit(0)

lines = p.read_text(encoding="utf-8").splitlines()
out = []
i = 0
removed = 0

def is_block_start(s: str) -> bool:
    return s.strip() == ".. automodule:: algolib.physics"

n = len(lines)
while i < n:
    if is_block_start(lines[i]):

        i += 1
        # skip all option lines that belong to this directive
        while i < n and lines[i].startswith("   :"):
            i += 1
        removed += 1
        continue  # do not append anything for this block
    out.append(lines[i])
    i += 1

# Also de-duplicate accidental duplicate option lines if any remained near the block
# (safety no-op if none)
cleaned = []
seen = set()
for ln in out:
    key = ln.strip()
    if key.startswith(":") and key in seen:
        continue
    if key.startswith(":"):
        seen.add(key)
    cleaned.append(ln)

if removed:
    p.write_text("\n".join(cleaned) + ("\n" if cleaned and cleaned[-1] != "" else ""), encoding="utf-8")
    print(f"Removed {removed} automodule block(s).")
else:
    print("No automodule blocks found.")
PY
else
  echo "[0/7] WARN: $PKG_RST not found; skip strip."
fi

# Preview the remaining top of package page for sanity
head -n 60 "$PKG_RST" | sed -n '1,120p' || true

echo "[1/7] Extract gettext templates..."
sphinx-build -E -b gettext source locale

echo "[2/7] Update/create PO files for zh_CN..."
sphinx-intl update -p locale -l zh_CN

echo "[3/7] Build EN site..."
sphinx-build -E -b html -D language=en    source build/html/en

echo "[4/7] Build ZH site..."
sphinx-build -E -b html -D language=zh_CN source build/html/zh

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
<p><a class="btn" href="./coverage/">Coverage report</a></p>
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

# --- 先逐文件用 msgfmt 打印“可读统计”（仅展示，不用于最终汇总） ---
for base in "${PO_BASES[@]}"; do
  [ -d "$base" ] || continue
  while IFS= read -r -d '' po; do
    STATS="$(msgfmt --statistics -o /dev/null "$po" 2>&1 || true)"
    echo " - $(basename "$po"): $STATS"
  done < <(find "$base" -type f -name '*.po' -print0)
done

# --- 去重重复 msgid（避免后续统计异常），需要 gettext 的 msguniq ---
if command -v msguniq >/dev/null 2>&1; then
  for base in "${PO_BASES[@]}"; do
    [ -d "$base" ] || continue
    while IFS= read -r -d '' po; do
      tmp="$(mktemp)"
      msguniq --use-first -o "$tmp" "$po" && mv "$tmp" "$po"
    done < <(find "$base" -type f -name '*.po' -print0)
  done
else
  echo "  (msguniq not found, skip de-duplicate .po; install gettext for best results)" >&2
fi

# --- 用 polib 精确统计并回写 README（不要再用 sed/awk 抽数字） ---
python3 - <<'PY'
import pathlib, re, sys
try:
    import polib
except Exception as e:
    print("polib not available; cannot compute progress.", file=sys.stderr)
    sys.exit(1)

BASES = [
    pathlib.Path("source/locale/zh_CN/LC_MESSAGES"),
    pathlib.Path("locale/zh_CN/LC_MESSAGES"),
]

files = []
for b in BASES:
    if b.is_dir():
        files += sorted(b.rglob("*.po"))

trans = fuzzy = untrans = total = 0

def file_stats(po_path: pathlib.Path):
    T=F=U=Tot=0
    po = polib.pofile(str(po_path))
    for e in po:
        if e.obsolete:
            continue
        Tot += 1
        if e.fuzzy:
            F += 1
        elif e.translated():
            T += 1
        else:
            U += 1
    return T,F,U,Tot

for f in files:
    T,F,U,Tot = file_stats(f)
    trans += T; fuzzy += F; untrans += U; total += Tot

pct = int(round(100.0 * trans / total)) if total else 0
print(f"Summary: translated={trans}, fuzzy={fuzzy}, untranslated={untrans}, total={total}")
print(f"Progress: {pct}%")

# 回写 README 的锚点块
readme = pathlib.Path(__file__).resolve().parents[1] / "README.md"
badge = f"[![i18n zh_CN](https://img.shields.io/badge/i18n%20zh--CN-{pct}%25-blue)](https://HidekiHokuto.github.io/algolib/zh/)"
block = "<!-- i18n-progress:start -->\n" + badge + f"\nTranslation Progress: {pct}%\n<!-- i18n-progress:end -->"

if readme.exists():
    txt = readme.read_text(encoding="utf-8")
    new = re.sub(r"<!-- i18n-progress:start -->.*?<!-- i18n-progress:end -->",
                 block, txt, flags=re.S)
    if new != txt:
        readme.write_text(new, encoding="utf-8")
        print("README updated.")
    else:
        print("README already up-to-date.")
else:
    print("README.md not found; skip updating.", file=sys.stderr)
PY

echo "✅ Done."
echo "EN: $(pwd)/build/html/en"
echo "ZH: $(pwd)/build/html/zh"