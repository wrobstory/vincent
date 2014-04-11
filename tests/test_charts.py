# -*- coding: utf-8 -*-
"""
Test Vincent.charts
-------------------

Tests for Vincent chart types, which also serve as reference grammar.
"""

import pandas as pd
import nose.tools as nt
from vincent.charts import (data_type, Chart, Bar, Scatter, Line, Area,
                            GroupedBar, Map, Pie, Word)


def chart_runner(chart, scales, axes, marks):
    """Iterate through each chart element for check for contents"""

    for i, scale in enumerate(scales):
        nt.assert_dict_equal(chart.scales[i].grammar(), scale)

    for i, axis in enumerate(axes):
        nt.assert_dict_equal(chart.axes[i].grammar(), axis)

    for i, mark in enumerate(marks):
        nt.assert_dict_equal(chart.marks[i].grammar(), mark)


def test_data_type():
    """Test automatic data type importing"""

    puts1 = [10, 20, 30, 40, 50]
    puts2 = {'apples': 10, 'bananas': 20, 'oranges': 30}

    gets1 = [{'col': 'data', 'idx': 0, 'val': 10},
             {'col': 'data', 'idx': 1, 'val': 20},
             {'col': 'data', 'idx': 2, 'val': 30},
             {'col': 'data', 'idx': 3, 'val': 40},
             {'col': 'data', 'idx': 4, 'val': 50}]
    gets2 = [{'col': 'data', 'idx': 'apples', 'val': 10},
             {'col': 'data', 'idx': 'bananas', 'val': 20},
             {'col': 'data', 'idx': 'oranges', 'val': 30}]

    for ins, outs in zip([puts1, puts2], [gets1, gets2]):
        test = data_type(ins)
        nt.assert_list_equal(test.values, outs)

    # From Iters
    puts = {'x': [1, 2, 3], 'y': [10, 20, 30], 'z': [40, 50, 60]}
    gets = [{'col': 'y', 'idx': 1, 'val': 10},
            {'col': 'y', 'idx': 2, 'val': 20},
            {'col': 'y', 'idx': 3, 'val': 30},
            {'col': 'z', 'idx': 1, 'val': 40},
            {'col': 'z', 'idx': 2, 'val': 50},
            {'col': 'z', 'idx': 3, 'val': 60}]

    test = data_type(puts, iter_idx='x')
    nt.assert_list_equal(test.values, gets)

    # Pandas
    df = pd.DataFrame({'one': [1, 2, 3], 'two': [4, 5, 6]})
    series = pd.Series([1, 2, 3], name='test')
    gets1 = [{'col': 'one', 'idx': 0, 'val': 1},
             {'col': 'two', 'idx': 0, 'val': 4},
             {'col': 'one', 'idx': 1, 'val': 2},
             {'col': 'two', 'idx': 1, 'val': 5},
             {'col': 'one', 'idx': 2, 'val': 3},
             {'col': 'two', 'idx': 2, 'val': 6}]
    gets2 = [{'col': 'test', 'idx': 0, 'val': 1},
             {'col': 'test', 'idx': 1, 'val': 2},
             {'col': 'test', 'idx': 2, 'val': 3}]
    test_df = data_type(df)
    test_series = data_type(series)
    nt.assert_list_equal(test_df.values, gets1)
    nt.assert_list_equal(test_series.values, gets2)

    # Bad type
    class BadType(object):
        'Bad data type'
        pass

    test = BadType()
    nt.assert_raises(ValueError, data_type, test)


class TestChart(object):
    """Test Chart ABC"""

    def test_init(self):
        chart = Chart([0, 1], width=100, height=100)
        nt.assert_equal(chart.width, 100)
        nt.assert_equal(chart.height, 100)
        padding = "auto"
        nt.assert_equal(chart.padding, padding)

        # Data loading errors
        nt.assert_raises(ValueError, Chart)
        nt.assert_raises(ValueError, Chart, [])


