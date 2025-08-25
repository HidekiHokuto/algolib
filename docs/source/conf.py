# docs/source/conf.py
import os, sys
sys.path.insert(0, os.path.abspath("../../src"))

project = "Algolib"
author = "Hideki Hokuto"
release = "0.1.1"
copyright = f"2025, {author}"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
]

html_theme = "sphinx_rtd_theme"
templates_path = ["_templates"]           # 可留空目录，无需放模板
html_static_path = ["_static"]            # 我们会把 JS/CSS 放这里
language = "en"
locale_dirs = ["locale/"]
gettext_compact = False

# 使用主题默认侧边栏，不再指定自定义模板
# html_sidebars = {...}  # ← 删除这一段配置（如果你有的话）


# 注入我们的 JS 与 CSS
def setup(app):
    app.add_js_file("langswitch.js")
    # app.add_css_file("custom.css")
html_css_files = ['custom.css']