# -*- coding: utf-8 -*-
'''
Vincent
-------

A Python to Vega translator. Python data structures go in, Vega grammar
comes out.

'''

from __future__ import print_function
from __future__ import division
import os
import json
import time
import itertools
from copy import deepcopy
from pkg_resources import resource_string
from string import Template
import pandas as pd


class Vega(object):
    '''Vega abstract base class'''

    def __init__(self, width=400, height=200, padding=None, viewport=None):
        '''
        The Vega classes generate JSON output in Vega grammar, a
        declarative format for creating and saving visualization designs.
        This class is meant to be an abstract base class on which to build
        the other piece of the complete VEGA specification.

        A Vega object is instantiated with only the Vega Visualization basic,
        properties, with default values for the name, width, height, padding,
        and viewport.

        Parameters:
        -----------

        width: int, default 800
            Width of the visualization
        height: int, default 400
            Height of the visualization
        padding: dict, default {'top': 10, 'left': 30, 'bottom':20, 'right':10}
            Internal margins for the visualization, Top, Left, Bottom, Right
        viewport: list, default None
            Width and height of on-screen viewport

        '''

        self.width = width
        self.height = height
        self.padding = padding or {
            'top': 10, 'left': 30, 'bottom': 20, 'right': 20
        }
        self.viewport = viewport
        self.visualization = {'width': self.width,
                              'padding': self.padding,
                              'viewport': self.viewport}
        self.data = []
        self.scales = []
        self.axes = []
        self.axis_labels = {}
        self.marks = []
        self.build_vega()

    def __deepcopy__(self, memo):
        vis = self.__class__()
        copy_attrib = [
            'width', 'height', 'padding', 'viewport', 'visualization',
            'data', 'scales', 'axes', 'axis_labels', 'marks']
        for attr in copy_attrib:
            setattr(vis, attr, deepcopy(getattr(self, attr), memo))
        return vis

    def __add__(self, tuple):
        '''Allow for updating of Vega with add operator'''
        vis = deepcopy(self)
        vis.update_component('add', *tuple)
        return vis

    def __iadd__(self, tuple):
        '''Allow for updating of Vega with iadd operator'''
        self.update_component('add', *tuple)
        return self

    def __sub__(self, tuple):
        '''Allow for updating of Vega with sub operator'''
        vis = deepcopy(self)
        vis.update_component('add', *tuple)
        return vis

    def __isub__(self, tuple):
        '''Allow for updating of Vega with sub operator'''
        self.update_component('remove', *tuple)
        return self

    def build_vega(self, *args):
        '''Build complete vega specification. String arguments passed will not
        be included in vega dict.

        Ex: object.build_vega('viewport')

        '''

        keys = ['width', 'height', 'padding', 'viewport', 'data',
                'scales', 'axes', 'marks']
        self.vega = {}
        for key in keys:
            if key not in args:
                self.vega[key] = getattr(self, key)

    def update_vis(self, **kwargs):
        '''
        Update Vega Visualization basic properties:
        width, height, padding, viewport

        Ex: >>>my_vega.update_vis(height=800, width=800)
        '''

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        self.build_vega()

    def axis_label(self, x_label=None, y_label=None, title=None,
                   horiz_y=False):
        '''
        Add axis labels to your visualization.

        Labels can be added or changed individually. To remove a label,
        pass "Remove Label" to the axis label you wish to remove.

        Parameters:
        -----------
        x_label: string, default None
            X-axis label.
        y_label: string, default None
            Y-axis label
        title: string, default None
            Visualization Title (defaults to top of vis)
        horiz_y: boolean, default False
            Pass "True" to plot y-axis label horizontally

        Examples:
        ---------
        >>>vis.axis_label(x_label='X Data')
        >>>vis.axis_label(x_label='New X Label', y_label='Y Data')
        >>>vis.axis_label(y_label='New Y Label', x_label='Remove Label')

        '''
        temp = {'x_label': x_label, 'y_label': y_label, 'title': title}
        for label, name in temp.iteritems():
            if name:
                self.axis_labels[label] = name

        x_mark = {"type": "text", "name": "x_label",
                  "from": {"data": "x_label"},
                  "properties": {"enter": {
                                 "x": {"value": self.width/2},
                                 "y": {"value": self.height},
                                 "dy": {"value": 35}}}}
        y_mark = {"type": "text", "name": "y_label",
                  "from": {"data": "y_label"},
                  "properties": {"enter": {
                                 "x": {"value": 0},
                                 "y": {"value": self.height/2},
                                 "dy": {"value": -45},
                                 "angle": {'value': -90}}}}
        if horiz_y:
            y_mark['properties']['enter'].pop('dy')
            y_mark['properties']['enter']['dx'] = {'value': -65}
            y_mark['properties']['enter']['angle'] = {'value':  0}

        title_mark = {"type": "text", "name": "title",
                      "from": {"data": "title"},
                      "properties": {"enter": {
                                     "x": {"value": self.width/2},
                                     "y": {"value": 0},
                                     "dy": {"value": -20}}}}

        common_pars = {"baseline": {"value": "middle"},
                       "align": {"value": "center"},
                       "fill": {"value": "#000"},
                       "text": {"field": "data.label"},
                       "font": {"value": "Helvetica Neue"},
                       "fontSize": {"value": 14}}

        marks = {'x_label': x_mark, 'y_label': y_mark, 'title': title_mark}

        def label_update(key, value, component, remove):
            '''Check component for axis label, append/insert/pop
            as required'''
            comp = getattr(self, component)
            for index, att in enumerate(comp):
                if att.get('name') == key:
                    comp.pop(index)
                    if remove != 'Remove Label':
                        comp.insert(index, value)
                    return
            if remove != 'Remove Label':
                comp.append(value)
            return

        for key, value in self.axis_labels.iteritems():
            label_data = {'name': key, 'values': [{'label': value}]}
            marks[key]['properties']['enter'].update(common_pars)
            remove = value
            label_update(key, label_data, 'data', remove)
            label_update(key, marks[key], 'marks', remove)

        left, top, bottom = 30, 10, 20
        if self.axis_labels.get('y_label'):
            if horiz_y:
                left = 120
            else:
                left = 60
        if self.axis_labels.get('title'):
            top = 30
        if self.axis_labels.get('x_label'):
            bottom = 50

        self.update_vis(padding={'bottom': bottom,
                                 'left': left, 'right': self.padding['right'],
                                 'top': top})

    def build_component(self, append=True, **kwargs):
        '''Build complete Vega component.

        The Vega grammar will update with passed keywords. This method
        rebuilds an entire Vega component: axes, data, scales, marks, etc.

        Examples:
        >>>my_vega.build_component(scales=[{"domain": {"data": "table",
                                                      "field": "data.x"},
                                            "name":"x", "type":"ordinal",
                                            "range":"width"}])
        >>>my_vega.build_component(axes=[{"scale": "x", type: "x"},
                                         {"scale": "y", type: "y"}],
                                   append=False)

        '''

        for key, value in kwargs.iteritems():
                setattr(self, key, value)

        self.build_vega()

    def update_component(self, change, value, parameter, index, *args):
        '''Update individual parameters of any component.

        Parameters:
        -----------
        change: string, either 'add' or 'remove'
            'add' will add the value to the last specified key in *args (this
            can be a new key). 'remove' will remove the key specified by
            'value'.
        value: Any JSON compatible datatype
            The value you want to substitute into the component
        parameter: string
            The Vega component you want to modify (scales, marks, etc)
        index: int
            The index of dict/object in the component array you want to mod

        Examples:
        >>>my_vega.update_component('add', 'w', 'axes', 0, 'scale')
        >>>my_vega.update_component('remove', 'width', 'marks', 0,
                                    'properties', 'enter')

        '''
        def set_keys(value, param, key, *args):
            if args:
                return set_keys(value, param.get(key), *args)
            if change == 'add':
                param[key] = value
            else:
                param[key].pop(value)

        parameter = getattr(self, parameter)[index]
        if not args:
            args = [value]
            if change == 'remove':
                parameter.pop(value)
                self.build_vega()
                return
        set_keys(value, parameter, *args)

        self.build_vega()

    def multi_update(self, comp_list):
        '''Pass a list of component updates to change all'''

        for update in comp_list:
            self.update_component(*update)

    def _json_IO(self, host, port):
        '''Return data values as JSON for StringIO '''

        data_vals = self.data[0]['values']
        self.update_component('remove', 'values', 'data', 0)
        url = ''.join(['http://', host, ':', str(port), '/data.json'])
        self.update_component('add', url, 'data', 0, 'url')
        vega = json.dumps(self.vega, sort_keys=True, indent=4)
        data = json.dumps(data_vals, sort_keys=True, indent=4)
        return vega, data

    def to_json(self, path, split_data=False, data_path='data.json',
                html=False, html_path='vega_template.html'):
        '''
        Save Vega object to JSON

        Parameters:
        -----------
        path: string
            File path for Vega grammar JSON.
        split_data: boolean, default False
            Split the output into a JSON with only the data values, and a
            Vega grammar JSON referencing that data.
        data_path: string, default 'data.json'
            Path for data file. Does nothing if `split_data` is False.
        html: boolean, default False
            Output Vega scaffolding HTML file.
        html_path: string, default 'vega_template.html'
            Path for the scaffolding HTML file. Does nothing if `html` is
            False.
        '''

        def json_out(path, output):
            '''Output to JSON'''
            with open(path, 'w') as f:
                json.dump(output, f, sort_keys=True, indent=4,
                          separators=(',', ': '))

        if split_data:
            name = self.data[0]['name']
            data_out = self.data[0]['values']
            self.update_component('remove', 'values', 'data', 0)
            self.update_component('add', data_path, 'data', 0, 'url')
            json_out(data_path, data_out)
            json_out(path, self.vega)

            #Reset our data in the Vega object
            self.data.pop(0)
            self.data.insert(0, {'name': name, 'values': data_out})
            self.build_vega()
        else:
            json_out(path, self.vega)

        if html:
            template = Template(
                resource_string('vincent', 'vega_template.html'))
            with open(html_path, 'w') as f:
                f.write(template.substitute(path=path))

    def _serial_transform(self, str_time):
        '''Transform data to make it JSON serializable. Vega requires
        Epoch time in milliseconds, and it will be converted to local
        timestamp, not UTC.'''
        for objs in self.data[0]['values']:
            for key, value in objs.iteritems():
                if isinstance(value, pd.Period):
                    value = value.to_timestamp()
                if pd.isnull(value):
                    objs[key] = None
                elif (isinstance(value, pd.tslib.Timestamp) or
                      isinstance(value, pd.Period)):
                    objs[key] = time.mktime(value.timetuple())*1000

    def tabular_data(self, data, columns=None, use_index=False,
                     append=False, axis_time='day'):
        '''Create the data for a bar chart in Vega grammer. Data can be passed
        in a list, dict, or Pandas Dataframe.

        All time series will be transformed into local Epoch time. Ensure that
        any timestamps have been converted to local time in Pandas before
        plotting for accurate axis timestamping.

        Parameters:
        -----------
        data: Tuples, List, Dict, Pandas Series, or Pandas DataFrame
            Input data
        columns: list, default None
            If passing Pandas DataFrame, you must pass at least one column
            name.If one column is passed, x-values will default to the index
            values.If two column names are passed, x-values are columns[0],
            y-values columns[1].
        use_index: boolean, default False
            Use the DataFrame index for your x-values
        append: boolean, default False
            Append new data to data already in vincent object
        axis_time: string, default 'day'
            Time scale for axis. Must be one of 'second', 'minute', 'hour',
            'day', 'week', 'month', or 'year'

        Examples:
        ---------
        >>>myvega.tabular_data([10, 20, 30, 40, 50])
        >>>myvega.tabular_data({'A': 10, 'B': 20, 'C': 30, 'D': 40, 'E': 50}
        >>>myvega.tabular_data(my_dataframe, columns=['column 1'],
                               use_index=True)
        >>>myvega.tabular_data(my_dataframe, columns=['column 1', 'column 2'])


        '''

        self.raw_data = data

        def period_axis(data, axis_time):
            '''Update to Time Scale if DatetimeIndex'''
            if isinstance(data.index, pd.DatetimeIndex):
                self.update_component('add', 'time', 'scales', 0,
                                      'type')
                self.update_component('add', axis_time, 'scales', 0,
                                      'nice')

        #Tuples
        if isinstance(data, tuple):
            values = [{"x": x[0], "y": x[1]} for x in data]

        #Lists
        if isinstance(data, list):
            if append:
                start = self.data[0]['values'][-1]['x'] + 1
                end = len(self.data[0]['values']) + len(data)
            else:
                start, end = 0, len(data)

            default_range = xrange(start, end+1, 1)
            values = [{"x": x, "y": y} for x, y in zip(default_range, data)]

        #Dicts
        if isinstance(data, dict) or isinstance(data, pd.Series):
            if isinstance(data, pd.Series):
                period_axis(data, axis_time)
            values = [{"x": x, "y": y} for x, y in data.iteritems()]

        #Dataframes
        if isinstance(data, pd.DataFrame):
            if len(columns) > 1 and use_index:
                raise ValueError('If using index as x-axis, len(columns)'
                                 'cannot be > 1')
            if use_index or len(columns) == 1:
                period_axis(data, axis_time)
                values = [{"x": x[0], "y": x[1][columns[0]]}
                          for x in data.iterrows()]
            else:
                values = [{"x": x[1][columns[0]], "y": x[1][columns[1]]}
                          for x in data.iterrows()]

        if append:
            self.data[0]['values'].extend(values)
        else:
            filter = lambda x: x.get('name') == 'table'
            self.data = list(itertools.ifilterfalse(filter, self.data))
            self.data.insert(0, {"name": "table", "values": values})

        self._serial_transform(axis_time)
        self.build_vega()


