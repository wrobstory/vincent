# -*- coding: utf-8 -*-
"""

Charts: Constructors for different chart types in Vega grammar.

"""
import copy
from .vega import (Data, Visualization, Scale, DataRef, Mark, MarkRef,
                   MarkProperties, PropertySet, ValueRef, Axis, Transform)

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None


def data_type(data, iter_pairs, stacked):
    '''Data type check for automatic import'''
    if stacked:
        return Data.stacked(data)
    if iter_pairs:
        return Data.from_mult_iters(**data)
    if pd:
        if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            return Data.from_pandas(data)
    if isinstance(data, (list, tuple)):
        if type(data[0]) in (list, tuple):
            return Data.from_iter_pairs(data)
        else:
            return Data.from_iter(data)
    elif isinstance(data, dict):
        return Data.from_dict(data)
    else:
        raise ValueError('This data type is not supported by Vincent.')


class Chart(Visualization):
    """Abstract Base Class for all Chart types"""

    def __init__(self, data=None, iter_pairs=False, width=960, height=500, stacked=False, *args, **kwargs):
        """Create a Vega Chart

        Parameters:
        -----------
        data: Tuples, List, Dict, Pandas Series, Pandas DataFrame, or Numpy ndarray
            Input data. Tuple of paired tuples, List of single values,
            dict of key/value pairs, Pandas Series/DataFrame, Numpy ndarray
        iter_pairs: boolean, default False
            Pass true if data is a dict of two iterables. Ex:
            {'x': [0, 1, 2, 3, 4, 5], 'y': [6, 7, 8, 9, 10]}
        width: int, default 960
            Chart width
        height: int, default 500
            Chart height
        stacked: boolean, default False
            If true, data will be imported using Data.stacked

        Output:
        -------
        Vega Chart

        Example:
        -------
        >>>vis = vincent.Chart([10, 20, 30, 40, 50], width=200, height=100)

        """

        super(Chart, self).__init__(*args, **kwargs)

        self.width, self.height = width, height
        self.padding = {'top': 10, 'left': 30, 'bottom': 20, 'right': 10}

        #Data
        if data is None:
            raise ValueError('Please initialize the chart with data.')
        if not data:
            raise ValueError('The data structure is empty.')
        self.data.append(data_type(data, iter_pairs, stacked))


class Bar(Chart):
    """Vega Bar chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Bar Chart"""

        super(Bar, self).__init__(*args, **kwargs)

        #Scales
        self.scales['x'] = Scale(name='x', type='ordinal', range='width',
                                 domain=DataRef(data='table', field='data.x'))
        self.scales['y'] = Scale(name='y', range='height', nice=True,
                                 domain=DataRef(data='table', field='data.y'))
        self.axes.extend([Axis(type='x', scale='x'),
                          Axis(type='y', scale='y')])

        #Marks
        enter_props = PropertySet(x=ValueRef(scale='x', field='data.x'),
                                  y=ValueRef(scale='y', field='data.y'),
                                  width=ValueRef(scale='x', band=True, offset=-1),
                                  y2=ValueRef(scale='y', value=0))

        update_props = PropertySet(fill=ValueRef(value='steelblue'))

        mark = Mark(type='rect', from_=MarkRef(data='table'),
                    properties=MarkProperties(enter=enter_props,
                                              update=update_props))

        self.marks.append(mark)


class StackedBar(Bar):
    """Vega Stacked Bar chart"""

    def __init__(self, data_stack=None, *args, **kwargs):
        """Create a Vega Stacked Bar Chart

        data_stack: string, default None
            Data reference to stack. Defaults to ``table``



        """

        super(StackedBar, self).__init__(*args, **kwargs)

        stack = data_stack or 'table'
        self.data.append(Data(name='stats', source='table',
                              transform=[Transform(type='facet',
                                                   keys=['data.x']),
                                         Transform(type='stats',
                                                   value='data.y')]))
        self.scales['y'].domain = DataRef(data='stats', field='sum')
        self.scales.append(Scale(name='color', type='ordinal', range='category20'))

        old_mark = copy.copy(self.marks[0])
        del old_mark.from_
        mark_ref = MarkRef(data=stack, transform=[Transform(type='facet',
                                                            keys=['data.c']),
                                                  Transform(type='stack',
                                                            point='data.x',
                                                            height='data.y')])
        self.marks[0] = Mark(type='group', from_=mark_ref)




class Scatter(Bar):
    """Vega Scatter chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Scatter Chart"""

        super(Scatter, self).__init__(*args, **kwargs)

        #Scatter updates
        del self.scales[0].type
        self.scales['x'].nice = True

        del self.marks[0].properties.enter.width
        del self.marks[0].properties.enter.y2
        self.marks[0].properties.enter.stroke = ValueRef(value='#2a3140')
        self.marks[0].properties.enter.fill_opacity = ValueRef(value=0.9)
        self.marks[0].type = 'symbol'


class Line(Bar):
    """Vega Line chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Line Chart"""

        super(Line, self).__init__(*args, **kwargs)

        #Line Updates
        self.scales['x'].type = 'linear'

        del self.marks[0].properties.update
        del self.marks[0].properties.enter.width
        del self.marks[0].properties.enter.y2

        self.marks[0].type = 'line'
        self.marks[0].properties.enter.stroke = ValueRef(value='#2a3140')
        self.marks[0].properties.enter.stroke_width = ValueRef(value=2)


class Area(Line):
    """Vega Area Chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Area Chart"""

        super(Area, self).__init__(*args, **kwargs)

        self.marks[0].type = "area"
        self.marks[0].properties.enter.interpolate = ValueRef(value="monotone")
        self.marks[0].properties.enter.y2 = ValueRef(value=0, scale="y")
        self.marks[0].properties.enter.fill = ValueRef(value='#2a3140')
        fill_opac = PropertySet(fill_opacity=ValueRef(value=1))
        self.marks[0].properties.update = fill_opac








