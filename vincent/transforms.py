# -*- coding: utf-8 -*-
"""

Transforms: Vincent Data Class for Vega Transform types

"""
from __future__ import (print_function, division)
from .core import grammar, GrammarClass
from ._compat import str_types


class Transform(GrammarClass):
    """Container to Transforma metrics

    As detailed in the Vega wiki:

    "A data transform performs operations on a data set prior to visualization.
    Common examples include filtering and grouping (e.g., group data points
    with the same stock ticker for plotting as separate lines).

    All transform definitions must include a "type" parameter,
    which specifies the transform to apply.
    Each transform then has a set of transform-specific parameters."

    """

    @grammar(str_types)
    def type(value):
        """string: property name in which to store the computed transform
        value.

        The valid transform types are as follows:
        'array', 'copy', 'cross', 'facet', 'filter', 'flatten', 'fold',
        'formula', 'slice', 'sort', 'stats', 'truncate', 'unique', 'window',
        'zip', 'force', 'geo', 'geopath', 'link', 'pie', 'stack', 'treemap',
        'wordcloud'

        """

        valid_transforms = frozenset([
            'array', 'copy', 'cross', 'facet', 'filter',
            'flatten', 'fold', 'formula', 'slice', 'sort', 'stats',
            'truncate', 'unique', 'window', 'zip', 'force', 'geo', 'geopath',
            'link', 'pie', 'stack', 'treemap', 'wordcloud'
        ])

        if value not in valid_transforms:
            raise ValueError('Transform type must be'
                             ' one of {0}'.format(str(valid_transforms)))

    @grammar(list)
    def fields(value):
        """list: Can take data references or object references

        Only used if ``type`` is ``array`` or ``copy``

        """

    @grammar(grammar_type=str_types, grammar_name='from')
    def from_(value):
        """str: The name of the object to copy values from

        Only used if ``type`` is ``copy``

        """

    @grammar(grammar_type=(list,) + str_types, grammar_name='as')
    def as_(value):
        """list: The field names to copy the values to.

        Can be used with the following ``type``:
        ``copy``
        ``unique``
        ``zip``

        """

    @grammar(list)
    def keys(value):
        """list: Each key value corresponds to a single facet in the output.

        Only used if ``type`` is ``facet``
        """

    @grammar(str_types)
    def sort(value):
        """string: Optional for sorting facet values

        Only used if ``type`` is ``facet``
        """

    @grammar(str_types)
    def test(value):
        """string: A string containing a javascript filtering expression.

        Ex: d.data.y >= 3

        Only used if ``type`` is ``filter``
        """

    @grammar(str_types)
    def field(value):
        """string: Property name to store computed formula value.

        Only used if ``type`` is ``formula`` or ``unique``

        See: https://github.com/trifacta/vega/wiki/Data-Transforms#-formula
        """

    @grammar(str_types)
    def expr(value):
        """string: Javascript expression of a formula, referencing the data as
        d.

        Only used if ``type`` is formula

        See: https://github.com/trifacta/vega/wiki/Data-Transforms#-formula
        """

    @grammar(str_types + (list,))
    def by(value):
        """str, list: a field or list of fields to sort. Can prepend with - to
        sort descending.

        Only used if ``type`` is ``sort``
        """

    @grammar(str_types)
    def value(value):
        """str: Field for which to compute statistics.

        Only used if ``type`` is ``stats``
        """

    @grammar(bool)
    def median(value):
        """boolean: If true, median statistic will also be computed.

        Only used if ``type`` is stats``
        """

    @grammar(grammar_type=str_types, grammar_name='with')
    def with_(value):
        """string: Name of dataset to zip to current dataset

        Only used if ``type`` is ``zip``
        """

    @grammar(str_types)
    def key(value):
        """string: Primary dataset field to match to secondary data

        Only used if ``type`` is ``zip``
        """

    @grammar(grammar_type=str_types, grammar_name='withKey')
    def with_key(value):
        """string: Field in secondary dataset to match to primary

        Only used if ``type`` is ``zip``
        """

    @grammar((int, float,) + str_types)
    def default(value):
        """Default value to use if no matching key value is found for zip
        transformation"""

    @grammar(str_types)
    def links(value):
        """string: Name of link (edge) data set.

        To be used with ``force`` types
        """

    @grammar((int, list))
    def size(value):
        """list: Dimensions of force layout
        Number: The size (in number of elements) of the sliding window.
            Defaults to 2.

        To be used with ``force`` types
        """

    @grammar(int)
    def iterations(value):
        """int: Number of iterations to run force directed layout.

        To be used with ``force`` types
        """

    @grammar((int,) + str_types)
    def charge(value):
        """int or string: Strength of the charge each node exerts.

        To be used with ``force`` types
        """

    @grammar(grammar_type=(int,) + str_types, grammar_name='linkDistance')
    def link_distance(value):
        """int or string: Determines lenght of the edges, in pixels.

        To be used with ``force`` types
        """

    @grammar(grammar_type=(int,) + str_types, grammar_name='linkStrength')
    def link_strength(value):
        """int or string: Determines the tension of the edges.

        To be used with ``force`` types
        """

    @grammar((int, float))
    def friction(value):
        """int or float: Strength of friction force to stabilize layout

        To be used with ``force`` types
        """

    @grammar((int, float))
    def theta(value):
        """int or float: theta parameter for the Barnes-Hut algorithm.

        To be used with ``force`` types
        """

    @grammar((int, float))
    def gravity(value):
        """int or float: Strength of pseudo-gravity force

        To be used with ``force`` types
        """

    @grammar((int, float))
    def alpha(value):
        """int or float: "temperature" parameter to determine node position
        adjustment

        To be used with ``force`` types
        """

    @grammar(str_types)
    def point(value):
        """string: Data field determining the points at which to stack. When
        stacked vertically, these are the x-coords.

        To be used with ``stack`` types
        """

    @grammar(str_types)
    def height(value):
        """string: Data field determining thickness, or height of stacks.

        To be used with ``stack`` types
        """

    @grammar(str_types)
    def offset(value):
        """string: Baseline offset style. Must be one of the following:

        ``zero``, ``silhouette``, ``wiggle``, ``expand``

         To be used with ``stack`` types
         """
        offsets = ['zero', 'silhouette', 'wiggle', 'expand']
        if value not in offsets:
            raise ValueError('offset must be one of {0}'.format(offsets))

    @grammar(str_types)
    def order(value):
        """str: The sort order for stack layers. Must be one of the following:

        ``default``, ``reverse``, ``inside-out``

        To be used with ``stack`` types
        """
        orders = ['default', 'reverse', 'inside-out']
        if value not in orders:
            raise ValueError('order must be one of {0}'.format(orders))

    @grammar(str_types)
    def projection(value):
        """str: Cartographic projection. Accepts any projection supported by
        the D3 projection plug-in:

        https://github.com/mbostock/d3/wiki/Geo-Projections
        """

    @grammar(list)
    def center(value):
        """Center of the projection. Should be length=2"""

        if len(value) != 2:
            raise ValueError('len(center) must = 2')

    @grammar(list)
    def translate(value):
        """Translation of the projection. Should be length=2"""

        if len(value) != 2:
            raise ValueError('len(center) must = 2')

    @grammar(int)
    def scale(value):
        """The scale of the projection"""

        if value < 0:
            raise ValueError('Scale cannot be negative.')

    @grammar((int, str_types, dict))
    def rotate(value):
        """The rotation of the projection or rotation define of word cloud
        """

        if isinstance(value, int):
            if value < 0:
                raise ValueError('The rotation cannot be negative.')

    @grammar(str_types)
    def font(value):
        """str: Font of word cloud.
        """

    @grammar(grammar_type=str_types, grammar_name='fontSize')
    def font_size(value):
        """str: The font size field of word cloud.
        """

    @grammar(str_types)
    def text(value):
        """str: The text field of word cloud.
        """

    @grammar(bool)
    def diagonal(value):
        """True: Elements on diagonal will be included in cross product.
        False (default): Elements on diagonal will not be included in cross
        product.
        """

    @grammar(bool)
    def assign(value):
        """bool: If true, a stats property will be added to each individual
        data element. This property references an object containing all the
        computed statistics. This option is useful if you want construct
        downstream formulas that reference both individual values and aggregate
        statistics.
        """

    @grammar(str_types)
    def output(value):
        """str: The name of the field in which to store the truncated value.
        Defaults to "truncate".
        """

    @grammar(int)
    def limit(value):
        """int: The maximum length of the truncated string.
        """

    @grammar(str_types)
    def ellipsis(value):
        """str: The text to use as an ellipsis for truncated text.
        Defaults to "...".
        """

    @grammar(bool)
    def wordbreak(value):
        """bool: If true, the truncation algorithm will truncate along word
        boundaries.
        """

    @grammar((int, float))
    def step(value):
        """Number: The step size (in number of elements) by which to advance
        the window per frame. Defaults to 1.
        """

    @grammar((int, float))
    def precision(value):
        """Number: The desired precision of the projection.
        """

    @grammar((int, float), grammar_name='clipAngle')
    def clip_angle(value):
        """Number: The clip angle of the projection.
        """

    @grammar(str_types)
    def shape(value):
        """str: A string describing the path shape to use. One of
        "line" (default), "curve", "diagonal", "diagonalX", or "diagonalY".
        """
        link_shapes = frozenset([
            "line", "curve", "diagonal", "diagonalX", "diagonalY"
            ])
        if value not in link_shapes:
            raise ValueError(
                'Link shape must be one of %s' % (str(link_shapes),)
                )

    @grammar(grammar_type=str_types, grammar_name='fontWeight')
    def font_weight(value):
        """str: The font weight (e.g., "bold") to use.
        """

    @grammar((int, list))
    def padding(value):
        """The padding (in pixels) to provide around text in the word cloud.
        The padding value can either be a single number or an array of four
        numbers [top, right, bottom, left]. The default padding is zero pixels.
        """

    @grammar(str_types)
    def lon(value):
        """string: The input longitude values.
        """

    @grammar(str_types)
    def lat(value):
        """string: The input latitude values.
        """

    @grammar(str_types)
    def source(value):
        """string: The data field that references the source node for this
        link.
        """

    @grammar(str_types)
    def target(value):
        """string: The data field that references the target node for this
        link.
        """