class Bar(Vega):
    '''Create a bar chart in Vega grammar'''

    def __init__(self, **kwargs):
        '''Build Vega Bar chart with default parameters'''
        super(Bar, self).__init__(**kwargs)

        self.scales = [{"name": "x", "type": "ordinal", "range": "width",
                        "domain": {"data": "table", "field": "data.x"}},
                       {"name": "y", "range": "height", "nice": True,
                        "domain": {"data": "table", "field": "data.y"}}]

        self.axes = [{"type": "x", "scale": "x"}, {"type": "y", "scale": "y"}]

        self.marks = [{"type": "rect", "from": {"data": "table"},
                       "properties": {
                           "enter": {
                               "x": {"scale": "x", "field": "data.x"},
                               "width": {"scale": "x", "band": True,
                                         "offset": -1},
                               "y": {"scale": "y", "field": "data.y"},
                               "y2": {"scale": "y", "value": 0}
                           },
                           "update": {"fill": {"value": "#2a3140"}},
                           "hover": {"fill": {"value": "#a63737"}}
                       }
                       }]

        self.build_vega()


class Area(Bar):
    '''Create an area chart in Vega grammar'''

    def __init__(self, **kwargs):
        '''Build Vega Area chart with default parameters'''
        super(Area, self).__init__(**kwargs)
        area_updates = [('remove', 'width', 'marks', 0, 'properties', 'enter'),
                        ('add', 'area', 'marks', 0, 'type'),
                        ('add', 'linear', 'scales', 0, 'type')]

        self.multi_update(area_updates)
        self.build_vega()


