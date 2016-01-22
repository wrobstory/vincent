# -*- coding: utf-8 -*-
"""

PropertySet: Definition of properties for ``Mark`` objects and labels of
``Axis``objects

"""

from vincent.core import _assert_is_type, grammar, GrammarClass
from vincent.values import ValueRef
from vincent._compat import str_types


class PropertySet(GrammarClass):
    """
    Shared Visual Properties

    https://github.com/vega/vega/wiki/Marks#shared-visual-properties
    """

    @grammar(ValueRef)
    def x(value):
        pass

    @grammar(ValueRef)
    def x2(value):
        pass

    @grammar(ValueRef)
    def xc(value):
        pass

    @grammar(ValueRef)
    def width(value):
        pass

    @grammar(ValueRef)
    def y(value):
        pass

    @grammar(ValueRef)
    def y2(value):
        pass

    @grammar(ValueRef)
    def yc(value):
        pass

    @grammar(ValueRef)
    def height(value):
        pass

    @grammar(ValueRef)
    def opacity(value):
        pass

    @grammar(ValueRef)
    def fill(value):
        if value.value:
            _assert_is_type('fill.value', value.value, str_types)

    @grammar(grammar_type=ValueRef, grammar_name='fillOpacity')
    def fill_opacity(value):
        if value.value:
            _assert_is_type('fill_opacity.value', value.value,
                            (float, int))
            if value.value < 0 or value.value > 1:
                raise ValueError(
                    'fill_opacity must be between 0 and 1')

    @grammar(ValueRef)
    def stroke(value):
        if value.value:
            _assert_is_type('stroke.value', value.value, str)

    @grammar(grammar_type=ValueRef, grammar_name='strokeWidth')
    def stroke_width(value):
        if value.value:
            _assert_is_type('stroke_width.value', value.value, int)
            if value.value < 0:
                raise ValueError('stroke width cannot be negative')

    @grammar(grammar_type=ValueRef, grammar_name='strokeOpacity')
    def stroke_opacity(value):
        if value.value:
            _assert_is_type('stroke_opacity.value', value.value,
                            (float, int))
            if value.value < 0 or value.value > 1:
                raise ValueError(
                    'stroke_opacity must be between 0 and 1')

    @grammar(ValueRef, grammar_name="strokeDash")
    def stroke_dash(value):
        pass

    @grammar(ValueRef, grammar_name="strokeDashOffset")
    def stroke_dash_offset(value):
        pass

    @grammar(ValueRef)
    def size(value):
        """ValueRef : number, area of the mark in pixels

        This is the total area of a symbol. For example, a value of 500 and
        a ``shape`` of ``'circle'`` would result in circles with an area of
        500 square pixels. Only used if ``type`` is ``'symbol'``.
        """
        if value.value:
            _assert_is_type('size.value', value.value, int)
            if value.value < 0:
                raise ValueError('size cannot be negative')

    _valid_shapes = frozenset([
        "circle", "square", "cross", "diamond", "triangle-up", "triangle-down"
        ])

    @grammar(ValueRef)
    def shape(value):
        """ValueRef : string, type of symbol to use

        Possible values are ``'circle'`` (default), ``'square'``,
        ``'cross'``, ``'diamond'``, ``'triangle-up'``, and
        ``'triangle-down'``. Only used if ``type`` is ``'symbol'``.
        """
        if value.value:
            _assert_is_type('shape.value', value.value, str_types)
            if value.value not in PropertySet._valid_shapes:
                raise ValueError(value.value + ' is not a valid shape')

    @grammar(ValueRef)
    def path(value):
        """ValueRef : string, SVG path string

        This would typically be used for maps and other things where the
        path is taken from the data.
        """
        if value.value:
            _assert_is_type('path.value', value.value, str_types)

    @grammar(grammar_type=ValueRef, grammar_name='innerRadius')
    def inner_radius(value):
        """ValueRef : number, inner radius of arc in pixels

        Only used if ``type`` is ``'arc'``."""

    @grammar(grammar_type=ValueRef, grammar_name='outerRadius')
    def outer_radius(value):
        """ValueRef : number, outer radius of the arc in pixels

        Only used if ``type`` is ``'arc'``."""

    @grammar(grammar_type=ValueRef, grammar_name='startAngle')
    def start_angle(value):
        """ValueRef : number, start angle of the arc in radians

        Only used if ``type`` is ``'arc'``."""

    @grammar(grammar_type=ValueRef, grammar_name='endAngle')
    def end_angle(value):
        """ValueRef : number, end angle of the arc in radians

        Only used if ``type`` is ``'arc'``."""

    _area_methods = [
        "linear", "step-before", "step-after", "basis", "basis-open",
        "cardinal", "cardinal-open", "monotone"
        ]
    _line_methods = [
        "linear", "step-before", "step-after", "basis", "basis-open",
        "basis-closed", "bundle", "cardinal", "cardinal-open",
        "cardinal-closed", "monotone"
        ]
    _valid_methods = frozenset(_area_methods + _line_methods)

    @grammar(ValueRef)
    def interpolate(value):
        """ValueRef : string, line interpolation method to use

        Possible values for ``area`` types are `'linear'`,
        ``'step-before'``, ``'step-after'``, ``'basis'``, ``'basis-open'``,
        ``'cardinal'``, ``'cardinal-open'``, ``'monotone'``. ``line`` types
        have all values for ``area`` as well as ``'basis-closed'``,
        ``'bundle'``, and ``'cardinal-closed'``.

        Only used if ``type`` is ``'area'`` or ``'line'``.
        """
        if value.value:
            _assert_is_type('shape.value', value.value, str_types)
            if value.value not in PropertySet._valid_methods:
                raise ValueError(value.value + ' is not a valid method')

    @grammar(ValueRef)
    def tension(value):
        """ValueRef : number, tension used for interpolation

        Only used if ``type`` is ``'area'`` or ``'line'``.
        """

    @grammar(ValueRef)
    def url(value):
        """ValueRef : string, url of image

        Only used if ``type`` is ``'image'``.
        """

    _valid_align = frozenset(["left", "right", "center"])

    @grammar(ValueRef)
    def align(value):
        """ValueRef : string, horizontal alignment of mark

        Possible values are ``'left'``, ``'right'``, and ``'center'``. Only
        used if ``type`` is ``'image'`` or ``'text'``.
        """
        if value.value:
            _assert_is_type('shape.value', value.value, str_types)
            if value.value not in PropertySet._valid_align:
                raise ValueError(value.value + ' is not a valid alignment')

    _valid_baseline = frozenset(["top", "middle", "bottom"])

    @grammar(ValueRef)
    def baseline(value):
        """ValueRef : string, vertical alignment of mark

        Possible values are ``'top'``, ``'middle'``, and ``'bottom'``. Only
        used if ``type`` is ``'image'`` or ``'text'``.
        """
        if value.value:
            _assert_is_type('shape.value', value.value, str_types)
            if value.value not in PropertySet._valid_baseline:
                raise ValueError(value.value + ' is not a valid baseline')

    @grammar(ValueRef)
    def text(value):
        """ValueRef : string, text to display

        Only used if ``type`` is ``'text'``."""

    @grammar(ValueRef)
    def dx(value):
        """ValueRef : number, horizontal margin between text and anchor
        point in pixels

        Ignored if ``align`` is ``'center'``. Only used if ``type`` is
        ``'text'``.
        """

    @grammar(ValueRef)
    def dy(value):
        """ValueRef : number, vertical margin between text and anchor
        point in pixels

        Ignored if ``baseline`` is ``'middle'``. Only used if ``type`` is
        ``'text'``.
        """

    @grammar(ValueRef)
    def angle(value):
        """ValueRef : number, rotation of text in degrees

        Only used if ``type`` is ``'text'``.
        """

    @grammar(ValueRef)
    def font(value):
        """ValueRef : string, typeface for text

        Only used if ``type`` is ``'text'``.
        """

    @grammar(grammar_type=ValueRef, grammar_name='fontSize')
    def font_size(value):
        """ValueRef : number, font size in pixels

        Only used if ``type`` is ``'text'``.
        """

    @grammar(grammar_type=ValueRef, grammar_name='fontWeight')
    def font_weight(value):
        """ValueRef : string, font weight

        Should be a valid SVG font weight. Only used if ``type`` is
        ``'text'``.
        """

    @grammar(grammar_type=ValueRef, grammar_name='fontStyle')
    def font_style(value):
        """ValueRef : string, font style

        Should be a valid SVG font style. Only used if ``type`` is
        ``'text'``.
        """
