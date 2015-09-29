# -*- coding: utf-8 -*-
"""

ValueRef: Generally used in a PropertySet class to define a set of values
within a property

"""
from .core import grammar, GrammarClass
from ._compat import str_types


class ValueRef(GrammarClass):
    """
    Container for the value-referencing properties of marks

    It is often useful for marks to share properties to maintain consistency
    when parts of the visualization are changed. Additionally, the marks
    themselves may have properties somehow mapped from the data (i.e. mark
    size proportional to some data field). The ``ValueRef`` class can be
    used to either define values locally or reference other fields.

    See the vega wiki for details:
    https://github.com/vega/vega/wiki/Marks#value-references
    """
    @grammar(str_types + (int, float))
    def value(value):
        pass

    @grammar(str_types)
    def field(value):
        pass

    @grammar(str_types)
    def datum(value):
        pass

    @grammar(str_types)
    def group(value):
        pass

    @grammar(str_types)
    def parent(value):
        pass

    @grammar(str_types)
    def scale(value):
        pass

    @grammar((int, float))
    def mult(value):
        pass

    @grammar((int, float))
    def offset(value):
        pass

    @grammar(bool)
    def band(value):
        pass
