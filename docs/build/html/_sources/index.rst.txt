.. docrawify documentation master file, created by
   sphinx-quickstart on Tue Mar 31 12:24:28 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

``docrawify`` -- rawify and de-rawify docstrings
================================================

.. automodule:: docrawify


API reference
-------------

The following functions are responsible for loading and dumping source files:

.. autofunction:: docrawify.load_python_module
.. autofunction:: docrawify.dump_python_module
.. autofunction:: docrawify.load_jupyter_notebook
.. autofunction:: docrawify.dump_jupyter_notebook


The following functions are responsible for (de)rawifying docstrings based on file type:

.. autofunction:: docrawify.rawify
.. autofunction:: docrawify._rawify
.. autofunction:: docrawify.handle_rawify
.. autofunction:: docrawify.get_docstring_node
