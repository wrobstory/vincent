# -*- coding: utf-8 -*-
"""

Charts: Constructors for different chart types in Vega grammar.

"""
from .visualization import Visualization
from .data import Data
from .transforms import Transform
from .values import ValueRef
from .properties import PropertySet
from .scales import DataRef, Scale
from .marks import MarkProperties, MarkRef, Mark
from .axes import Axis
from .colors import brews

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None


def data_type(data, grouped=False, columns=None, key_on='idx', iter_idx=None):
    '''Data type check for automatic import'''
    if iter_idx:
        return Data.from_mult_iters(idx=iter_idx, **data)
    if pd:
        if isinstance(data, (pd.Series, pd.DataFrame)):
            return Data.from_pandas(data, grouped=grouped, columns=columns,
                                    key_on=key_on)
    if isinstance(data, (list, tuple, dict)):
            return Data.from_iter(data)
    else:
        raise ValueError('This data type is not supported by Vincent.')


class Chart(Visualization):
    """Abstract Base Class for all Chart types"""

    def __init__(self, data=None, columns=None, key_on='idx', iter_idx=None,
                 width=960, height=500, grouped=False, no_data=False,
                 *args, **kwargs):
        """Create a Vega Chart

        Parameters
        -----------
        data: Tuples, List, Dict, Pandas Series, or Pandas DataFrame
            Input data. Tuple of paired tuples, List of single values,
            dict of key/value pairs, Pandas Series/DataFrame, Numpy ndarray
        columns: list, default None
            Pandas DataFrame columns to plot.
        key_on: string, default 'idx'
            Pandas DataFrame column to key on, if not index
        iter_index: string, default None
            Pass an index key if data is a dict of multiple iterables. Ex:
            {'x': [0, 1, 2, 3, 4, 5], 'y': [6, 7, 8, 9, 10]}
        width: int, default 960
            Chart width
        height: int, default 500
            Chart height
        grouped: boolean, default False
            Pass true for grouped charts. Currently only enabled for Pandas
            DataFrames
        no_data: boolean, default False
            Pass true to indicate that data is not being passed. For example,
            this is used for the Map class, where geodata is passed as a
            separate attibute

        Returns
        -------
        Vega Chart

        Example
        -------
        >>>vis = vincent.Chart([10, 20, 30, 40, 50], width=200, height=100)

        """

        super(Chart, self).__init__(*args, **kwargs)

        self.width, self.height = width, height
        self.padding = "auto"
        self.columns = columns
        self._is_datetime = False

        # Data
        if data is None and not no_data:
            raise ValueError('Please initialize the chart with data.')

        if not no_data:
            if isinstance(data, (list, tuple, dict)):
                if not data:
                    raise ValueError('The data structure is empty.')
            if isinstance(data, (pd.Series, pd.DataFrame)):
                if isinstance(data.index, pd.DatetimeIndex):
                    self._is_datetime = True

            # Using a vincent KeyedList here
            self.data['table'] = (
                data_type(data, grouped=grouped, columns=columns,
                          key_on=key_on, iter_idx=iter_idx)
                )


class Line(Chart):
    """Vega Line chart

    Support line and multi-lines chart.
    """

    def __init__(self, *args, **kwargs):
        """Create a Vega Line Chart"""

        super(Line, self).__init__(*args, **kwargs)

        # Scales
        x_type = 'time' if self._is_datetime else 'linear'
        self.scales += [
            Scale(name='x', type=x_type, range='width',
                  domain=DataRef(data='table', field="data.idx")),
            Scale(name='y', range='height', nice=True,
                  domain=DataRef(data='table', field="data.val")),
            Scale(name='color', type='ordinal',
                  domain=DataRef(data='table', field='data.col'),
                  range='category20')
        ]

        # Axes
        self.axes += [Axis(type='x', scale='x'),
                      Axis(type='y', scale='y')]

        # Marks
        from_ = MarkRef(
            data='table',
            transform=[Transform(type='facet', keys=['data.col'])])
        enter_props = PropertySet(
            x=ValueRef(scale='x', field="data.idx"),
            y=ValueRef(scale='y', field="data.val"),
            stroke=ValueRef(scale="color", field='data.col'),
            stroke_width=ValueRef(value=2))
        marks = [Mark(type='line',
                      properties=MarkProperties(enter=enter_props))]
        mark_group = Mark(type='group', from_=from_, marks=marks)
        self.marks.append(mark_group)


