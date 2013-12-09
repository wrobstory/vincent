# -*- coding: utf-8 -*-
"""

Scales: Classes to define Vega scales

"""
from .core import grammar, GrammarClass
from ._compat import str_types


class DataRef(GrammarClass):
    """Definitions for how data is referenced by scales

    Data can be referenced in multiple ways, and sometimes it makes sense to
    reference multiple data fields at once.
    """
    @grammar(str_types)
    def data(value):
        """string : Name of data-set containing the domain values"""

    @grammar((list,) + str_types)
    def field(value):
        """string or list of strings : Reference to desired data field(s)

        If multiple fields are given, then the values of all fields are
        included in the domain.
        """


class Scale(GrammarClass):
    """Definitions for mapping from data space to visual space

    Scales determine the way in which data is mapped from a data space (such
    as numbers, time stamps, etc.) to a visual space (length of a line,
    height of a bar, etc.), for both independent and dependent variables.
    """
    @grammar(str_types)
    def name(value):
        """string : Unique name for the scale

        This is used for referencing by other components (mainly ``Mark``).
        """

    @grammar(str_types)
    def type(value):
        """string : Type of the scale

        Valid types are as follows:

        * ``'ordinal'``: ordinal scale types
        * ``'time'`` or ``'utc'``: time scale types
        * ``'linear'``, ``'log'``, ``'pow'``, ``'sqrt'``, ``'quantile'``,
          ``'quantize'``, and ``'threshold'``: quantitative scale types

        For time scales, the value should be a Javascript-style numeric
        value of seconds.  ``'time'`` implies the value is in local time.

        If unspecified, then the scale is assumed to be linear. See the d3
        documentation for scale type details.
        """

    @grammar((list, DataRef))
    def domain(value):
        """list or DataRef : Domain of the scale
        """

    @grammar(grammar_type=(float, int, DataRef), grammar_name='domainMin')
    def domain_min(value):
        """float, int, or DataRef : Minimum domain value

        Only used for quantitative/time scales. This takes precedence over
        the minimum of the ``domain`` property.
        """

    @grammar(grammar_type=(float, int, DataRef),
             grammar_name='domainMax')
    def domain_max(value):
        """float, int, or DataRef : Maximum domain value

        Only used for quantitative/time scales. This takes precedence over
        the maximum of the ``domain`` property.
        """

    @grammar((list,) + str_types)
    def range(value):
        """list or string : Range of the scale

        For quantitative scales, the range may be specified as a two-element
        list of min/max values. For ordinal scales, the range should be a
        list of output values mapped to the input values.

        String values may be used to automatically set a range:
            - ``'width'`` - Set the range to the width of the visualization
            - ``'height'`` - Set the range to the height of the visualization
            - ``'shapes'`` - Equivalent to the symbol types ``['circle',
              'cross', 'diamond', 'square', 'triangle-down',
              'triangle-up']``
            - ``'category10'`` - A pre-determined 10-color pallet
            - ``'category20'`` - A pre-determined 20-color pallet
        """

    @grammar(grammar_type=(float, int, DataRef), grammar_name='rangeMin')
    def range_min(value):
        """float, int, or DataRef : Minimum range value

        Only used for quantitative/time scales. This takes precedence over
        the minimum of the ``range`` property.
        """

    @grammar(grammar_type=(float, int, DataRef), grammar_name='rangeMax')
    def range_max(value):
        """float, int, or DataRef : Maximum range value

        Only used for quantitative/time scales. This takes precedence over
        the maximum of the ``range`` property.
        """

    @grammar(bool)
    def reverse(value):
        """boolean : If True, flip the scale range"""

    @grammar(bool)
    def round(value):
        """boolean : If True, numeric output values are rounded to
        integers"""

    @grammar(bool)
    def points(value):
        """boolean : If True, distribute ordinal values over evenly spaced
        points between ``range_min`` and ``range_max``

        Ignored for non-ordinal scales.
        """

    @grammar(bool)
    def clamp(value):
        """boolean : If True, values that exceed the domain are clamped to
        within the domain

        Ignored for ordinal scales.
        """

    @grammar((bool,) + str_types)
    def nice(value):
        """boolean or string : scale the domain to a more human-friendly set

        If the scale ``type`` is ``'time'`` or ``'utc'``, then the value
        should be one of ``'second'``, ``'minute'``, ``'hour'``, ``'day'``,
        ``'week'``, ``'month'``, or ``'year'``.

        If the scale ``type`` is a quantitative scale, then the value should
        be a boolean. The input values are rounded to a more human-friendly
        value. The details of the rounding are in the d3 documentation.

        Ignored for ordinal scales.
        """

    @grammar((float, int))
    def exponent(value):
        """float or int : Exponent for ``'pow'`` scale types

        Ignored for all scale types other than ``'pow'``.
        """

    @grammar(bool)
    def zero(value):
        """boolean : If True, include zero in the domain

        Only valid for quantitative scale types. This is useful if the
        domain is defined as a DataRef that may not include 0 exactly.
        """

    @grammar((float, int))
    def padding(value):
        """string: Ordinal element padding

        Only valid for ordinal scale types
        """