class TestScatter(object):
    """Test Scatter Chart"""

    def test_init(self):

        scatter = Scatter([1, 2, 3])

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'type': 'linear'},
                  {'domain': {'data': 'table', 'field': 'data.val'},
                   'name': 'y',
                   'range': 'height',
                   'nice': True},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{
            'type': 'group',
            'from': {
                'data': 'table',
                'transform': [
                    {'keys': ['data.col'], 'type': 'facet'}
                ]
            },
            'marks': [{
                'type': 'symbol',
                'properties': {
                    'enter': {
                        'fill': {'field': 'data.col', 'scale': 'color'},
                        'size': {'value': 100},
                        'x': {'field': 'data.idx', 'scale': 'x'},
                        'y': {'field': 'data.val', 'scale': 'y'}}},
            }]
        }]

        chart_runner(scatter, scales, axes, marks)


class TestLine(object):
    """Test Line Chart"""

    def test_init(self):
        line = Line([1, 2, 3])

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'type': 'linear',
                   'range': 'width'},
                  {'domain': {'data': 'table', 'field': 'data.val'},
                   'name': 'y',
                   'nice': True,
                   'range': 'height'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{
            'type': 'group',
            'from': {
                'data': 'table',
                'transform': [
                    {'keys': ['data.col'], 'type': 'facet'}
                ]
            },
            'marks': [{
                'type': 'line',
                'properties': {
                    'enter': {
                        'stroke': {'field': 'data.col', 'scale': 'color'},
                        'strokeWidth': {'value': 2},
                        'x': {'field': 'data.idx', 'scale': 'x'},
                        'y': {'field': 'data.val', 'scale': 'y'}
                    }
                }
            }]
        }]

        chart_runner(line, scales, axes, marks)


class TestArea(object):
    """Test Area and Stacked Area Chart"""

    def test_init(self):
        area = Area([1, 2, 3])
        stacked_area = Area({'x': [1, 2, 3], 'y': [4, 5, 6], 'z': [7, 8, 9]},
                            iter_idx='x')

        # Test stacked area data
        datas = [
            {'name': 'table',
             'values': [
                 {'col': 'y', 'idx': 1, 'val': 4},
                 {'col': 'y', 'idx': 2, 'val': 5},
                 {'col': 'y', 'idx': 3, 'val': 6},
                 {'col': 'z', 'idx': 1, 'val': 7},
                 {'col': 'z', 'idx': 2, 'val': 8},
                 {'col': 'z', 'idx': 3, 'val': 9}]},
            {'name': 'stats',
             'source': 'table',
             'transform': [
                 {'type': 'facet', 'keys': ['data.idx']},
                 {'type': 'stats', 'value': 'data.val'}]}
        ]

        for i, data in enumerate(datas):
            nt.assert_dict_equal(stacked_area.data[i].grammar(), data)

        # Test area grammar
        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'zero': False,
                   'type': 'linear'},
                  {'domain': {'data': 'stats', 'field': 'sum'},
                   'name': 'y',
                   'nice': True,
                   'range': 'height'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{
            'type': 'group',
            'from': {
                'data': 'table',
                'transform': [
                    {'type': 'facet', 'keys': ['data.col']},
                    {'type': 'stack', 'height': 'data.val',
                     'point': 'data.idx'}]
            },
            'marks': [{
                'type': 'area',
                'properties': {
                    'enter': {
                        'x': {'field': 'data.idx', 'scale': 'x'},
                        'y': {'field': 'y', 'scale': 'y'},
                        'y2': {'field': 'y2', 'scale': 'y'},
                        'fill': {'field': 'data.col', 'scale': 'color'},
                        'interpolate': {'value': 'monotone'}
                    }
                }
            }]
        }]

        chart_runner(area, scales, axes, marks)
        chart_runner(stacked_area, scales, axes, marks)


