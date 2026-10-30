Chinese Herbarium Documentation
===============================

This documentation is generated with Sphinx from the Django project source.
It is intended to help future changes to the herb, local plant, food, recipe,
formula, and personal formula areas of the app.

Regenerate the model diagrams before building the docs:

.. code-block:: console

   .venv/bin/python manage.py export_model_diagrams

Build the HTML documentation:

.. code-block:: console

   .venv/bin/sphinx-build -b html docs docs/_build/html

If Graphviz is installed, Sphinx can render the DOT diagram directly. Without
Graphviz, the generated SVG fallback is still included.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   diagrams
   models
   views
   forms
   management
   regeneration
