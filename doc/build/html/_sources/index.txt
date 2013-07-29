.. vincent documentation master file, created by
   sphinx-quickstart on Fri May 24 02:28:04 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Vincent: A Python to Vega Translator
====================================

The folks at Trifacta are making it easy to build visualizations on top of D3 with Vega. Vincent makes it easy to build Vega with Python.


Concept
-------

The data capabilities of Python. The visualization capabilities of JavaScript.

Vincent allows you to build Vega specifications in a Pythonic way, and performs type-checking to help ensure that your specifications are correct. It also has a number of convenience chart-building methods that quickly turn Python data structures into Vega visualization grammar, enabling graphical exploration. It allows for quick iteration of visualization designs via getters and setters on grammar elements, and outputs the final visualization to JSON.

Perhaps most importantly, Vincent has Pandas-Fu, and is built specifically to allow for quick plotting of DataFrames and Series.

Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   charts_library
   building_vega
   vega_api
   development

* :ref:`search`