class TestBar(object):
    """Test Bar and Stacked Bar Chart"""

    def test_init(self):
        bar = Bar([1, 2, 3])
        stacked_bar = Bar({'x': [1, 2, 3], 'y': [4, 5, 6], 'z': [7, 8, 9]},
                          iter_idx='x')

        # Test stacked bar data
        datas = [
            {'name': 'table',
             'values': [
                 {'col': 'y', 'idx': 1, 'val': 4},
                 {'col': 'y', 'idx': 2, 'val': 5},
                 {'col': 'y', 'idx': 3, 'val': 6},
                 {'col': 'z', 'idx': 1, 'val': 7},
                 {'col': 'z', 'idx': 2, 'val': 8},
                 {'col': 'z', 'idx': 3, 'val': 9}]},
            {'name': 'stats',
             'source': 'table',
             'transform': [
                 {'type': 'facet', 'keys': ['data.idx']},
                 {'type': 'stats', 'value': 'data.val'}]}
        ]
        for i, data in enumerate(datas):
            nt.assert_dict_equal(stacked_bar.data[i].grammar(), data)

        # Test bar grammar
        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'zero': False,
                   'type': 'ordinal'},
                  {'domain': {'data': 'stats', 'field': 'sum'},
                   'name': 'y',
                   'nice': True,
                   'range': 'height'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{
            'type': 'group',
            'from': {
                'data': 'table',
                'transform': [
                    {'type': 'facet', 'keys': ['data.col']},
                    {'type': 'stack', 'height': 'data.val',
                     'point': 'data.idx'}]
            },
            'marks': [{
                'type': 'rect',
                'properties': {
                    'enter': {
                        'x': {'field': 'data.idx', 'scale': 'x'},
                        'width': {'band': True, 'offset': -1, 'scale': 'x'},
                        'y': {'field': 'y', 'scale': 'y'},
                        'y2': {'field': 'y2', 'scale': 'y'},
                        'fill': {'field': 'data.col', 'scale': 'color'}
                    }
                }
            }]
        }]

        chart_runner(bar, scales, axes, marks)
        chart_runner(stacked_bar, scales, axes, marks)


class TestGroupedBar(object):
    """Test grouped bar chart"""

    def test_init(self):

        farm_1 = {'apples': 10, 'berries': 32, 'squash': 21}
        farm_2 = {'apples': 15, 'berries': 40, 'squash': 17}
        data = [farm_1, farm_2]
        index = ['Farm 1', 'Farm 2']
        df = pd.DataFrame(data, index=index)
        group = GroupedBar(df)

        # Test grouped bar data
        datas = [{
            'name': 'table',
            'values': [
                {'col': 'apples', 'idx': 'Farm 1', 'val': 10},
                {'col': 'berries', 'idx': 'Farm 1', 'val': 32},
                {'col': 'squash', 'idx': 'Farm 1', 'val': 21},
                {'col': 'apples', 'idx': 'Farm 2', 'val': 15},
                {'col': 'berries', 'idx': 'Farm 2', 'val': 40},
                {'col': 'squash', 'idx': 'Farm 2', 'val': 17}
            ]
        }]
        for i, data in enumerate(datas):
            nt.assert_dict_equal(group.data[i].grammar(), data)

        # Test grouped bar grammar
        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'padding': 0.2,
                   'range': 'width',
                   'type': 'ordinal'},
                  {'domain': {'data': 'table', 'field': 'data.val'},
                   'name': 'y',
                   'nice': True,
                   'range': 'height'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{
            'type': 'group',
            'from': {
                'data': 'table',
                'transform': [{'keys': ['data.idx'], 'type': 'facet'}]
            },
            'marks': [{
                'type': 'rect',
                'properties': {
                    'enter': {
                        'fill': {'field': 'data.col', 'scale': 'color'},
                        'width': {'band': True, 'offset': -1, 'scale': 'pos'},
                        'x': {'field': 'data.col', 'scale': 'pos'},
                        'y': {'field': 'data.val', 'scale': 'y'},
                        'y2': {'scale': 'y', 'value': 0}}
                }
            }],
            'properties': {
                'enter': {
                    'width': {'band': True, 'scale': 'x'},
                    'x': {'field': 'key', 'scale': 'x'}
                }
            },
            'scales': [{
                'domain': {'field': 'data.col'},
                'name': 'pos',
                'range': 'width',
                'type': 'ordinal'
            }]
        }]

        chart_runner(group, scales, axes, marks)


