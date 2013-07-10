# -*- coding: utf-8 -*-
"""

Charts: Constructors for different chart types in Vega grammar.

"""
from .vega import (Data, Visualization, Scale, DataRef, Mark, MarkRef,
                   MarkProperties, PropertySet, ValueRef, Axis)

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None


def data_type(data, iter_pairs):
    '''Data type check for automatic import'''
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

    def __init__(self, data=None, iter_pairs=False, width=960, height=500, *args, **kwargs):
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
        self.data.append(data_type(data, iter_pairs))


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
