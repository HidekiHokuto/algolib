import os, sys
sys.path.insert(0, os.path.abspath("../../src"))

project = "Algolib"
author = "Hideki Hokuto"
release = "0.1.0"

extensions = [
    "myst_parser",          # Markdown 支持
    "sphinx.ext.autodoc",   # 从 docstring 生成 API 文档
    "sphinx.ext.viewcode",  # 文档里显示源码
    "sphinx.ext.napoleon",  # Google/NumPy 风格 docstring
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# --- i18n settings ---
language = "en"                # 默认英文
locale_dirs = ["locale/"]      # 翻译目录（相对 docs/source）
gettext_compact = False
