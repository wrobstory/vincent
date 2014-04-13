# -*- coding: utf-8 -*-
"""

Legend: Classes to define Vega Legends

"""
from __future__ import (print_function, division)
from .core import grammar, GrammarClass
from .properties import PropertySet
from ._compat import str_types


class LegendProperties(GrammarClass):
    """Sets of Legend Properties.

    These properties enable custom mark properties for the legend
    elements. Each element can use a standard ValueRef for values.

    """

    @grammar(PropertySet)
    def title(value):
        """Legend title properties """

    @grammar(PropertySet)
    def labels(value):
        """Legend label properties"""

    @grammar(PropertySet)
    def symbols(value):
        """Legend symbol properties"""

    @grammar(PropertySet)
    def gradient(value):
        """Continuous color gradient for legend"""

    @grammar(PropertySet)
    def legend(value):
        """Legend styling properties"""


class Legend(GrammarClass):
    """Definition for Vega Legends

    Legends visualize scales, and take one or more scales as their input.
    They can be customized via a LegendProperty object.

    """

    @grammar(str_types)
    def size(value):
        """The name of the scale that determines an item's size"""

    @grammar(str_types)
    def shape(value):
        """The name of the scale that determines an item's shape"""

    @grammar(str_types)
    def fill(value):
        """The name of the scale that determines an item's fill color"""

    @grammar(str_types)
    def stroke(value):
        """The name of the scale that determine's stroke color"""

    @grammar(str_types)
    def orient(value):
        """The orientation of the legend.

        Must be one of 'left' or 'right'
        """

        if value not in ('left', 'right'):
            raise ValueError('Value must be one of "left" or "right".')

    @grammar(int)
    def offset(value):
        """Pixel offset from figure"""

    @grammar(str_types)
    def title(value):
        """The Legend title"""

    @grammar(str_types)
    def format(value):
        """Optional formatting pattern for legend labels.

        See the D3 formatting pattern:
        https://github.com/mbostock/d3/wiki/Formatting
        """

    @grammar(list)
    def values(value):
        """Explicitly set visible legend values"""

    @grammar(LegendProperties)
    def properties(value):
        """Optional mark property definitions for custom styling"""
