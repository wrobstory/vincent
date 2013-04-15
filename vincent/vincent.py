'''
Vincent
-------

A Python to Vega translator. Python data structures go in, Vega grammar
comes out. 

'''

from __future__ import print_function
import os
import json
from pkg_resources import resource_string
import pandas as pd
import pdb


class Vega(object):
    '''Vega abstract base class'''

    def __init__(self, width=400, height=200,
                 padding={'top': 10, 'left': 30, 'bottom': 20, 'right': 10},
                 viewport=None):
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
        self.padding = padding
        self.viewport = viewport
        self.visualization = {'width': self.width,
                              'padding': self.padding,
                              'viewport': self.viewport}
        self.data = []
        self.scales = []
        self.axes = []
        self.marks = []
        self.build_vega()

    def __add__(self, tuple):
        '''Allow for updating of Vega with add operator'''
        self.update_component('add', *tuple)

    def __iadd__(self, tuple):
        '''Allow for updating of Vega with iadd operator'''
        self.update_component('add', *tuple)
        return self

    def __sub__(self, tuple):
        '''Allow for updating of Vega with sub operator'''
        self.update_component('remove', *tuple)

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
        >>>my_vega.update_component(add, 'w', 'axes', 0, 'scale')
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

    def to_json(self, path, split_data=False, html=False):
        '''
        Save Vega object to JSON

        Parameters:
        -----------
        path: string
            File path for Vega grammar JSON.
        split_data: boolean, default False
            Split the output into a JSON with only the data values, and a
            Vega grammar JSON referencing that data.
        html: boolean, default False
            Output Vega Scaffolding HTML file to path

        '''

        def json_out(path, output):
            '''Output to JSON'''
            with open(path, 'w') as f:
                json.dump(output, f, sort_keys=True, indent=4,
                          separators=(',', ': '))

        if split_data:
            data_out = self.data[0]['values']
            self.update_component('remove', 'values', 'data', 0)
            self.update_component('add', 'data.json', 'data', 0, 'url')
            data_path = os.path.dirname(path) + r'/data.json'
            json_out(data_path, data_out)
            json_out(path, self.vega)
            if html:
                template = resource_string('vincent', 'vega_template.html')
                html_path = ''.join([os.path.dirname(path),
                                     r'/vega_template.html'])
                with open(html_path, 'w') as f:
                    f.write(template)

            self.tabular_data(self.raw_data)
            
        else:
            json_out(path, self.vega)

    def tabular_data(self, data, name="table", columns=None, use_index=False,
                     append=False):
        '''Create the data for a bar chart in Vega grammer. Data can be passed
        in a list, dict, or Pandas Dataframe. 

        Parameters:
        -----------
        name: string, default "table"
            Type of visualization
        columns: list, default None
            If passing Pandas DataFrame, you must pass at least one column
            name.If one column is passed, x-values will default to the index
            values.If two column names are passed, x-values are columns[0],
            y-values columns[1].
        use_index: boolean, default False
            Use the DataFrame index for your x-values
        append: boolean, default False
            Append new data to data already in vincent object

        Examples:
        ---------
        >>>myvega.tabular_data([10, 20, 30, 40, 50])
        >>>myvega.tabular_data({'A': 10, 'B': 20, 'C': 30, 'D': 40, 'E': 50}
        >>>myvega.tabular_data(my_dataframe, columns=['column 1'],
                               use_index=True)
        >>>myvega.tabular_data(my_dataframe, columns=['column 1', 'column 2'])

        '''
        
        self.raw_data = data

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
            values = [{"x": x, "y": y} for x, y in data.iteritems()]

        #Dataframes
        if isinstance(data, pd.DataFrame):
            if len(columns) > 1 and use_index:
                raise ValueError('If using index as x-axis, len(columns)'
                                 'cannot be > 1')
            if use_index or len(columns) == 1:
                values = [{"x": x[0], "y": x[1][columns[0]]}
                          for x in data.iterrows()]
            else:
                values = [{"x": x[1][columns[0]], "y": x[1][columns[1]]}
                          for x in data.iterrows()]

        if append:
            self.data[0]['values'].extend(values)
        else:
            self.data = []
            self.data.append({"name": name, "values": values})

        self.build_vega()


class Bar(Vega):
    '''Create a bar chart in Vega grammar'''

    def __init__(self):
        '''Build Vega Bar chart with default parameters'''
        super(Bar, self).__init__()

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

    def __init__(self):
        '''Build Vega Area chart with default parameters'''
        super(Area, self).__init__()
        area_updates = [('remove', 'width', 'marks', 0, 'properties', 'enter'),
                        ('add', 'area', 'marks', 0, 'type'),
                        ('add', 'linear', 'scales', 0, 'type')]

        self.multi_update(area_updates)
        self.build_vega()


class Scatter(Bar):
    '''Create a scatter plot in Vega grammar'''

    def __init__(self):
        '''Build Vega Scatter chart with default parameters'''
        super(Scatter, self).__init__()
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

    def __init__(self):
        '''Build Vega Line plot chart with default parameters'''

        pass

        #Something still broken- need to do some syntax hunting...
        super(Line, self).__init__()
        line_updates = [('add', 'linear', 'scales', 0, 'type'),
                        ('remove', 'update', 'marks', 0, 'properties'),
                        ('remove', 'hover', 'marks', 0, 'properties'),
                        ('remove', 'width', 'marks', 0, 'properties', 'enter'),
                        ('add', 'line', 'marks', 0, 'type'),
                        ('add', {'value': '#2a3140'}, 'marks', 0,
                         'properties', 'enter', 'stroke'),
                        ('add', {'value': 2}, 'marks', 0, 'properties',
                         'enter', 'strokeWidth')]

        self.multi_update(line_updates)
        self.build_vega()
