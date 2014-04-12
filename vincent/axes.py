# -*- coding: utf-8 -*-
"""

Axes: Classes for defining Vega axis properties

"""
from .core import grammar, GrammarClass
from .properties import PropertySet
from ._compat import str_types


class AxisProperties(GrammarClass):
    """Definitions for the rendering of axes

    Like Marks, axis properties can be broken into various subcomponents,
    but instead of events, the axes are divided into major ticks, minor
    ticks, labels, and the axis itself.
    """
    @grammar(grammar_type=PropertySet, grammar_name='majorTicks')
    def major_ticks(value):
        """PropertySet : Definition of major tick marks"""

    @grammar(grammar_type=PropertySet, grammar_name='minorTicks')
    def minor_ticks(value):
        """PropertySet : Definition of minor tick marks"""

    @grammar(PropertySet)
    def labels(value):
        """PropertySet : Definition of marks for axis labels"""

    @grammar(PropertySet)
    def title(value):
        """PropertySet : Definition of marks for axis labels"""

    @grammar(PropertySet)
    def axis(value):
        """PropertySet : Definition of axis line style"""


class Axis(GrammarClass):
    """Definitions for axes

    Axes are visual cues that the viewer uses to interpret the marks
    representing the data itself.
    """
    @grammar(str_types)
    def type(value):
        """string : Type of axis - ``'x'`` or ``'y'``"""
        if value not in ('x', 'y'):
            raise ValueError('Axis.type must be "x" or "y"')

    @grammar(str_types)
    def title(value):
        """string: Axis title"""

    @grammar(grammar_type=int, grammar_name='titleOffset')
    def title_offset(value):
        """int: Offset in pixels from the axis on which to place the title"""

    @grammar(bool)
    def grid(value):
        """bool: If True, gridlines are created"""

    @grammar(str_types)
    def layer(value):
        """string: A string indicating if the axis (and any gridlines) should
        be placed above or below the data marks.
        Can only be "front" (default) or "back".
        """
        if value not in ("front", "back"):
            raise ValueError("Axis.layer must be front or back")

    @grammar(str_types)
    def scale(value):
        """string : Name of scale used for axis"""

    @grammar(str_types)
    def orient(value):
        """string : Orientation of the axis

        Should be one of ``'top'``, ``'bottom'``, ``'left'``, or ``'right'``.
        """

    @grammar(str_types)
    def format(value):
        """string : Formatting to use for axis labels

        See d3's formatting documentation for format pattern.
        """

    @grammar(int)
    def ticks(value):
        """int : Number of ticks to use"""

    @grammar(list)
    def values(value):
        """list of objects in scale's domain : Explicit definitions for
        values

        Values should be in the domain of the Axis's scale. Custom ticks can
        be used by setting ``properties``.
        """

    @grammar((int, float))
    def subdivide(value):
        """int or float : Number of minor ticks in between major ticks

        Only valid for quantitative scales.
        """

    @grammar(grammar_type=(int), grammar_name='tickPadding')
    def tick_padding(value):
        """int : Pixels between ticks and text labels"""

    @grammar(grammar_type=(int), grammar_name='tickSize')
    def tick_size(value):
        """int : Size in pixels of all ticks"""

    @grammar(grammar_type=(int), grammar_name='tickSizeMajor')
    def tick_size_major(value):
        """int : Size in pixels of major ticks"""

    @grammar(grammar_type=(int), grammar_name='tickSizeMinor')
    def tick_size_minor(value):
        """int : Size in pixels of minor ticks"""

    @grammar(grammar_type=(int), grammar_name='tickSizeEnd')
    def tick_size_end(value):
        """int : Size in pixels of end ticks"""

    @grammar(int)
    def offset(value):
        """int : Offset in pixels to displace the edge of the axis from the
        referenced area
        """

    @grammar(AxisProperties)
    def properties(value):
        """AxisProperties : Custom styling for ticks and tick labels
        """
