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
<html lang="en"><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>algolib — Rigorous Numerical Computation Library</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" rel="stylesheet">

    <!-- Tailwind Configuration -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#0F3460', // 深蓝 - 严谨
                        secondary: '#F9D342', // 明黄 - 可追溯
                        accent: '#1A73E8',
                        dark: '#1A1A2E',
                        light: '#F5F7FA'
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace']
                    },
                }
            }
        }
    </script>

    <style type="text/tailwindcss">
        @layer utilities {
            .content-auto {
                content-visibility: auto;
            }
            .text-balance {
                text-wrap: balance;
            }
            .transition-custom {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .card-hover {
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .card-hover:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
            }
            .gradient-bg {
                background: linear-gradient(135deg, #0F3460 0%, #1A73E8 100%);
            }
        }
    </style>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
</head>
<body class="bg-light text-dark font-sans">
    <!-- Header with Navigation -->
    <header class="sticky top-0 z-50 bg-white/90 backdrop-blur-sm shadow-sm">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <!-- Logo & Project Name -->
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 rounded-lg gradient-bg flex items-center justify-center">
                        <i class="fa fa-calculator text-white text-xl"></i>
                    </div>
                    <span class="text-xl font-bold text-primary">algolib</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Hero Section (First Screen) -->
    <section class="py-20 md:py-32 bg-gradient-to-b from-white to-light">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="max-w-4xl mx-auto text-center">
                <!-- Logo for Hero -->
                <div class="w-16 h-16 mx-auto mb-8 rounded-lg gradient-bg flex items-center justify-center">
                    <i class="fa fa-calculator text-white text-2xl"></i>
                </div>

                <!-- Project Name -->
                <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-primary mb-6">algolib</h1>

                <!-- Slogan -->
                <p class="text-xl md:text-2xl text-gray-700 font-medium mb-8 italic">
                    A rigorous, auditable numerical computation library in Python.
                </p>

                <!-- Brief Introduction -->
                <p class="text-lg text-gray-600 mb-10 max-w-2xl mx-auto text-balance">
                    algolib 是一个开源数学算法库，目标是为科学研究与工程计算提供高可靠、可追溯、工业级审计友好的数值工具。
                </p>

                <!-- Key Features -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div class="bg-white p-6 rounded-xl shadow-md">
                        <i class="fa fa-code text-primary text-2xl mb-4"></i>
                        <h3 class="font-semibold mb-2">统一 API 与模块结构</h3>
                    </div>
                    <div class="bg-white p-6 rounded-xl shadow-md">
                        <i class="fa fa-check-circle text-primary text-2xl mb-4"></i>
                        <h3 class="font-semibold mb-2">严格的数值约定</h3>
                    </div>
                    <div class="bg-white p-6 rounded-xl shadow-md">
                        <i class="fa fa-flask text-primary text-2xl mb-4"></i>
                        <h3 class="font-semibold mb-2">高覆盖率测试体系</h3>
                    </div>
                </div>

                <!-- Primary Goal -->
                <div class="inline-block bg-primary/10 text-primary px-6 py-3 rounded-full text-lg font-medium">
                    比 math / numpy 更严谨，比工业黑箱更透明
                </div>

                <!-- Action Buttons -->
                <div class="mt-12 flex flex-col sm:flex-row justify-center gap-4">
                    <a href="https://hidekihokuto.github.io/algolib/coverage/" class="px-6 py-3 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg shadow-lg shadow-primary/20 transition-custom">
                        <i class="fa fa-chart-pie mr-2"></i>Coverage Report
                    </a>
                </div>

                <!-- Language Selection -->
                <div class="mt-10">
                    <p class="text-gray-600 mb-3">Select doc language / 选择文档语言：</p>
                    <div class="flex justify-center gap-3">
                        <a href="./en/" class="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:border-primary transition-custom">
                            English
                        </a>
                        <a href="./zh/" class="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:border-primary transition-custom">
                            简体中文
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-primary text-white py-12">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="flex items-center space-x-2 mb-6 md:mb-0">
                    <div class="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                        <i class="fa fa-calculator text-white text-xl"></i>
                    </div>
                    <span class="text-xl font-bold">algolib</span>
                </div>

                <div class="text-center md:text-right">
                    <p class="mb-2">© 2025 algolib contributors. All rights reserved.</p>
                    <p class="text-white/70 text-sm">Released under the GNU General Public License v3.0 (GPLv3)</p>
                </div>
            </div>
        </div>
    </footer>

    <!-- JavaScript for interactions -->
    <script>
        // Navbar scroll effect
        const navbar = document.querySelector('header');
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-md');
                navbar.classList.remove('shadow-sm');
            } else {
                navbar.classList.remove('shadow-md');
                navbar.classList.add('shadow-sm');
            }
        });
    </script>



    </body></html>
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