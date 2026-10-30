Regenerating Documentation
==========================

The short version from the project root is:

.. code-block:: console

   cd docs
   make html

That target regenerates the model diagrams first and then builds the HTML docs.

Install Python documentation dependencies:

.. code-block:: console

   .venv/bin/python -m pip install -r requirements.txt

Optional but recommended: install Graphviz so Sphinx can render DOT diagrams.
On Debian or Ubuntu this is usually:

.. code-block:: console

   sudo apt install graphviz

Regenerate model diagrams:

.. code-block:: console

   .venv/bin/python manage.py export_model_diagrams

Build the docs:

.. code-block:: console

   .venv/bin/sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser.