class Scatter(Bar):
    '''Create a scatter plot in Vega grammar'''

    def __init__(self, **kwargs):
        '''Build Vega Scatter chart with default parameters'''
        super(Scatter, self).__init__(**kwargs)
        self.height, self.width = 400, 400
        self.padding = {'top': 40, 'left': 40, 'bottom': 40, 'right': 40}
        scatter_updates = [('remove', 'type', 'scales', 0),
                           ('add', True, 'scales', 0, 'nice'),
                           ('remove', 'width', 'marks', 0, 'properties',
                            'enter'),
                           ('remove', 'y2', 'marks', 0, 'properties',
                            'enter'),
                           ('remove', 'hover', 'marks', 0, 'properties'),
                           ('add', {'value': '#2a3140'}, 'marks', 0,
                            'properties', 'enter', 'stroke'),
                           ('add', {'value': 0.9}, 'marks', 0, 'properties',
                            'enter', 'fillOpacity'),
                           ('add', 'symbol', 'marks', 0, 'type')]

        self.multi_update(scatter_updates)
        self.build_vega()


class Line(Bar):
    '''Create a line plot in Vega grammar'''

    def __init__(self, **kwargs):
        '''Build Vega Line plot chart with default parameters'''

        super(Line, self).__init__(**kwargs)
        line_updates = [('add', 'linear', 'scales', 0, 'type'),
                        ('remove', 'update', 'marks', 0, 'properties'),
                        ('remove', 'hover', 'marks', 0, 'properties'),
                        ('remove', 'width', 'marks', 0, 'properties', 'enter'),
                        ('remove', 'y2', 'marks', 0, 'properties',
                         'enter'),
                        ('add', 'line', 'marks', 0, 'type'),
                        ('add', {'value': '#2a3140'}, 'marks', 0,
                         'properties', 'enter', 'stroke'),
                        ('add', {'value': 2}, 'marks', 0, 'properties',
                         'enter', 'strokeWidth')]

        self.multi_update(line_updates)
        self.build_vega()


