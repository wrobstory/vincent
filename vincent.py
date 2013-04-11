'''
Vincent
----

A Python to Vega translator.  

'''

import json
import pandas as pd

class Vega(object): 
    '''Vega abstract base class'''
    
    def __init__(self, name='Vega', width=400, height=200,
                 padding={'top': 10, 'left': 30, 'bottom': 20, 'right': 10},
                 viewport=None):
        '''
        The Vega classes generate JSON output in Vega grammer, a
        declarative format for creating and saving visualization designs.
        This class is meant to be an abstract base class on which to build
        the other piece of the complete VEGA specification. 
        
        A Vega object is initialized with only the Vega Visualization basic, 
        properties, with default values for the name, width, height, padding, 
        and viewport.
        
        Parameters:
        -----------
        name: string, default 'Vega'
            Name of the visualization
        width: int, default 800
            Width of the visualization
        height: int, default 400
            Height of the visualization
        padding: dict, default {'top': 10, 'left': 30, 'bottom': 20, 'right': 10}
            Internal margins for the visualization, Top, Left, Bottom, Right
        viewport: list, default None
            Width and height of on-screen viewport
            
        '''
        
        self.name = name
        self.width = width
        self.height = height
        self.padding = padding
        self.viewport = viewport
        self.visualization = {'name': self.name, 'width': self.width, 
                              'padding': self.padding, 
                              'viewport': self.viewport}
        self.data = []
        self.scales = []
        self.axes = []
        self.marks = []
        self.build_vega()
    
    def build_vega(self, *args):
        '''Build complete vega specification. String arguments passed will not
        be included in vega dict. 
        
        Ex: object._build_vega('viewport')
        
        '''
        
        keys = ['name', 'width', 'height', 'padding', 'viewport', 'data', 
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
        '''Build complete Vega component. The Vega grammar will update with
        passed keywords. This method defaults to appending to the existing 
        component; if you want to rebuild the component entirely, you must 
        pass append=False and the component as a list. 
        
        Examples:
        >>>my_vega.build_component(scales={"domain": {"data": "table",
                                                      "field": "data.x"},
                                           "name":"x", "type":"ordinal", 
                                           "range":"width"})
        >>>my_vega.build_component(axes=[{"scale": "x", type: "x"},
                                         {"scale": "y", type: "y"}], 
                                   append=False)
        
        '''

        for key, value in kwargs.iteritems(): 
            if append: 
                getattr(self, key).append(value)
            else: 
                setattr(self, key, value)
        
        self.build_vega()
        
    def update_component(self, value, component, index, *args):
        '''Update individual parameters of any component. 
        
        Parameters: 
        -----------
        value: Any JSON compatible datatype
            The value you want to substitute into the component
        component: string
            The Vega component you want to modify (scales, marks, etc)
        index: int
            The index of dict/object in the component array you want to mod
        
        Examples:
        >>>my_vega.update_component('w', 'axes', 0, 'scale')
        >>>my_vega.update_component(property='marks', index=0, type=rect,
                                   hover= {"fill": {"value: "red"}}

        ''' 
        def set_keys(value, param, key, *args):
            if args: 
                return set_keys(value, param.get(key), *args)
            param[key] = value
            
        parameter = getattr(self, component)[index]
        set_keys(value, parameter, *args)
        
        self.build_vega()
                           
    def to_json(self, path):
        '''
        Save Vega object to JSON
        
        Parameters: 
        -----------
        path: string
            Save path
            
        '''
        
        with open(path, 'w') as f: 
            json.dump(self.vega, f, sort_keys=True, indent=4,
                      separators=(',', ': '))
                      
    def tabular_data(self, data, name="table", columns=None, use_index=False,
                     append=False):
        '''Create the data for a bar chart in Vega grammer. Data can be passed
        in a list, dict, or Pandas Dataframe. Note: old data is overwritten 
        
        Parameters:
        -----------
        name: string, default "VegaBar"
            If passed as a list or dict, the name will default to the name 
            passed name parameter. If a DataFrame, the name parameter will use
            the DataFrame name if provided
        columns: list, default None
            If passing Pandas DataFrame, you must pass at least one column name. 
            If one column is passed, x-values will default to the index values.
            If two column names are passed, x-values are columns[0], y-values 
            columns[1]./
        
        Examples: 
        ---------
        >>>myvega.tabular_data([10, 20, 30, 40, 50])
        >>>myvega.tabular_data({'A': 10, 'B': 20, 'C': 30, 'D': 40, 'E': 50}
        >>>myvega.tabular_data(my_dataframe, columns=['column 1'], use_index=True)
        >>>myvega.tabular_data(my_dataframe, columns=['column 1', 'column 2'])

        '''
        
        if isinstance(data, list):
            if append:
                start = self.data[0]['values'][-1]['x'] + 1
                end = len(self.data) + len(data)
            else: 
                start, end = 0, len(data)
                
            default_range = xrange(start, end+1, 1)
            values = [{"x": x, "y": y} for x, y in zip(default_range, data)]
            
        if isinstance(data, dict) or isinstance(data, pd.Series):
            values = [{"x": x, "y": y} for x, y in data.iteritems()]
   
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
            if not self.data[0]['name']:
                raise ValueError('There is no existing data to append')
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
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
           
           