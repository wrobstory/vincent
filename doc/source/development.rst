.. _development:

Development
===========

Want to help make Vincent better? Here's how to get started:

First, `fork <https://help.github.com/articles/fork-a-repo>`_  Vincent on `Github <https://github.com/wrobstory/vincent>`_. Then clone your fork into a local folder::

    $git clone https://github.com/your_username/vincent

Set up your `virtualenv <http://www.virtualenv.org/en/latest/>`_::

    $virtualenv .env

Pip install the dependencies::

    $pip install -r requirements.txt

Set up the package for development::

    $python setup.py develop

Now you're set. Here are some area where Vincent could use contribution:

Charts.py
--------

Go take a look at charts.py within the main Vincent package and you'll see that we're using Vincent to build Vincent! This module is the home for convenience chart builds, such that we can do things like ``bar = vincent.Bar([10, 20, 30])``. This package still needs maps, pie charts, donut charts, treemaps, faceted charts, etc. If you use Vincent to build a new chart, make a pull request for this module. Make sure you add a test with valid grammar to ``test_charts.py``

Transforms.py
-------------

There are still a number of Vega Transform types that have yet to be implemented. Start adding them to ``transforms.py`` and make a pull request.

Testing
-------

Vincent uses the Nose library for testing, and aims for reasonable test coverage. Take a look at ``test_charts.py`` and ``test_vega.py`` to get an idea of what our tests look like, and please add coverage for anything you add.