class Scatter(Chart):
    """Vega Scatter chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Scatter Chart"""

        super(Scatter, self).__init__(*args, **kwargs)

        # Scales
        x_type = 'time' if self._is_datetime else 'linear'
        self.scales += [
            Scale(name='x', type=x_type, range='width',
                  domain=DataRef(data='table', field="data.idx")),
            Scale(name='y', range='height', nice=True,
                  domain=DataRef(data='table', field="data.val")),
            Scale(name='color', type='ordinal',
                  domain=DataRef(data='table', field='data.col'),
                  range='category20')
        ]

        # Axes
        self.axes += [Axis(type='x', scale='x'),
                      Axis(type='y', scale='y')]

        # Marks
        from_ = MarkRef(
            data='table',
            transform=[Transform(type='facet', keys=['data.col'])])
        enter_props = PropertySet(
            x=ValueRef(scale='x', field="data.idx"),
            y=ValueRef(scale='y', field="data.val"),
            size=ValueRef(value=100),
            fill=ValueRef(scale="color", field='data.col'))
        marks = [Mark(type='symbol',
                      properties=MarkProperties(enter=enter_props))]
        mark_group = Mark(type='group', from_=from_, marks=marks)
        self.marks.append(mark_group)


class Bar(Chart):
    """Vega Bar chart

    Support both bar and stacked bar charts.
    """

    def __init__(self, *args, **kwargs):
        """Create a Vega Bar Chart"""

        super(Bar, self).__init__(*args, **kwargs)

        # Scales
        self.scales += [
            Scale(name='x', type='ordinal', range='width', zero=False,
                  domain=DataRef(data='table', field='data.idx')),
            Scale(name='y', range='height', nice=True,
                  domain=DataRef(data='stats', field='sum')),
            Scale(name='color', type='ordinal', range='category20',
                  domain=DataRef(data='table', field='data.col'))
        ]

        # Axes
        self.axes += [Axis(type='x', scale='x'),
                      Axis(type='y', scale='y')]

        # Stats Data
        stats_transform = [Transform(type='facet', keys=['data.idx']),
                           Transform(type='stats', value='data.val')]
        stats_data = Data(name='stats', source='table',
                          transform=stats_transform)
        self.data.append(stats_data)

        # Marks
        from_transform = [
            Transform(type='facet', keys=['data.col']),
            Transform(type='stack', point='data.idx', height='data.val')
        ]
        from_ = MarkRef(data='table', transform=from_transform)
        enter_props = PropertySet(
            x=ValueRef(scale='x', field='data.idx'),
            y=ValueRef(scale='y', field='y'),
            y2=ValueRef(scale='y', field='y2'),
            width=ValueRef(scale='x', band=True, offset=-1),
            fill=ValueRef(scale='color', field='data.col'))
        marks = [Mark(type='rect',
                      properties=MarkProperties(enter=enter_props))]
        mark_group = Mark(type='group', from_=from_, marks=marks)
        self.marks.append(mark_group)
StackedBar = Bar


class Area(Chart):
    """Vega Area Chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Area Chart"""

        super(Area, self).__init__(*args, **kwargs)

        # Scales
        x_type = 'time' if self._is_datetime else 'linear'
        self.scales += [
            Scale(name='x', type=x_type, range='width', zero=False,
                  domain=DataRef(data='table', field="data.idx")),
            Scale(name='y', range='height', nice=True,
                  domain=DataRef(data='stats', field='sum')),
            Scale(name='color', type='ordinal', range='category20',
                  domain=DataRef(data='table', field='data.col'))
        ]

        # Axes
        self.axes += [Axis(type='x', scale='x'),
                      Axis(type='y', scale='y')]

        # Stats Data
        stats_transform = [Transform(type='facet', keys=['data.idx']),
                           Transform(type='stats', value='data.val')]
        stats_data = Data(name='stats', source='table',
                          transform=stats_transform)
        self.data.append(stats_data)

        # Marks
        from_transform = [
            Transform(type='facet', keys=['data.col']),
            Transform(type='stack', point='data.idx', height='data.val')
        ]
        from_ = MarkRef(data='table', transform=from_transform)
        enter_props = PropertySet(
            x=ValueRef(scale='x', field='data.idx'),
            y=ValueRef(scale='y', field='y'),
            y2=ValueRef(scale='y', field='y2'),
            interpolate=ValueRef(value='monotone'),
            fill=ValueRef(scale='color', field='data.col'))
        marks = [Mark(type='area',
                      properties=MarkProperties(enter=enter_props))]
        mark_group = Mark(type='group', from_=from_, marks=marks)
        self.marks.append(mark_group)
