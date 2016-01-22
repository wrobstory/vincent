# -*- coding: utf-8 -*-
"""

Transforms: Vincent ORM Class for Vega Transform types

"""
from __future__ import (print_function, division)
from vincent.core import grammar, GrammarClass
from vincent._compat import str_types


class AggregateSpec(GrammarClass):
    """
    Aggregate Specifications:
    https://github.com/vega/vega/wiki/Data-Transforms#-aggregate
    """

    @grammar(str_types)
    def field(value):
        pass

    @grammar(list)
    def ops(value):

        valid_aggregate_ops = frozenset([
            "values",
            "count",
            "valid",
            "missing",
            "distinct",
            "sum",
            "mean",
            "average",
            "variance",
            "variancep",
            "stdev",
            "stdevp",
            "median",
            "q1",
            "q3",
            "modeskew",
            "min",
            "max",
            "argmin",
            "argmax"])

        set_diff = set(value).difference(valid_aggregate_ops)
        if len(set_diff) != 0:
            raise ValueError('Ops must be'
                             ' one of {0}'.format(str(valid_aggregate_ops)))

    @grammar(list, grammar_name="as")
    def as_(value):
        pass


class Transform(GrammarClass):
    """
    Container to Transforma metrics

    As detailed in the Vega wiki:

    A data transform performs operations on a data set prior to visualization.
    Common examples include filtering and grouping (e.g., group data points
    with the same stock ticker for plotting as separate lines).
    Other examples include layout functions (e.g., stream graphs, treemaps,
    graph layout) that are run prior to mark encoding.

    All transform definitions must include a type parameter,
    which specifies the transform to apply. Each transform then has a set of
    transform-specific parameters. Transformation workflows are defined as an
    array of transforms; each transform is then evaluated
    in the specified order.

    """

    @grammar(str_types)
    def type(value):
        """string: property name in which to store the computed transform
        value.
        """

        valid_transforms = frozenset([
            'aggregate',
            'bin',
            'countpattern',
            'cross',
            'facet',
            'filter',
            'fold',
            'formula',
            'lookup',
            'sort',
            'zip',
            'force',
            'geo',
            'geopath',
            'linkpath',
            'pie',
            'stack',
            'treemap',
            'voronoi',
            'wordcloud'
        ])

        if value not in valid_transforms:
            raise ValueError('Transform type must be'
                             ' one of {0}'.format(str(valid_transforms)))

    """
    Aggregate Transform Properties:
    https://github.com/vega/vega/wiki/Data-Transforms#-aggregate
    """

    @grammar(list)
    def groupby(value):
        pass

    @grammar(list)
    def summarize(value):
        pass

    @grammar(str_types)
    def field(value):
        pass

    @grammar(list)
    def ops(value):
        pass

    @grammar(grammar_type=(list,) + str_types, grammar_name='as')
    def as_(value):
        pass

    """
    Bin Transform Properties:
    https://github.com/vega/vega/wiki/Data-Transforms#-bin
    """

    @grammar((int, float))
    def min(value):
        pass

    @grammar((int, float))
    def max(value):
        pass

    @grammar((int, float))
    def base(value):
        pass

    @grammar((int, float))
    def maxbins(value):
        pass

    @grammar((int, float))
    def step(value):
        pass

    @grammar(list)
    def steps(value):
        pass

    @grammar((int, float))
    def minstep(value):
        pass

    @grammar(list)
    def div(value):
        pass

    """
    Countpattern Transform Properties:
    https://github.com/vega/vega/wiki/Data-Transforms#-countpattern
    """

    @grammar(str_types)
    def pattern(value):
        pass

    @grammar(str_types)
    def case(value):
        pass

    @grammar(str_types)
    def stopwords(value):
        pass

    """
    Cross Transform Properties:
    https://github.com/vega/vega/wiki/Data-Transforms#-cross
    """

    @grammar(str_types)
    def width(value):
        pass

    @grammar(bool)
    def diagonal(value):
        pass

    @grammar(str_types)
    def filter(value):
        pass

    """
    Facet Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-facet
    """

    @grammar(list)
    def transform(value):
        pass

    """
    Filter Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-filter
    """

    @grammar(str_types)
    def test(value):
        pass

    """
    Fold Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-fold
    """

    @grammar(list)
    def fields(value):
        pass

    """
    Formula Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-formula
    """

    @grammar(str_types)
    def expr(value):
        pass

    """
    Lookup Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-lookup
    """

    @grammar(str_types)
    def on(value):
        pass

    @grammar(str_types, grammar_name="onKey")
    def on_key(value):
        pass

    @grammar(list)
    def keys(value):
        pass

    @grammar(str_types)
    def default(value):
        pass

    """
    Sort Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-sort
    """

    @grammar((list, str_types))
    def by(value):
        pass

    """
    Force Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-force
    """

    @grammar(str_types)
    def links(value):
        pass

    @grammar(list)
    def size(value):
        pass

    @grammar(bool)
    def bound(value):
        pass

    @grammar(bool)
    def interactive(value):
        pass

    @grammar((int, float))
    def iterations(value):
        pass

    @grammar((str_types, int))
    def charge(value):
        pass

    @grammar((str_types, int), grammar_name="linkDistance")
    def link_distance(value):
        pass

    @grammar((str_types, int), grammar_name="linkStrength")
    def link_strength(value):
        pass

    @grammar((int, float))
    def friction(value):
        pass

    @grammar((int, float))
    def theta(value):
        pass

    @grammar((int, float))
    def gravity(value):
        pass

    @grammar((int, float))
    def alpha(value):
        pass

    @grammar(dict)
    def drag(value):
        pass

    @grammar(str_types)
    def fixed(value):
        pass

    """
    Geo and GeoPath Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-geo
    """

    @grammar(str_types)
    def projection(value):
        pass

    @grammar(str_types)
    def lon(value):
        pass

    @grammar(str_types)
    def lat(value):
        pass

    @grammar(list)
    def center(value):
        pass

    @grammar(list)
    def translate(value):
        pass

    @grammar((int, float))
    def scale(value):
        pass

    @grammar((int, dict))
    def rotate(value):
        pass

    @grammar((int, float))
    def precision(value):
        pass

    @grammar(int, grammar_name="clipAngle")
    def clip_angle(value):
        pass

    """
    LinkPath Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-linkpath
    """

    @grammar(str_types, grammar_name="sourceX")
    def source_x(value):
        pass

    @grammar(str_types, grammar_name="sourceY")
    def source_y(value):
        pass

    @grammar(str_types, grammar_name="targetX")
    def target_x(value):
        pass

    @grammar(str_types, grammar_name="targetY")
    def target_y(value):
        pass

    @grammar(str_types)
    def shape(value):
        pass

    @grammar((int, float))
    def tension(value):
        pass

    """
    Pie Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-pie
    """

    @grammar(int, grammar_name="startAngle")
    def start_angle(value):
        pass

    @grammar(int, grammar_name="endAngle")
    def end_angle(value):
        pass

    @grammar((bool, list))
    def sort(value):
        pass

    """
    Stack Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-stack
    """

    @grammar(list)
    def sortby(value):
        pass

    @grammar(str_types)
    def offset(value):
        pass

    """
    Treemap Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-stack
    """

    @grammar((int, list))
    def padding(value):
        pass

    @grammar((int, float))
    def ratio(value):
        pass

    @grammar(bool)
    def round(value):
        pass

    @grammar(bool)
    def sticky(value):
        pass

    @grammar(str_types)
    def children(value):
        pass

    """
    Voroni Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-voroni
    """

    @grammar(str_types)
    def x(value):
        pass

    @grammar(str_types)
    def y(value):
        pass

    @grammar(list, grammar_name="clipExtent")
    def clip_extent(value):
        pass

    """
    Wordcloud Transform Properties
    https://github.com/vega/vega/wiki/Data-Transforms#-wordcloud
    """

    @grammar(str_types)
    def font(value):
        pass

    @grammar((int, str_types), grammar_name="fontSize")
    def font_size(value):
        pass

    @grammar(str_types, grammar_name="fontStyle")
    def font_style(value):
        pass

    @grammar(str_types, grammar_name="fontWeight")
    def font_weight(value):
        pass

    @grammar(list, grammar_name="fontScale")
    def font_scale(value):
        pass

    @grammar(str_types)
    def spiral(value):
        pass

    @grammar(str_types)
    def text(value):
        pass
