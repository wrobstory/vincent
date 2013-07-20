  # -*- coding: utf-8 -*-
'''
Test Vincent.charts
-------------------

'''

import pandas as pd
import nose.tools as nt
from vincent.charts import (data_type, Chart, Bar, Scatter, Line, Area)


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

    puts = [[1], [1, 2], ((1, 2)), ((1, 2), (3, 4)), [(1, 2), (3, 4)],
            [[1, 2], [3, 4]], {1: 2}, {1: 2, 3: 4}]

    common = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]
    gets = [[{'x': 0, 'y': 1}], [{'x': 0, 'y': 1}, {'x': 1, 'y': 2}],
            [{'x': 0, 'y': 1}, {'x': 1, 'y': 2}], common, common,
            common, [{'x': 1, 'y': 2}], common]

    for ins, outs in zip(puts, gets):
        test = data_type(ins, False, False)
        nt.assert_list_equal(test.values, outs)

    #From Iters
    puts = [{'x': [1, 3], 'y': [2, 4]}, {'x': (1, 3), 'y': (2, 4)}]
    gets = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]

    for ins in puts:
        test = data_type(ins, True, False)
        nt.assert_list_equal(test.values, gets)

    #Pandas
    df = pd.DataFrame({'test': [1, 2, 3]})
    series = pd.Series([1, 2, 3], name='test')
    gets = [{'idx': 0, 'test': 1}, {'idx': 1, 'test': 2},
            {'idx': 2, 'test': 3}]
    test_df = data_type(df, False, False)
    test_series = data_type(series, False, False)
    nt.assert_list_equal(test_df.values, gets)
    nt.assert_list_equal(test_series.values, gets)

    #Bad type
    class BadType(object):
        """Bad data type"""
        pass

    test = BadType()
    nt.assert_raises(ValueError, data_type, test, False, False)


class TestChart(object):
    """Test Chart ABC"""

    def test_init(self):
        chart = Chart([0, 1], width=100, height=100)
        nt.assert_equal(chart.width, 100)
        nt.assert_equal(chart.height, 100)
        padding = {'top': 10, 'left': 30, 'bottom': 20, 'right': 10}
        nt.assert_dict_equal(chart.padding, padding)

        #Data loading errors
        nt.assert_raises(ValueError, Chart)
        nt.assert_raises(ValueError, Chart, [])


class TestBar(object):
    """Test Bar Chart"""

    def test_init(self):
        bar = Bar([1, 2, 3])

        scales = [{u'domain': {u'data': u'table', u'field': u'data.x'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'ordinal'},
                  {u'domain': {u'data': u'table', u'field': u'data.y'},
                   u'name': u'y',
                   u'nice': True,
                   u'range': u'height'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table'},
                  u'properties': {u'enter': {u'width': {u'band': True,
                  u'offset': -1,
                  u'scale': u'x'},
                  u'x': {u'field': u'data.x', u'scale': u'x'},
                  u'y': {u'field': u'data.y', u'scale': u'y'},
                  u'y2': {u'scale': u'y', u'value': 0}},
                  u'update': {u'fill': {u'value': u'steelblue'}}},
                  u'type': u'rect'}]

        chart_runner(bar, scales, axes, marks)


class TestScatter(object):
    """Test Scatter Chart"""

    def test_init(self):

        scatter = Scatter([1, 2, 3])

        scales = [{u'domain': {u'data': u'table', u'field': u'data.x'},
                   u'name': u'x',
                   u'nice': True,
                   u'range': u'width'},
                  {u'domain': {u'data': u'table', u'field': u'data.y'},
                   u'name': u'y',
                   u'range': u'height',
                   u'nice': True}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table'},
                  u'properties': {u'enter': {u'fillOpacity': {u'value': 0.9},
                  u'stroke': {u'value': u'#2a3140'},
                  u'x': {u'field': u'data.x', u'scale': u'x'},
                  u'y': {u'field': u'data.y', u'scale': u'y'}},
                  u'update': {u'fill': {u'value': u'steelblue'}}},
                  u'type': u'symbol'}]

        chart_runner(scatter, scales, axes, marks)


class TestLine(object):
    """Test Line Chart"""

    def test_init(self):
        line = Line([1, 2, 3])

        scales = [{u'domain': {u'data': u'table', u'field': u'data.x'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'linear'},
                  {u'domain': {u'data': u'table', u'field': u'data.y'},
                   u'name': u'y',
                   u'nice': True,
                   u'range': u'height'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table'},
                 u'properties': {u'enter': {u'stroke': {u'value': u'#2a3140'},
                 u'strokeWidth': {u'value': 2},
                 u'x': {u'field': u'data.x', u'scale': u'x'},
                 u'y': {u'field': u'data.y', u'scale': u'y'}}},
                 u'type': u'line'}]

        chart_runner(line, scales, axes, marks)


class TestArea(object):
    """Test Area Chart"""

    def test_init(self):
        area = Area([1, 2, 3])

        scales = [{u'domain': {u'data': u'table', u'field': u'data.x'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'linear'},
                  {u'domain': {u'data': u'table', u'field': u'data.y'},
                   u'name': u'y',
                   u'nice': True,
                   u'range': u'height'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table'},
                  u'properties': {u'enter': {u'fill': {u'value': u'#2a3140'},
                  u'interpolate': {u'value': u'monotone'},
                  u'stroke': {u'value': u'#2a3140'},
                  u'strokeWidth': {u'value': 2},
                  u'x': {u'field': u'data.x', u'scale': u'x'},
                  u'y': {u'field': u'data.y', u'scale': u'y'},
                  u'y2': {u'scale': u'y', u'value': 0}},
                  u'update': {u'fillOpacity': {u'value': 1}}},
                  u'type': u'area'}]

        chart_runner(area, scales, axes, marks)