class Map(Vega):
    '''Create a map plot in Vega grammar'''

    def __init__(self, **kwargs):
        '''Build Vega Map chart with default parameters'''
        super(Map, self).__init__(**kwargs)

        self.data = []
        self.geojson = {}
        self.map_par = {}
        self.build_vega('axes', 'scales')

    def spatial_to_geoJSON(self, data_path=None, json_out=None):
        '''Write a spatial file to geoJSON via Ogre

        Call the Ogre spatial file converter:
        http://ogre.adc4gis.com/ to transform your data into
        to geoJSON for Vincent.

        Parameters:
        -----------
        spatial_path: string, default None
            Path to spatial files. Please see http://ogre.adc4gis.com/ for
            the type of data that can be passed. Zipped shapefiles must have
            .shp, .dbf, and .shx (.prj optional)
        json_out: string, default None
            Path to write geoJSON output. If None, will default to same
            path as shp_path

        Examples:
        ---------
        >>>vis.shapefile_to_json(shp_path=r'countries.zip')

        '''
        import requests
        url = r'http://ogre.adc4gis.com/convert'
        shp_data = {'upload': open(data_path, 'rb')}
        print('Calling Ogre to perform geoJSON conversion...')
        try:
            r = requests.post(url, files=shp_data)
        except:
            print("There was an error with the HTTP request")
            raise
        r.raise_for_status()
        if json_out:
            path = '.'.join([name, 'json'])
        else:
            dir, zip = os.path.split(data_path)
            geoJSON = '.'.join([zip.split('.')[0], 'json'])
            path = '/'.join([dir, geoJSON])
        print('Writing to geoJSON. This may take some time if your spatial'
              ' file is high resolution.')
        with open(path, 'w') as f:
            json.dump(r.json, f, sort_keys=True, indent=4,
                      separators=(',', ': '))

    def update_map(self, projection=None, scale=None):
        '''Update the map projection or scale'''

        if not projection:
            projection = self.map_par.get('projection', 'mercator')
        if not scale:
            scale = self.map_par.get('scale', 100)

        self.map_par.update({'projection': projection, 'scale': scale})

        for data in self.data:
            if data.get('transform'):
                data['transform'][0].update({'projection': projection,
                                             'scale': scale})

    def geo_data(self, scale=100, projection='winkel3', reset=False,
                 bind_data=None, spatial_convert=False, **kwargs):
        '''Create the data for a map in Vega grammar.

        Each set of map data is passed as a keyword argument, with the key as
        the data name and the value the data path. Tabular data can be bound
        to geo_data to create chloropleth maps.

        Vincent/Vega support D3 geo projections:
        https://github.com/mbostock/d3/wiki/Geo-Projections

        Once a set of map data has been passed, subsequent map datasets will
        retain the scale and parameter of the original data, unless reset=True
        is passed. Scale/Projection can be changed for all maps with the
        `update_map` method.

        Parameters:
        -----------
        scale: int, default 100
            Map scale
        projection: string, default 'mercator'
            Map projection
        reset: boolean, default False
            reset=True will remove all existing map datasets
        bind_data: string, default None
            Bind the geo_data to the tabular data in the vincent object. The
            passed string references a geoJSON data attribute
            (id, properties, etc). This data must match the x-column of the
            tabular_data to plot correctly.
        spatial_convert: boolean, default False
            If True, Vincent will call the online Ogre converter to convert
            the spatial file to geoJSON via the spatial_to_geoJSON method.
        kwargs: keyword argument
            Pass paths to map data, with the passed keyword as the name
            of the dataset. Can pass geoJSON or shapefiles; if shapefile is
            passed, 'shapefile=True' must be passed as a keyword argument.

        Examples:
        ---------
        #Plot both counties and states, bind data to counties
        >>>vis = vincent.Map()
        >>>vis.tabular_data(county_data_dataframe, columns=['ID', 'Data'])
        >>>vis.geo_data(scale=1000, projection='albersUsa',
                        states=r'/states.json')
        >>>vis.geo_data(bind_data='data.id', counties=r'/counties.json')

        #Change the tabular data to state-level, reset map data
        >>>vis.tabular_data(state_data_dataframe, columns=['name', 'Data'])
        >>>vis.geo_data(scale=1000, projection='albersUsa',
                        bind_data='data.properties.name', reset=True,
                        states=r'/states.json')

        '''

        self.map_par['projection'] = self.map_par.get('projection', projection)
        self.map_par['scale'] = self.map_par.get('scale', scale)

        for name, url in kwargs.iteritems():

            if spatial_convert:
                self.spatial_to_geoJSON(data_path=url)
                url = '.'.join([os.path.splitext(url)[0], 'json'])

            self.geojson[name] = {}
            self.geojson[name]['file'] = os.path.split(url)[-1]
            with open(url, 'r') as f:
                self.geojson[name]['data'] = json.load(f)

            if reset:
                self.map_par['projection'] = projection
                self.map_par['scale'] = scale
                filter_data = lambda x: x.get('name') == 'table'
                filter_mark = lambda x: x.get('name') == 'mapmark'
                self.data = list(itertools.ifilter(filter_data, self.data))
                self.marks = list(itertools.ifilterfalse(filter_mark,
                                                         self.marks))

            mapdata = {'name': name, 'url': self.geojson[name]['file'],
                       'format': {'type': 'json',
                                  'property': 'features'},
                       'transform': [{'type': 'geopath',
                                      'value': 'data',
                                      'scale': self.map_par['scale'],
                                      'projection': self.map_par['projection']
                                      }]}
            self.data.append(mapdata)

            mapmark = {"type": "path", 'from': {'data': name},
                       'name': 'mapmark',
                       "properties": {
                           "enter": {
                           "stroke": {'value': '#fff'},
                           "strokeWidth": {"value": 1.0},
                           "path": {"field": "path"},
                           "fill": {'value': '#2a3140'}
                           }}}
            self.marks.append(mapmark)

            if bind_data:
                transform = {"type": "zip", "key": bind_data,
                             "with": "table", "withKey": "data.x",
                             "as": "value"}
                scales = {"name": "color",
                          "domain": {"data": "table", "field": "data.y"},
                          "range": ["#f5f5f5", "#000045"]}
                marks = {"fill": {"scale": "color", "field": "value.data.y"}}
                self.data[-1]['transform'].append(transform)
                self.scales.append(scales)
                self.marks[-1]['properties'].update({'update': marks})

            self.build_vega()

    def to_json(self, path, **kwargs):
        '''Map-specific JSON write. Always writes geoJSON to separate file
        in path of vega.json file'''

        super(Map, self).to_json(path, **kwargs)

        for key, value in self.geojson.iteritems():
            path_test = os.path.split(path)[0]
            if path_test == '':
                geo_path = ''.join([os.path.split(path)[0], value['file']])
            else:
                geo_path = '/'.join([os.path.split(path)[0], value['file']])
            with open(geo_path, 'w') as f:
                json.dump(value['data'], f, sort_keys=True, indent=4,
                          separators=(',', ': '))
