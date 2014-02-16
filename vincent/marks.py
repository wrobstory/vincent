# -*- coding: utf-8 -*-
"""

Marks: Classes to define Vega Marks

"""
from .core import grammar, GrammarClass, KeyedList
from .values import ValueRef
from .properties import PropertySet
from ._compat import str_types


class MarkProperties(GrammarClass):
    """Sets of all Mark properties

    Mark properties can change depending on user interaction or changing
    data. This class defines four events for which the properties may
    change.
    """
    @grammar(PropertySet)
    def enter(value):
        """PropertySet : properties applied when data is loaded
        """

    @grammar(PropertySet)
    def exit(value):
        """PropertySet : properties applied when data is removed
        """

    @grammar(PropertySet)
    def update(value):
        """PropertySet : properties applied for all non-exiting data

        (This is vague. Need better Vega docs.)
        """

    @grammar(PropertySet)
    def hover(value):
        """PropertySet, properties applied on mouse-over

        On mouse out, the ``update`` properties are applied.
        """


class MarkRef(GrammarClass):
    """Definitions for Mark source data
    """
    @grammar(str_types)
    def data(value):
        """string : Name of the source `Data`"""

    @grammar(list)
    def transform(value):
        """list : List of transforms to apply to the data"""


class Mark(GrammarClass):
    """Definitions for data marks

    Marks are the fundamental component that the viewer sees - such as a
    bar, line etc.. This class defines how the marks appear and what data
    the marks represent.
    """
    _valid_type_values = frozenset(['rect', 'symbol', 'path', 'arc', 'area',
                                    'line', 'image', 'text', 'group'])

    @grammar(str_types)
    def name(value):
        """string : Optional unique name for mark"""

    @grammar(str_types)
    def description(value):
        """string : Optional description for mark"""

    @grammar(str_types)
    def type(value):
        """string : Type of mark

        Valid types are ``'rect'``, ``'symbol'``, ``'path'``, ``'arc'``,
        ``'area'``, ``'line'``, ``'image'``, and ``'text'``.
        """
        if value not in Mark._valid_type_values:
            raise ValueError(
                'invalid mark type %s, valid types are %s' % (
                    value, Mark._valid_type_values))

    @grammar(grammar_type=MarkRef, grammar_name='from')
    def from_(value):
        """dict : Description of data to visualize

        Note that although the property has the name ``from_`` (using
        ``from`` is invalid Python syntax), the JSON will contain the
        correct property ``from``.
        """

    @grammar(MarkProperties)
    def properties(value):
        """MarkProperties : Mark property set definitions"""

    @grammar(str_types)
    def key(value):
        """string : Field to use for data binding

        When updating data dynamically, restrict dynamic transitions from
        affecting data with the given key. This can be useful for something
        like scrolling time series. See the Vega examples.
        """

    @grammar(ValueRef)
    def delay(value):
        """ValueRef, number : Transitional delay in milliseconds.
        """

    @grammar(str_types)
    def ease(value):
        """string : Type of transition easing

        Valid types are ``'linear'``, ``'quad'``, ``'cubic'``, ``'sin'``,
        ``'exp'``, ``'circle'``, and ``'bounce'``, which can be appended
        with the modifiers ``'in'``, ``'out'``, ``'in-out'``, and
        ``'out-in'``. The default is ``'cubic-in-out'``.

        See the documentation for the d3 ease function for more details.
        """

    @grammar(list)
    def marks(value):
        """list: For grouped marks, you can define a "marks" with a mark
        """

    @grammar((list, KeyedList))
    def scales(value):
        """list or KeyedList: For grouped marks, you can define a set of scales
        for within the mark groups
        """