class TestPie(object):
    """Test Pie Chart"""

    def test_init(self):
        pie = Pie([12, 23, 34])

        axes = []

        scales = [{
            "domain": {"data": "table", "field": "data.idx"},
            "name": "color",
            "range": "category10",
            "type": "ordinal"
        }]

        marks = [{
            "type": "arc",
            "from": {
                "data": "table",
                "transform": [{"type": "pie", "value": "data.val"}]
            },
            "properties": {
                "enter": {
                    "x": {"group": "width", "mult": 0.5},
                    "y": {"group": "height", "mult": 0.5},
                    "endAngle": {"field": "endAngle"},
                    "innerRadius": {"value": 0},
                    "outerRadius": {"value": 250},
                    "startAngle": {"field": "startAngle"},
                    "stroke": {"value": "white"},
                    "fill": {"field": "data.idx", "scale": "color"}
                }
            }
        }]

        chart_runner(pie, scales, axes, marks)


class TestMaps(object):
    """Test maps, both simple and with data binding"""

    def setup(self):

        # Data
        self.df = pd.DataFrame({'one': [1, 2, 3], 'two': [4, 5, 6],
                                'three': [7, 8, 9]})
        self.series = pd.Series([1, 2, 3], name='test')

        self.geo_data = [{
            'name': 'fake_data',
            'url': 'mapdata.topo.json',
            'feature': 'topo_feature'
        },
            {
                'name': 'fake_data_2',
                'url': 'mapdata2.topo.json',
                'feature': 'topo_feature'
            }]

    def test_simple(self):

        map_ = Map(geo_data=[self.geo_data[0]], projection='albersUsa',
                   center=[10, 20], scale=200, rotate=10)

        axes = []
        scales = []

        datas = [{'name': 'fake_data',
                  'url': 'mapdata.topo.json',
                  'format': {'feature': 'topo_feature', 'type': 'topojson'},
                  'transform': [{
                      'center': [10, 20],
                      'projection': 'albersUsa',
                      'rotate': 10,
                      'scale': 200,
                      'translate': [480, 250],
                      'type': 'geopath',
                      'value': 'data'
                  }]
                  }]

        marks = [{'type': 'path',
                  'from': {'data': 'fake_data'},
                  'properties': {
                      'enter': {
                          'path': {'field': 'path'},
                          'stroke': {'value': '#000000'}
                      },
                      'update': {
                          'fill': {'value': 'steelblue'}
                      }
                  }
                  }]

        chart_runner(map_, scales, axes, marks)

        for i, data in enumerate(datas):
            nt.assert_dict_equal(map_.data[i].grammar(), data)

    def test_binding(self):

        with nt.assert_raises(ValueError) as err:
            map_df = Map(data=self.df, geo_data=self.geo_data,
                         projection='albersUsa', center=[10, 20], scale=200,
                         rotate=10, map_key={'fake_data_2': 'properties.id'})
            nt.assert_equal(
                err.exception.args[0],
                'If passing data, you must pass data cols to key/bind on'
            )

        map_df = Map(data=self.df, geo_data=self.geo_data,
                     projection='albersUsa',
                     center=[10, 20], scale=200, rotate=10,
                     map_key={'fake_data_2': 'properties.id'}, data_key='one',
                     data_bind='two')

        axes = []
        scales = [{
            'name': 'color',
            'type': 'quantize',
            'domain': [4.0, 5.9],
            'range': ['#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4',
                      '#4eb3d3', '#2b8cbe', '#0868ac', '#084081']
        }]

        datas = [{'name': 'fake_data',
                  'url': 'mapdata.topo.json',
                  'format': {'feature': 'topo_feature', 'type': 'topojson'},
                  'transform': [{
                      'center': [10, 20],
                      'projection': 'albersUsa',
                      'rotate': 10,
                      'scale': 200,
                      'translate': [480, 250],
                      'type': 'geopath',
                      'value': 'data'
                  }],
                  },
                 {'name': 'table',
                  'values': [
                      {'x': 1, 'y': 4},
                      {'x': 2, 'y': 5},
                      {'x': 3, 'y': 6}
                  ]
                  },
                 {'name': 'fake_data_2',
                  'url': 'mapdata2.topo.json',
                  'format': {'feature': 'topo_feature', 'type': 'topojson'},
                  'transform': [
                      {
                          'as': 'value',
                          'default': 'noval',
                          'key': 'data.properties.id',
                          'type': 'zip',
                          'with': 'table',
                          'withKey': 'data.x'
                      },
                      {
                          'test': "d.path!='noval' && d.value!='noval'",
                          'type': 'filter'
                      },
                      {
                          'center': [10, 20],
                          'projection': 'albersUsa',
                          'rotate': 10,
                          'scale': 200,
                          'translate': [480, 250],
                          'type': 'geopath',
                          'value': 'data'
                      }]
                  }
                 ]

        marks = [{'type': 'path',
                  'from': {'data': 'fake_data'},
                  'properties': {
                      'enter': {
                          'path': {'field': 'path'},
                          'stroke': {'value': '#000000'}
                      },
                      'update': {
                          'fill': {'value': 'steelblue'}
                      }
                  }
                  },
                 {'type': 'path',
                  'from': {'data': 'fake_data_2'},
                  'properties': {
                      'enter': {
                          'path': {'field': 'path'},
                          'stroke': {'value': '#000000'}
                      },
                      'update': {
                          'fill': {'field': 'value.data.y', 'scale': 'color'}
                      }
                  }
                  }]

        chart_runner(map_df, scales, axes, marks)

        for i, data in enumerate(datas):
            nt.assert_dict_equal(map_df.data[i].grammar(), data)

        map_df.rebind(column='three', brew='PuBu')

        rebound = {'name': 'table',
                   'values': [
                       {'x': 1, 'y': 7},
                       {'x': 2, 'y': 8},
                       {'x': 3, 'y': 9}
                   ]
                   }

        new_scale = {
            'name': 'color',
            'type': 'quantize',
            'domain': [7.0, 8.9],
            'range': [
                "#fff7fb",
                "#ece7f2",
                "#d0d1e6",
                "#a6bddb",
                "#74a9cf",
                "#3690c0",
                "#0570b0",
                "#045a8d",
                "#023858"
            ]
        }

        assert map_df.data['table'].grammar() == rebound
        assert map_df.scales['color'].grammar() == new_scale


class TestWord(object):
    """Test Pie Chart"""

    def test_init(self):
        d = {'emop': 32, 'epom': 28, 'meop': 36, 'mepo': 12,
             'moep': 40, 'mope': 56, 'omep': 20, 'opem': 24,
             'pemo': 10, 'peom': 44, 'poem': 80, 'pome': 10}
        word = Word(d)

        axes = []

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'color',
                   'range': 'category10',
                   'type': 'ordinal'}]

        marks = [{
            'type': 'text',
            'from': {'data': 'table'},
            'properties': {
                'enter': {
                    'align': {'value': 'center'},
                    'angle': {'field': 'angle'},
                    'baseline': {'value': 'middle'},
                    'fill': {'field': 'data.idx', 'scale': 'color'},
                    'font': {'field': 'font'},
                    'fontSize': {'field': 'fontSize'},
                    'text': {'field': 'data.idx'},
                    'x': {'field': 'x'},
                    'y': {'field': 'y'}
                }
            }
        }]

        chart_runner(word, scales, axes, marks)
