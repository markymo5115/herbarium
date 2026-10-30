SPHINXBUILD ?= ../.venv/bin/sphinx-build
SOURCEDIR = .
BUILDDIR = _build

.PHONY: html diagrams clean

html: diagrams
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

diagrams:
	../.venv/bin/python ../manage.py export_model_diagrams --output-dir _static

clean:
	rm -rf $(BUILDDIR)