StackedArea = Area


class GroupedBar(Chart):
    """Vega Grouped Bar Chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Grouped Bar Chart"""

        super(GroupedBar, self).__init__(*args, **kwargs)

        # Scales
        self.scales += [
            Scale(name='x', type='ordinal', range='width', padding=0.2,
                  domain=DataRef(data='table', field='data.idx')),
            Scale(name='y', range='height', nice=True,
                  domain=DataRef(data='table', field="data.val")),
            Scale(name='color', type='ordinal', range='category20',
                  domain=DataRef(data='table', field='data.col'))
        ]

        # Axes
        self.axes += [Axis(type='x', scale='x'),
                      Axis(type='y', scale='y')]

        # Marks
        mark_props = MarkProperties(
            enter=PropertySet(
                x=ValueRef(scale='pos', field='data.col'),
                y=ValueRef(scale='y', field='data.val'),
                y2=ValueRef(scale='y', value=0),
                width=ValueRef(scale='pos', band=True, offset=-1),
                fill=ValueRef(scale='color', field='data.col')))

        mark_group_marks = [Mark(type='rect', properties=mark_props)]
        mark_group_from = MarkRef(
            data='table',
            transform=[Transform(type='facet', keys=['data.idx'])])
        mark_group_props = MarkProperties(
            enter=PropertySet(x=ValueRef(scale='x', field='key'),
                              width=ValueRef(scale='x', band=True)))
        mark_group_scales = [Scale(name="pos", range="width", type="ordinal",
                             domain=DataRef(field="data.col"))]
        mark_group = Mark(
            type='group', from_=mark_group_from,
            properties=mark_group_props, scales=mark_group_scales,
            marks=mark_group_marks)
        self.marks.append(mark_group)


class Map(Chart):
    """Vega Simple Map"""

    def __init__(self, data=None, geo_data=None, projection="winkel3",
                 center=None, translate=None, scale=None, rotate=None,
                 data_bind=None, data_key=None, map_key=None,
                 brew='GnBu', *args, **kwargs):
        """Create a Vega Map. Takes standard Chart class parameters.

        Note: Data binding only works with Pandas DataFrames right now.

        `geo_data` needs to be passed as a list of dicts with the following
        format:
        {
            name: data name
            url: path_to_data,
            feature: TopoJSON object set (ex: 'countries')
        }

        Parameters
        ----------
        data: Tuples, List, Dict, Pandas Series, or Pandas DataFrame
            Input data. Tuple of paired tuples, List of single values,
            dict of key/value pairs, Pandas Series/DataFrame, Numpy ndarray.
            Used to bind to map for choropleth mapping.
        geo_data: list, default None
            List of dicts
        projection: string, default "winkel3"
            Map projection
        center: list, default None
            Two element list with projection center
        translate: list, default None
            Two element list with projection translation
        scale: integer, default None
            Projection scale
        rotate: integer, default None
            Projection rotation
        data_bind:str, default None
            Column you want to visualize. E.g. the data value you are binding
            to the map
        data_key: str, default None
            If passing data to bind to the map, data field to key-on. For a
            Pandas DataFrame, this would be the column name.
        map_key: dict, default None
            Key: The geo-data you are keying to. Value: The map property that
            you are keying your data on. This can be nested with dot notation.
            Ex: 'properties.name'
        brew: str, default GnBu
            Color brewer abbreviation. See colors.py

        Returns
        -------
        Vega Chart

        """

        self.raw_data = data
        self.data_key = data_key

        super(Map, self).__init__(no_data=True, *args, **kwargs)

        # Don't want to pass None to property setters
        geo_kwargs = {}
        for param in [('projection', projection), ('center', center),
                      ('translate', translate), ('scale', scale),
                      ('rotate', rotate)]:
            if param[1]:
                geo_kwargs[param[0]] = param[1]

        if not translate:
            geo_kwargs['translate'] = [self.width/2, self.height/2]

        # Add Data
        for dat in geo_data:
            # Data
            transforms = []
            if data is not None and list(map_key.keys())[0] == dat['name']:
                get_brewer = True
                if not data_key or not data_bind:
                    raise ValueError('If passing data, '
                                     'you must pass data cols to key/bind on')
                self.data['table'] = Data.keypairs(
                    data, columns=[data_key, data_bind]
                    )
                key_join = '.'.join(['data', map_key[dat['name']]])
                data_transform = Transform(
                    type='zip', key=key_join, with_='table',
                    with_key='data.x', as_='value', default='noval'
                    )
                transforms.append(data_transform)
                null_trans = Transform(
                    type='filter', test="d.path!='noval' && d.value!='noval'"
                    )
                transforms.append(null_trans)
            else:
                get_brewer = False

            geo_transform = Transform(
                type='geopath', value="data", **geo_kwargs
                )
            transforms.append(geo_transform)
            self.data[dat['name']] = Data(
                name=dat['name'], url=dat['url'], transform=transforms
                )
            if dat.get('feature'):
                self.data[dat['name']].format = {
                    'type': "topojson",
                    'feature': dat['feature']
                    }

            # Marks

            geo_from = MarkRef(data=dat['name'])

            enter_props = PropertySet(
                stroke=ValueRef(value='#000000'),
                path=ValueRef(field='path')
                )

            if get_brewer:
                update_props = PropertySet(
                    fill=ValueRef(scale='color', field='value.data.y')
                    )
                domain = [Data.serialize(data[data_bind].min()),
                          Data.serialize(data[data_bind].quantile(0.95))]
                scale = Scale(name='color', type='quantize', domain=domain,
                              range=brews[brew])
                self.scales['color'] = scale
            else:
                update_props = PropertySet(fill=ValueRef(value='steelblue'))

            mark_props = MarkProperties(enter=enter_props, update=update_props)

            self.marks.append(
                Mark(type='path', from_=geo_from, properties=mark_props)
                )

    def rebind(self, column=None, brew='GnBu'):
        """Bind a new column to the data map

        Parameters
        ----------
        column: str, default None
            Pandas DataFrame column name
        brew: str, default None
            Color brewer abbreviation. See colors.py

        """
        self.data['table'] = Data.keypairs(
            self.raw_data, columns=[self.data_key, column])
        domain = [Data.serialize(self.raw_data[column].min()),
                  Data.serialize(self.raw_data[column].quantile(0.95))]
        scale = Scale(name='color', type='quantize', domain=domain,
                      range=brews[brew])
        self.scales['color'] = scale


