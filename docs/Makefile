# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# ==== i18n: extract POT templates ====
gettext:
	@sphinx-build -b gettext source locale

# ==== i18n: update/create PO files (add more locales with -l xx) ====
i18n-update:
	@sphinx-intl update -p locale -l zh_CN

# ==== i18n: compile PO -> MO (可选，部分主题用得到) ====
i18n-compile:
	@sphinx-intl build -d locale

# ==== build EN ====
html-en:
	@sphinx-build -b html -D language=en source build/html

# ==== build ZH ====
html-zh:
	@sphinx-build -b html -D language=zh_CN source build/html-zh

# ==== one-shot: extract -> update -> build both ====
html-i18n: gettext i18n-update html-en html-zh
	@echo "Built EN: build/html"
	@echo "Built ZH: build/html-zh"
