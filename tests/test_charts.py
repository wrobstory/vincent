  # -*- coding: utf-8 -*-
'''
Test Vincent.charts
-------------------

Tests for Vincent chart types, which also serve as reference grammar.

'''

import pandas as pd
import nose.tools as nt
from vincent.charts import (data_type, Chart, Bar, Scatter, Line, Area,
                            StackedArea, StackedBar, GroupedBar)


def chart_runner(chart, scales, axes, marks):
    """Iterate through each chart element for check for contents"""

    for i, scale in enumerate(scales):
        nt.assert_dict_equal(chart.scales[i].grammar(), scale)

    for i, axis in enumerate(axes):
        nt.assert_dict_equal(chart.axes[i].grammar(), axis)

    for i, axis in enumerate(marks):
        nt.assert_dict_equal(chart.marks[i].grammar(), axis)


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

    #From Iters
    puts = {'x': [1, 2, 3], 'y': [10, 20, 30], 'z': [40, 50, 60]}
    gets = [{'col': 'y', 'idx': 1, 'val': 10},
            {'col': 'y', 'idx': 2, 'val': 20},
            {'col': 'y', 'idx': 3, 'val': 30},
            {'col': 'z', 'idx': 1, 'val': 40},
            {'col': 'z', 'idx': 2, 'val': 50},
            {'col': 'z', 'idx': 3, 'val': 60}]

    test = data_type(puts, iter_idx='x')
    nt.assert_list_equal(test.values, gets)

    #Pandas
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

    #Bad type
    class BadType(object):
        """Bad data type"""
        pass

    test = BadType()
    nt.assert_raises(ValueError, data_type, test)


class TestChart(object):
    """Test Chart ABC"""

    def test_init(self):
        chart = Chart([0, 1], width=100, height=100)
        nt.assert_equal(chart.width, 100)
        nt.assert_equal(chart.height, 100)
        padding = {'top': 10, 'left': 50, 'bottom': 50, 'right': 100}
        nt.assert_dict_equal(chart.padding, padding)

        #Data loading errors
        nt.assert_raises(ValueError, Chart)
        nt.assert_raises(ValueError, Chart, [])


class TestBar(object):
    """Test Bar Chart"""

    def test_init(self):
        bar = Bar([1, 2, 3])

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'type': 'ordinal'},
                  {'domain': {'data': 'table', 'field': 'data.val'},
                   'name': 'y',
                   'nice': True,
                   'range': 'height'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{'from': {'data': 'table'},
                  'properties': {'enter': {'width': {'band': True,
                  'offset': -1,
                  'scale': 'x'},
                  'x': {'field': 'data.idx', 'scale': 'x'},
                  'y': {'field': 'data.val', 'scale': 'y'},
                  'y2': {'scale': 'y', 'value': 0}},
                  'update': {'fill': {'value': 'steelblue'}}},
                  'type': 'rect'}]

        chart_runner(bar, scales, axes, marks)


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
                   'type': 'linear',
                   'range': 'height',
                   'nice': True},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{'from': {'data': 'table',
                  'transform': [{'keys': ['data.col'], 'type': 'facet'}]},
                  'marks':
                  [{'properties': {'enter': {'fill': {'field': 'data.col',
                    'scale': 'color'},
                    'size': {'value': 100},
                    'x': {'field': 'data.idx', 'scale': 'x'},
                    'y': {'field': 'data.val', 'scale': 'y'}}},
                    'type': 'symbol'}],
                  'type': 'group'}]

        chart_runner(scatter, scales, axes, marks)