class Pie(Chart):
    """Vega Pie chart"""

    def __init__(self, data=None, inner_radius=0, outer_radius=None,
                 *args, **kwargs):
        """Create a Vega Pie Chart"""

        super(Pie, self).__init__(data, *args, **kwargs)

        outer_radius = outer_radius or min(self.width, self.height) / 2

        self.scales["color"] = Scale(
            name="color", type="ordinal", range="category10",
            domain=DataRef(data="table", field="data.idx"))

        transform = MarkRef(
            data="table", transform=[Transform(type="pie", value="data.val")])

        enter_props = PropertySet(
            x=ValueRef(group="width", mult=0.5),
            y=ValueRef(group="height", mult=0.5),
            start_angle=ValueRef(field="startAngle"),
            end_angle=ValueRef(field="endAngle"),
            inner_radius=ValueRef(value=inner_radius),
            outer_radius=ValueRef(value=outer_radius),
            stroke=ValueRef(value="white"),
            fill=ValueRef(scale="color", field="data.idx"))

        mark = Mark(type="arc", from_=transform,
                    properties=MarkProperties(enter=enter_props))

        self.marks.append(mark)


class Word(Chart):
    """Vega Word chart"""

    def __init__(self, *args, **kwargs):
        """Create a Vega Word Chart"""

        super(Word, self).__init__(*args, **kwargs)

        # Scales
        self.scales["color"] = Scale(
            name="color", type="ordinal", range="category10",
            domain=DataRef(data="table", field="data.idx"))

        # Data transform
        wordcloud_transform = [
            Transform(type="wordcloud", text="data.idx",
                      font="Helvetica Neue", font_size="data.val",
                      rotate={"random": list(range(-90, 90, 30))})]
        self.data[0].transform = wordcloud_transform

        # Marks
        enter_props = PropertySet(
            x=ValueRef(field="x"),
            y=ValueRef(field="y"),
            angle=ValueRef(field="angle"),
            align=ValueRef(value="center"),
            baseline=ValueRef(value="middle"),
            font=ValueRef(field="font"),
            font_size=ValueRef(field="fontSize"),
            text=ValueRef(field="data.idx"),
            fill=ValueRef(scale="color", field="data.idx"))

        mark = Mark(type="text", from_=MarkRef(data="table"),
                    properties=MarkProperties(enter=enter_props))

        self.marks.append(mark)
