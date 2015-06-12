# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -E
SPHINXBUILD   = $(VENVDIR)/bin/sphinx-build
VIRTUALENV    = virtualenv
PAPER         =
BUILDDIR      = build
VENVDIR       = $(BUILDDIR)/venv
TARGET        ?= devo8

# User-friendly check for sphinx-build
ifeq ($(shell which $(VIRTUALENV) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(VIRTUALENV)' command was not found. Make sure you have virtualenv installed.  This is typically done via 'sudo pip install -U $(VIRTUALENV))
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees -t $(TARGET) $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source

.PHONY: help clean html pdf

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  pseudoxml  to make pseudoxml-XML files for display purposes"

clean:
	rm -rf $(BUILDDIR)/*

html:   $(SPHINXBUILD)
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

pseudoxml: $(SPHINXBUILD)
	$(SPHINXBUILD) -b pseudoxml $(ALLSPHINXOPTS) $(BUILDDIR)/pseudoxml
	@echo
	@echo "Build finished. The pseudo-XML files are in $(BUILDDIR)/pseudoxml."

pdf: $(SPHINXBUILD)
	$(SPHINXBUILD) -b pdf $(ALLSPHINXOPTS) $(BUILDDIR)/pdf
	@echo
	@echo "Build finished. The PDF files are in $(BUILDDIR)/pdf."

venv: $(VENVDIR)/bin/activate
$(BUILDDIR)/venv/bin/activate: requirements.txt
	test -d $(VENVDIR) || $(VIRTUALENV) $(VENVDIR)
	$(VENVDIR)/bin/pip install -Ur requirements.txt
	touch $(VENVDIR)/bin/activate

devbuild: venv
	cd dist-packages/rst2pdf && ../../$(VENVDIR)/bin/python setup.py install
	cd dist-packages/wordaxe && ../../$(VENVDIR)/bin/python setup.py install

$(SPHINXBUILD):
	make devbuild