class TestLine(object):
    """Test Line Chart"""

    def test_init(self):
        line = Line([1, 2, 3])

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'type': 'linear'},
                  {'domain': {'data': 'table', 'field': 'data.val'},
                   'name': 'y',
                   'type': 'linear',
                   'nice': True,
                   'range': 'height'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{'from': {'data': 'table',
                  'transform': [{'keys': ['data.col'], 'type': 'facet'}]},
                  'marks':
                 [{'properties': {'enter': {'stroke': {'field': 'data.col',
                   'scale': 'color'},
                   'strokeWidth': {'value': 2},
                   'x': {'field': 'data.idx', 'scale': 'x'},
                   'y': {'field': 'data.val', 'scale': 'y'}}},
                   'type': 'line'}],
                 'type': 'group'}]

        chart_runner(line, scales, axes, marks)


class TestArea(object):
    """Test Area Chart"""

    def test_init(self):
        area = Area([1, 2, 3])

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'type': 'linear'},
                  {'domain': {'data': 'table', 'field': 'data.val'},
                   'name': 'y',
                   'nice': True,
                   'type': 'linear',
                   'range': 'height'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        marks = [{'from': {'data': 'table',
                  'transform': [{'keys': ['data.col'], 'type': 'facet'}]},
                  'marks':
                  [{'properties': {'enter': {'fill': {'field': 'data.col',
                    'scale': 'color'},
                    'interpolate': {'value': 'monotone'},
                    'x': {'field': 'data.idx', 'scale': 'x'},
                    'y': {'field': 'data.val', 'scale': 'y'},
                    'y2': {'scale': 'y', 'value': 0}}},
                    'type': 'area'}],
                 'type': 'group'}]

        chart_runner(area, scales, axes, marks)


class TestStackedArea(object):
    """Test Stacked Area Chart"""

    def test_init(self):

        stack = StackedArea({'x': [1, 2, 3], 'y': [4, 5, 6], 'z': [7, 8, 9]},
                            iter_idx='x')

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'type': 'linear',
                   'zero': False},
                  {'domain': {'data': 'stats', 'field': 'sum'},
                   'name': 'y',
                   'nice': True,
                   'range': 'height',
                   'type': 'linear'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        datas = [{'name': 'table',
                 'values': [{'col': 'y', 'idx': 1, 'val': 4},
                  {'col': 'y', 'idx': 2, 'val': 5},
                  {'col': 'y', 'idx': 3, 'val': 6},
                  {'col': 'z', 'idx': 1, 'val': 7},
                  {'col': 'z', 'idx': 2, 'val': 8},
                  {'col': 'z', 'idx': 3, 'val': 9}]},
                {'name': 'stats',
                 'source': 'table',
                 'transform': [{'keys': ['data.idx'], 'type': 'facet'},
                  {'type': 'stats', 'value': 'data.val'}]}]

        marks = [{'from': {'data': 'table',
                  'transform': [{'keys': ['data.col'], 'type': 'facet'},
                 {'height': 'data.val', 'point': 'data.idx', 'type': 'stack'}]},
                 'marks':
                 [{'properties': {'enter': {'fill': {'field': 'data.col',
                   'scale': 'color'},
                   'interpolate': {'value': 'monotone'},
                   'x': {'field': 'data.idx', 'scale': 'x'},
                   'y': {'field': 'y', 'scale': 'y'},
                   'y2': {'field': 'y2', 'scale': 'y'}}},
                   'type': 'area'}],
                   'type': 'group'}]

        chart_runner(stack, scales, axes, marks)

        for i, data in enumerate(datas):
            nt.assert_dict_equal(stack.data[i].grammar(), data)


class TestStackedBar(object):
    """Test Stacked Bar Chart"""

    def test_init(self):

        stack = StackedBar({'x': [1, 2, 3], 'y': [4, 5, 6], 'z': [7, 8, 9]},
                           iter_idx='x')

        scales = [{'domain': {'data': 'table', 'field': 'data.idx'},
                   'name': 'x',
                   'range': 'width',
                   'type': 'ordinal'},
                  {'domain': {'data': 'stats', 'field': 'sum'},
                   'name': 'y',
                   'nice': True,
                   'range': 'height',
                   'type': 'linear'},
                  {'domain': {'data': 'table', 'field': 'data.col'},
                   'name': 'color',
                   'range': 'category20',
                   'type': 'ordinal'}]

        axes = [{'scale': 'x', 'type': 'x'},
                {'scale': 'y', 'type': 'y'}]

        datas = [{'name': 'table',
                 'values': [{'col': 'y', 'idx': 1, 'val': 4},
                  {'col': 'y', 'idx': 2, 'val': 5},
                  {'col': 'y', 'idx': 3, 'val': 6},
                  {'col': 'z', 'idx': 1, 'val': 7},
                  {'col': 'z', 'idx': 2, 'val': 8},
                  {'col': 'z', 'idx': 3, 'val': 9}]},
                {'name': 'stats',
                 'source': 'table',
                 'transform': [{'keys': ['data.idx'], 'type': 'facet'},
                {'type': 'stats', 'value': 'data.val'}]}]

        marks = [{'from': {'data': 'table',
                  'transform': [{'keys': ['data.col'], 'type': 'facet'},
                 {'height': 'data.val', 'point': 'data.idx', 'type': 'stack'}]},
                 'marks':
                 [{'properties': {'enter': {'fill': {'field': 'data.col',
                   'scale': 'color'},
                   'width': {'band': True, 'offset': -1, 'scale': 'x'},
                   'x': {'field': 'data.idx', 'scale': 'x'},
                   'y': {'field': 'y', 'scale': 'y'},
                   'y2': {'field': 'y2', 'scale': 'y'}}},
                   'type': 'rect'}],
                   'type': 'group'}]

        chart_runner(stack, scales, axes, marks)

        for i, data in enumerate(datas):
            nt.assert_dict_equal(stack.data[i].grammar(), data)


class TestGroupedBar(object):
    """Test grouped bar chart"""

    def test_init(self):

        farm_1 = {'apples': 10, 'berries': 32, 'squash': 21}
        farm_2 = {'apples': 15, 'berries': 40, 'squash': 17}
        data = [farm_1, farm_2]
        index = ['Farm 1', 'Farm 2']
        df = pd.DataFrame(data, index=index)

        group = GroupedBar(df)

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

        datas = [{'name': 'table',
                  'values':
                  [{'col': 'apples', 'group': 0, 'idx': 'Farm 1', 'val': 10},
                  {'col': 'berries', 'group': 1, 'idx': 'Farm 1', 'val': 32},
                  {'col': 'squash', 'group': 2, 'idx': 'Farm 1', 'val': 21},
                  {'col': 'apples', 'group': 0, 'idx': 'Farm 2', 'val': 15},
                  {'col': 'berries', 'group': 1, 'idx': 'Farm 2', 'val': 40},
                  {'col': 'squash', 'group': 2, 'idx': 'Farm 2', 'val': 17}]}]

        marks = [{'from': {'data': 'table',
                  'transform': [{'keys': ['data.idx'], 'type': 'facet'}]},
                  'marks': [{'properties': {'enter': {'fill': {'field': 'data.col',
                      'scale': 'color'},
                     'width': {'band': True, 'offset': -1, 'scale': 'pos'},
                     'x': {'field': 'data.group', 'scale': 'pos'},
                     'y': {'field': 'data.val', 'scale': 'y'},
                     'y2': {'scale': 'y', 'value': 0}}},
                   'type': 'rect'}],
                 'properties': {'enter': {'width': {'band': True, 'scale': 'x'},
                   'x': {'field': 'key', 'scale': 'x'}}},
                 'scales': [{'domain': {'field': 'data.group'},
                   'name': 'pos',
                   'range': 'width',
                   'type': 'ordinal'}],
                 'type': 'group'}]

        chart_runner(group, scales, axes, marks)

        for i, data in enumerate(datas):
            nt.assert_dict_equal(group.data[i].grammar(), data)
