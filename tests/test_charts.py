  # -*- coding: utf-8 -*-
'''
Test Vincent.charts
-------------------

'''

import pandas as pd
import nose.tools as nt
from vincent.charts import (data_type, Chart, Bar)


def test_data_type():
    """Test automatic data type importing"""

    puts = [[1], [1, 2], ((1, 2)), ((1, 2), (3, 4)), [(1, 2), (3, 4)],
            [[1, 2], [3, 4]], {1: 2}, {1: 2, 3: 4}]

    common = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]
    gets = [[{'x': 0, 'y': 1}], [{'x': 0, 'y': 1}, {'x': 1, 'y': 2}],
            [{'x': 0, 'y': 1}, {'x': 1, 'y': 2}], common, common,
            common, [{'x': 1, 'y': 2}], common]

    for ins, outs in zip(puts, gets):
        test = data_type(ins, False)
        nt.assert_list_equal(test.values, outs)

    #From Iters
    puts = [{'x': [1, 3], 'y': [2, 4]}, {'x': (1, 3), 'y': (2, 4)}]
    gets = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]

    for ins in puts:
        test = data_type(ins, True)
        nt.assert_list_equal(test.values, gets)

    #Pandas
    df = pd.DataFrame({'test': [1, 2, 3]})
    series = pd.Series([1, 2, 3], name='test')
    gets = [{'_index': 0, 'test': 1}, {'_index': 1, 'test': 2},
            {'_index': 2, 'test': 3}]
    test_df = data_type(df, False)
    test_series = data_type(series, False)
    nt.assert_list_equal(test_df.values, gets)
    nt.assert_list_equal(test_series.values, gets)

    #Bad type
    class BadType(object):
        """Bad data type"""
        pass

    test = BadType()
    nt.assert_raises(ValueError, data_type, test, False)


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
                   u'type': u'ordinal'}]

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

        for i, scale in enumerate(scales):
            nt.assert_dict_equal(bar.scales[i].grammar(), scale)

        for i, axis in enumerate(axes):
            nt.assert_dict_equal(bar.axes[i].grammar(), axis)

        for i, axis in enumerate(marks):
            nt.assert_dict_equal(bar.marks[i].grammar(), axis)
