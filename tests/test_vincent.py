  # -*- coding: utf-8 -*-
'''
Test Vincent
---------

'''

import pandas as pd
import vincent
import nose.tools as nt
import os.path as path

try:
    import unittest.mock as mock
    assert mock
except ImportError:
    # Requires mock library if version < 3.3
    import mock


# Location of test data files.
data_dir = path.join(path.dirname(path.abspath(__file__)), 'data')


def assert_vega_equal(vis1, vis2):
    '''Assert two Vega classes contain equal contents'''
    attrib_compares = {
        'width':            nt.assert_equal,
        'height':           nt.assert_equal,
        'padding':          nt.assert_dict_equal,
        'viewport':         nt.assert_list_equal,
        'visualization':    nt.assert_dict_equal,
        'data':             nt.assert_list_equal,
        'scales':           nt.assert_list_equal,
        'axes':             nt.assert_list_equal,
        'axis_labels':      nt.assert_dict_equal,
        'marks':            nt.assert_list_equal}

    for attr, assert_eq in attrib_compares.iteritems():
        if getattr(vis1, attr):
            assert_eq(getattr(vis1, attr), getattr(vis2, attr))


class TestVincent(object):
    '''Test vincent.py'''

    def setup(self):
        '''Setup method'''

        self.testvin = vincent.Vega()

        self.default_vega = {'width': 400, 'height': 200,
                             'viewport': None, 'axes': [],
                             'padding': {'top': 10, 'left': 30,
                                         'bottom': 20, 'right': 20},
                             'data': [],
                             'marks': [], 'scales': []}

    def test_atts(self):
        '''Test init attributes'''

        assert self.testvin.width == 400
        assert self.testvin.height == 200
        assert self.testvin.padding == {'top': 10, 'left': 30,
                                        'bottom': 20, 'right': 20}
        assert self.testvin.viewport == None
        assert self.testvin.vega == self.default_vega

    def test_keypop(self):
        '''Test vega build key removal'''
        keys = ['width', 'height', 'padding', 'viewport', 'data',
                'scales', 'axes', 'marks']
        for key in keys:
            self.testvin.build_vega(key)
            dict = self.default_vega.copy()
            dict.pop(key)
            assert self.testvin.vega == dict

    def test_updatevis(self):
        '''Test updating the visualization'''

        self.testvin.update_vis(height=300, width=1000,
                                padding={'bottom': 40,
                                         'left': 40,
                                         'right': 40,
                                         'top': 40})
        assert self.testvin.width == 1000
        assert self.testvin.height == 300
        assert self.testvin.padding == {'top': 40, 'left': 40,
                                        'bottom': 40, 'right': 40}

    def test_build_component(self):
        '''Test component build'''

        self.testvin.build_component(scales=[{"domain": {"data": "area",
                                                         "field": "data.z"},
                                              "name": "z", "type": "ordinal",
                                              "range": "height"}])
        assert self.testvin.scales[-1] == {"domain": {"data": "area",
                                                      "field": "data.z"},
                                           "name": "z", "type": "ordinal",
                                           "range": "height"}
        assert self.testvin.scales == self.testvin.vega['scales']

        self.testvin.build_component(axes=[{"scale": "x", type: "x"},
                                           {"scale": "y", type: "y"},
                                           {"scale": "z", type: "z"}])

        assert self.testvin.axes == [{"scale": "x", type: "x"},
                                     {"scale": "y", type: "y"},
                                     {"scale": "z", type: "z"}]
        assert self.testvin.axes == self.testvin.vega['axes']

    def test_update_component(self):
        '''Test component update'''

        self.testvin.build_component(axes=[{"scale": "x", type: "x"}])
        self.testvin.update_component('add', 'w', 'axes', 0, 'scale')
        assert self.testvin.axes[0]["scale"] == 'w'

        self.testvin.build_component(scales=[{"domain": {"data": "table",
                                                         "field": "data.x"},
                                             "name": "x", "type": "ordinal",
                                             "range": "width"}], append=False)
        self.testvin.update_component('add', 'data.y', 'scales', 0, 'domain',
                                      'field')
        assert self.testvin.vega['scales'][0]['domain']['field'] == 'data.y'

    def test_tabular_data(self):
        '''Test tabular data input'''

        #Lists
        self.testvin.tabular_data([10, 20, 30, 40, 50])
        assert self.testvin.data[0]['values'][0:2] == [{'x': 0, 'y': 10},
                                                       {'x': 1, 'y': 20}]
        self.testvin.tabular_data([60, 70, 80, 90, 100], append=True)
        assert self.testvin.data[0]['values'][-2:] == [{'x': 8, 'y': 90},
                                                       {'x': 9, 'y': 100}]
        #Dicts
        self.testvin.tabular_data({'A': 10, 'B': 20})
        assert self.testvin.data[0]['values'][0:2] == [{'x': 'A', 'y': 10},
                                                       {'x': 'B', 'y': 20}]
        self.testvin.tabular_data({'C': 30, 'D': 40})
        assert self.testvin.data[0]['values'][-2:] == [{'x': 'C', 'y': 30},
                                                       {'x': 'D', 'y': 40}]

        #Dataframes
        df = pd.DataFrame({'Column 1': [10, 20, 30, 40, 50],
                           'Column 2': [60, 70, 80, 90, 100]})
        df2 = pd.DataFrame({'Column 1': [60, 70, 80, 90, 100],
                            'Column 2': [65, 75, 85, 95, 105]})

        self.testvin.tabular_data(df, columns=['Column 1', 'Column 2'])
        assert self.testvin.data[0]['values'][0:2] == [{'x': 10, 'y': 60},
                                                       {'x': 20, 'y': 70}]
        self.testvin.tabular_data(df2, columns=['Column 1', 'Column 2'])
        assert self.testvin.data[0]['values'][-2:] == [{'x': 90, 'y': 95},
                                                       {'x': 100, 'y': 105}]

    def test_axis_title(self):
        '''Test the addition of axis and title labels'''

        self.testvin.axis_label(x_label='Test 1', y_label='Test 2')
        assert self.testvin.data[0]['name'] == 'x_label'
        assert self.testvin.data[0]['values'][0]['label'] == 'Test 1'
        assert self.testvin.data[1]['name'] == 'y_label'
        assert self.testvin.data[1]['values'][0]['label'] == 'Test 2'
        assert self.testvin.padding['bottom'] == 50

        self.testvin.axis_label(title='Test 3', y_label='Remove Label')
        assert self.testvin.data[1]['name'] == 'title'
        assert self.testvin.data[1]['values'][0]['label'] == 'Test 3'
        assert len(self.testvin.marks) == 2

        self.testvin.axis_label(x_label='Test 1', y_label='Test 2',
                                horiz_y=True)
        assert len(self.testvin.marks) == 3
        assert len(self.testvin.data) == 3
        assert self.testvin.padding['left'] == 120

        self.testvin.axis_label(x_label='Remove Label', y_label='Remove Label',
                                title='Remove Label')
        assert len(self.testvin.data) == 0
        assert not self.testvin.marks

    def test_iadd_isub(self):
        '''Test in-place add and subtract on some subclasses'''

        bar = vincent.Bar()
        area = vincent.Area()

        area += ({'value': 'basis'}, 'marks', 0, 'properties', 'enter',
                 'interpolate')
        bar += ('red', 'marks', 0, 'properties', 'hover', 'fill', 'value')

        assert 'interpolate' in area.marks[0]['properties']['enter']
        assert bar.marks[0]['properties']['hover']['fill']['value'] == 'red'

        bar -= ('domain', 'scales', 1)
        bar -= ('name', 'scales', 1)
        area -= ('scale', 'axes', 0)
        area -= ('type', 'axes', 1)

        assert bar.scales[1] == {'nice': True, 'range': 'height'}
        assert area.axes == [{'type': 'x'}, {'scale': 'y'}]

    def test_add_sub(self):
        '''Test add and subtract on some subclasses'''
        test_classes = [
            vincent.Bar, vincent.Area, vincent.Scatter, vincent.Line]
        for cls in test_classes:
            vis1 = cls()
            vis2 = cls()
            vis3 = cls()
            assert_vega_equal(vis1, vis2)
            assert_vega_equal(vis2, vis3)
            vis1 += ([0, 1], 'scales', 0, 'range')
            vis3 = vis2 + ([0, 1], 'scales', 0, 'range')
            assert_vega_equal(vis1, vis3)

    def test_datetimeandserial(self):
        '''Test pandas serialization and datetime parsing'''
        import pickle

        all_data = {}
        with open('%s/all_data.pickle' % data_dir, 'rb') as f:
            all_data = pickle.load(f)

        price = pd.DataFrame({tic: data['Adj Close']
                              for tic, data in all_data.iteritems()})

        scatter = vincent.Scatter()
        scatter.tabular_data(price, columns=['AAPL', 'GOOG'])
        assert scatter.data[0]['values'][0]['x'] == 10.49
        nt.assert_is_none(scatter.data[0]['values'][0]['y'])

        line = vincent.Line()
        line.tabular_data(price, columns=['AAPL'])
        assert line.data[0]['values'][0]['x'] == 1073019600000

    def test_to_json(self):
        '''Test json output

        This tests that files are written with the correct names, not that
        the json was serialized correctly.'''
        line = vincent.Line()
        line.tabular_data([1, 2, 3, 4, 5])
        from mock import call, patch, MagicMock

        with patch('__builtin__.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=file)

            path = 'test.json'
            data_path = 'test_data.json'
            default_data_path = 'data.json'
            html_path = 'test.html'
            default_html_path = 'vega_template.html'

            # No data splitting / html
            kwargs_default_behavior = [
                {}, {'split_data': False}, {'html': False},
                {'data_path': data_path}, {'html_path': html_path}]
            for kwargs in kwargs_default_behavior:
                line.to_json(path, **kwargs)
                mock_open.assert_called_once_with(path, 'w')
                mock_open.reset_mock()

            line.to_json(path, split_data=True)
            mock_open.assert_has_calls([
                call(path, 'w'), call(default_data_path, 'w')],
                any_order=True)
            mock_open.reset_mock()

            line.to_json(path, split_data=True, data_path=data_path)
            mock_open.assert_has_calls([
                call(path, 'w'), call(data_path, 'w')], any_order=True)
            mock_open.reset_mock()

            # The HTML option reads a default file that needs a real return
            # value the template substitution.
            mock_open.return_value.read.return_value = '$path'

            line.to_json(path, html=True)
            mock_open.assert_has_calls([
                call(path, 'w'), call(default_html_path, 'w')],
                any_order=True)
            mock_open.reset_mock()

            line.to_json(path, html=True, html_path=html_path)
            mock_open.assert_has_calls([
                call(path, 'w'), call(html_path, 'w')],
                any_order=True)
            mock_open.reset_mock()

    def test_deepcopy(self):
        '''Test class deepcopy behavior'''
        from copy import deepcopy

        # Note: Map requires some additional initialization and fails below.
        test_classes = [
            vincent.Bar, vincent.Area, vincent.Scatter, vincent.Line]
        for cls in test_classes:
            vis1 = cls()
            vis2 = deepcopy(vis1)
            vis3 = cls()
            assert_vega_equal(vis1, vis2)
            assert_vega_equal(vis2, vis3)
            vis1 += ([0, 1], 'scales', 0, 'range')
            assert_vega_equal(vis2, vis3)


class TestMaps(object):
    '''Class to test the Maps subclass'''
    us_states_json = path.join(data_dir, 'us-states.json')

    def setup(self):
        '''Setup method'''
        self.testmap = vincent.Map()

    def test_add_geo(self):
        '''Test adding geoJSON data to map'''

        self.testmap.geo_data(projection='albersUsa', scale=1000,
                              states=self.us_states_json)
        assert self.testmap.data[0]['url'] == 'us-states.json'
        assert self.testmap.data[0]['name'] == 'states'

    def test_append_reset_geo(self):
        '''Test appending geo, then resetting all geo'''

        self.testmap.geo_data(projection='albersUsa', scale=1000,
                              states=self.us_states_json)
        self.testmap.geo_data(states=self.us_states_json)
        assert len(self.testmap.data) == 2
        assert len(self.testmap.marks) == 2

        self.testmap.geo_data(projection='albersUsa', scale=1000,
                              reset=True, states=self.us_states_json)
        assert len(self.testmap.data) == 1
        assert len(self.testmap.marks) == 1

    def test_update_map(self):
        '''Test map updating and projection/scale retention'''

        self.testmap.geo_data(projection='albersUsa', scale=1000,
                              states=self.us_states_json)
        self.testmap.geo_data(projection='mercator', scale=100,
                              states=self.us_states_json)
        for data in self.testmap.data:
            assert data['transform'][0]['projection'] == 'albersUsa'
            assert data['transform'][0]['scale'] == 1000

        self.testmap.update_map(projection='mercator', scale=200)
        for data in self.testmap.data:
            assert data['transform'][0]['projection'] == 'mercator'
            assert data['transform'][0]['scale'] == 200

    def test_tabular_map(self):
        '''Test the binding of tabular data to map data'''

        #Just testing that marks/data syntax is created correctly,
        #not that the data keys match
        self.testmap.geo_data(projection='albersUsa', scale=1000,
                              bind_data='data.properties.name',
                              states=self.us_states_json)
        transform = {"type": "zip", "key": 'data.properties.name',
                     "with": "table", "withKey": "data.x",
                     "as": "value"}
        scales = {"name": "color",
                  "domain": {"data": "table", "field": "data.y"},
                  "range": ["#f5f5f5", "#000045"]}
        assert self.testmap.data[-1]['transform'][1] == transform
        assert self.testmap.scales[0] == scales
