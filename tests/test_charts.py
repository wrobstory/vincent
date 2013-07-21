  # -*- coding: utf-8 -*-
'''
Test Vincent.charts
-------------------

Tests for Vincent chart types, which also serve as reference grammar.

'''

import pandas as pd
import nose.tools as nt
from vincent.charts import (data_type, Chart, Bar, Scatter, Line, Area,
                            StackedArea, StackedBar)


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
             {'col': 'data', 'idx': 'oranges', 'val': 30},
             {'col': 'data', 'idx': 'bananas', 'val': 20}]

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

        scales = [{u'domain': {u'data': u'table', u'field': u'data.idx'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'ordinal'},
                  {u'domain': {u'data': u'table', u'field': u'data.val'},
                   u'name': u'y',
                   u'nice': True,
                   u'range': u'height'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table'},
                  u'properties': {u'enter': {u'width': {u'band': True,
                  u'offset': -1,
                  u'scale': u'x'},
                  u'x': {u'field': u'data.idx', u'scale': u'x'},
                  u'y': {u'field': u'data.val', u'scale': u'y'},
                  u'y2': {u'scale': u'y', u'value': 0}},
                  u'update': {u'fill': {u'value': u'steelblue'}}},
                  u'type': u'rect'}]

        chart_runner(bar, scales, axes, marks)


class TestScatter(object):
    """Test Scatter Chart"""

    def test_init(self):

        scatter = Scatter([1, 2, 3])

        scales = [{u'domain': {u'data': u'table', u'field': u'data.idx'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'linear'},
                  {u'domain': {u'data': u'table', u'field': u'data.val'},
                   u'name': u'y',
                   u'type': u'linear',
                   u'range': u'height',
                   u'nice': True},
                  {u'domain': {u'data': u'table', u'field': u'data.col'},
                   u'name': u'color',
                   u'range': u'category20',
                   u'type': u'ordinal'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table',
                  u'transform': [{u'keys': [u'data.col'], u'type': u'facet'}]},
                  u'marks':
                  [{u'properties': {u'enter': {u'fill': {u'field': u'data.col',
                    u'scale': u'color'},
                    u'size': {u'value': 10},
                    u'x': {u'field': u'data.idx', u'scale': u'x'},
                    u'y': {u'field': u'data.val', u'scale': u'y'}}},
                    u'type': u'symbol'}],
                  u'type': u'group'}]

        chart_runner(scatter, scales, axes, marks)


class TestLine(object):
    """Test Line Chart"""

    def test_init(self):
        line = Line([1, 2, 3])

        scales = [{u'domain': {u'data': u'table', u'field': u'data.idx'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'linear'},
                  {u'domain': {u'data': u'table', u'field': u'data.val'},
                   u'name': u'y',
                   u'type': u'linear',
                   u'nice': True,
                   u'range': u'height'},
                  {u'domain': {u'data': u'table', u'field': u'data.col'},
                   u'name': u'color',
                   u'range': u'category20',
                   u'type': u'ordinal'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table',
                  u'transform': [{u'keys': [u'data.col'], u'type': u'facet'}]},
                  u'marks':
                 [{u'properties': {u'enter': {u'stroke': {u'field': u'data.col',
                   u'scale': u'color'},
                   u'strokeWidth': {u'value': 2},
                   u'x': {u'field': u'data.idx', u'scale': u'x'},
                   u'y': {u'field': u'data.val', u'scale': u'y'}}},
                   u'type': u'line'}],
                 u'type': u'group'}]

        chart_runner(line, scales, axes, marks)


class TestArea(object):
    """Test Area Chart"""

    def test_init(self):
        area = Area([1, 2, 3])

        scales = [{u'domain': {u'data': u'table', u'field': u'data.idx'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'linear'},
                  {u'domain': {u'data': u'table', u'field': u'data.val'},
                   u'name': u'y',
                   u'nice': True,
                   u'type': u'linear',
                   u'range': u'height'},
                  {u'domain': {u'data': u'table', u'field': u'data.col'},
                   u'name': u'color',
                   u'range': u'category20',
                   u'type': u'ordinal'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        marks = [{u'from': {u'data': u'table',
                  u'transform': [{u'keys': [u'data.col'], u'type': u'facet'}]},
                  u'marks':
                  [{u'properties': {u'enter': {u'fill': {u'field': u'data.col',
                    u'scale': u'color'},
                    u'interpolate': {u'value': u'monotone'},
                    u'x': {u'field': u'data.idx', u'scale': u'x'},
                    u'y': {u'field': u'data.val', u'scale': u'y'},
                    u'y2': {u'scale': u'y', u'value': 0}}},
                    u'type': u'area'}],
                 u'type': u'group'}]

        chart_runner(area, scales, axes, marks)


class TestStackedArea(object):
    """Test Stacked Area Chart"""

    def test_init(self):

        stack = StackedArea({'x': [1, 2, 3], 'y': [4, 5, 6], 'z': [7, 8, 9]},
                            iter_idx='x')

        scales = [{u'domain': {u'data': u'table', u'field': u'data.idx'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'linear',
                   u'zero': False},
                  {u'domain': {u'data': u'stats', u'field': u'sum'},
                   u'name': u'y',
                   u'nice': True,
                   u'range': u'height',
                   u'type': u'linear'},
                  {u'domain': {u'data': u'table', u'field': u'data.col'},
                   u'name': u'color',
                   u'range': u'category20',
                   u'type': u'ordinal'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        datas = [{u'name': u'table',
                 u'values': [{u'col': u'y', u'idx': 1, u'val': 4},
                  {u'col': u'y', u'idx': 2, u'val': 5},
                  {u'col': u'y', u'idx': 3, u'val': 6},
                  {u'col': u'z', u'idx': 1, u'val': 7},
                  {u'col': u'z', u'idx': 2, u'val': 8},
                  {u'col': u'z', u'idx': 3, u'val': 9}]},
                {u'name': u'stats',
                 u'source': u'table',
                 u'transform': [{u'keys': [u'data.idx'], u'type': u'facet'},
                  {u'type': u'stats', u'value': u'data.val'}]}]

        marks = [{u'from': {u'data': u'table',
                  u'transform': [{u'keys': [u'data.col'], u'type': u'facet'},
                 {u'height': u'data.val', u'point': u'data.idx', u'type': u'stack'}]},
                 u'marks':
                 [{u'properties': {u'enter': {u'fill': {u'field': u'data.col',
                   u'scale': u'color'},
                   u'interpolate': {u'value': u'monotone'},
                   u'x': {u'field': u'data.idx', u'scale': u'x'},
                   u'y': {u'field': u'y', u'scale': u'y'},
                   u'y2': {u'field': u'y2', u'scale': u'y'}}},
                   u'type': u'area'}],
                   u'type': u'group'}]

        chart_runner(stack, scales, axes, marks)

        for i, data in enumerate(datas):
            nt.assert_dict_equal(stack.data[i].grammar(), data)

class TestStackedBar(object):
    """Test Stacked Bar Chart"""

    def test_init(self):

        stack = StackedBar({'x': [1, 2, 3], 'y': [4, 5, 6], 'z': [7, 8, 9]},
                           iter_idx='x')

        scales = [{u'domain': {u'data': u'table', u'field': u'data.idx'},
                   u'name': u'x',
                   u'range': u'width',
                   u'type': u'ordinal'},
                  {u'domain': {u'data': u'stats', u'field': u'sum'},
                   u'name': u'y',
                   u'nice': True,
                   u'range': u'height',
                   u'type': u'linear'},
                  {u'domain': {u'data': u'table', u'field': u'data.col'},
                   u'name': u'color',
                   u'range': u'category20',
                   u'type': u'ordinal'}]

        axes = [{u'scale': u'x', u'type': u'x'},
                {u'scale': u'y', u'type': u'y'}]

        datas = [{u'name': u'table',
                 u'values': [{u'col': u'y', u'idx': 1, u'val': 4},
                  {u'col': u'y', u'idx': 2, u'val': 5},
                  {u'col': u'y', u'idx': 3, u'val': 6},
                  {u'col': u'z', u'idx': 1, u'val': 7},
                  {u'col': u'z', u'idx': 2, u'val': 8},
                  {u'col': u'z', u'idx': 3, u'val': 9}]},
                {u'name': u'stats',
                 u'source': u'table',
                 u'transform': [{u'keys': [u'data.idx'], u'type': u'facet'},
                {u'type': u'stats', u'value': u'data.val'}]}]

        marks = [{u'from': {u'data': u'table',
                  u'transform': [{u'keys': [u'data.col'], u'type': u'facet'},
                 {u'height': u'data.val', u'point': u'data.idx', u'type': u'stack'}]},
                 u'marks':
                 [{u'properties': {u'enter': {u'fill': {u'field': u'data.col',
                   u'scale': u'color'},
                   u'width': {u'band': True, u'offset': -1, u'scale': u'x'},
                   u'x': {u'field': u'data.idx', u'scale': u'x'},
                   u'y': {u'field': u'y', u'scale': u'y'},
                   u'y2': {u'field': u'y2', u'scale': u'y'}}},
                   u'type': u'rect'}],
                   u'type': u'group'}]

        chart_runner(stack, scales, axes, marks)

        for i, data in enumerate(datas):
            nt.assert_dict_equal(stack.data[i].grammar(), data)












