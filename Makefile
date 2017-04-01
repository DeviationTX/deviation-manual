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

# Preparation for SVG handling for LaTeX builds
SOURCEDIR     = source
IMAGEDIRS     = $(SOURCEDIR)/images
SVG2PDF       = inkscape
SVG2PDF_FLAGS =


# User-friendly check for sphinx-build
ifeq ($(shell which $(VIRTUALENV) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(VIRTUALENV)' command was not found. Make sure you have virtualenv installed.  This is typically done via 'sudo pip install -U $(VIRTUALENV))
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees -t $(TARGET) $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS)  source

.PHONY: help clean html latex latexpdf pdf

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  pdf        to make standalone PDF files via rst2pdf"
	@echo "  epub       to make an epub"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  gettext    to make PO message catalogs"
	@echo "  pseudoxml  to make pseudoxml-XML files for display purposes"

# Pattern rule for converting SVG to PDF
%.pdf : %.svg
	$(SVG2PDF) -f $< -A $@

# Build a list of SVG files to convert to PDFs
SVGs := $(shell find $(IMAGEDIRS) -name '*.svg')
PDFs := $(foreach svg, $(SVGs), $(patsubst %.svg,%.pdf,$(svg)))

# Make a rule to build the PDFs
images: $(PDFs)

clean:
	rm -rf $(BUILDDIR)/*
	rm $(PDFs)


html:   $(SPHINXBUILD)
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html-$(TARGET)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html-$(TARGET)."

epub:   $(SPHINXBUILD)
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS) $(BUILDDIR)/epub-$(TARGET)
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub-$(TARGET)."

latex:  $(SPHINXBUILD) $(PDFs)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex-$(TARGET)
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex-$(TARGET)."
	@echo "Run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."
 
latexpdf: $(SPHINXBUILD) $(PDFs)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex-$(TARGET)
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex-$(TARGET) all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex-$(TARGET)."

gettext: $(SPHINXBUILD)
	$(SPHINXBUILD) -b gettext $(I18NSPHINXOPTS) $(BUILDDIR)/locale
	@echo
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/locale."

pseudoxml: $(SPHINXBUILD)
	$(SPHINXBUILD) -b pseudoxml $(ALLSPHINXOPTS) $(BUILDDIR)/pseudoxml-$(TARGET)
	@echo
	@echo "Build finished. The pseudo-XML files are in $(BUILDDIR)/pseudoxml-$(TARGET)."

pdf: $(SPHINXBUILD)
	$(SPHINXBUILD) -b pdf $(ALLSPHINXOPTS) $(BUILDDIR)/pdf-$(TARGET)
	@echo
	@echo "Build finished. The PDF files are in $(BUILDDIR)/pdf-$(TARGET)."

venv: $(VENVDIR)/bin/activate
$(BUILDDIR)/venv/bin/activate: requirements.txt
	test -d $(VENVDIR) || $(VIRTUALENV) $(VENVDIR)
	$(VENVDIR)/bin/pip install -Ur requirements.txt
	touch $(VENVDIR)/bin/activate

devbuild: venv
	cd dist-packages/rst2pdf && ../../$(VENVDIR)/bin/python setup.py install
	cd dist-packages/wordaxe && ../../$(VENVDIR)/bin/python setup.py install

$(SPHINXBUILD):
	$(MAKE) devbuild
