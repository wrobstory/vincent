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
                 viewport=[]):
        '''
        The Vega classes generate JSON output in Vega grammer, a
        declarative format for creating and saving visualization designs.
        This class is meant to be an abstract base class on which to build
        the other piece of the complete VEGA specification. 
        
        A Vega object is initialized at the top level as a Vega Visualization, 
        with default values for the name, width, height, padding, and viewport.
        
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
        viewport: list, default []
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
        self._build_vega()
    
    def _build_vega(self, *args):
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
                
    def update_viz(self, **kwargs):
        '''
        Update Vega top level Visualization property:
        width, height, padding, viewport
        
        Ex: >>>my_vega.build_viz(height=800, width=800)
        '''
        
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
            
        self._build_vega()
        
        
    def build_property(self, **kwargs):
        '''Build top-level Vega property. The Vega grammar will update with
        passed keywords.
        
        Examples:
        >>>my_vega.build_property(scales = {"name":"x", "type":"ordinal", 
                                            "range":"width"})
        >>>my_vega.build_property(width=400, height=800)                                            
        '''

        for key, value in kwargs.iteritems(): 
            getattr(self, key).append(value)
        
        self._build_vega()
        
    def update_property(self, property=None, index=None, **kwargs):
        '''Update individual parameters of any property.''' 
        
        pass
        
        for key, value in kwargs.iteritems():
            getattr(self, property)[index].update({key: value})
        
        self._build_vega()
                           
    def to_json(self, path):
        '''
        Save Vega object to JSON
        
        Parameters: 
        -----------
        path: string
            Save path
        '''
        
        with open(path, 'w') as f: 
            json.dump(self.vega, f, sort_keys=True, indent=0,
                      separators=(',', ': '))
                      
    def tabular_data(self, data, name="table", columns=None, use_index=False):
        '''Create the data for a bar chart in Vega grammer. Data can be passed
        in a list, dict, or Pandas Dataframe. 
        
        Parameters:
        -----------
        name: string, default "VegaBar"
            If passed as a list or dict, the name will default to the name 
            passed name parameter. If a DataFrame, the name parameter will use
            the DataFrame name if provided
        columns: list, default None
            If passing Pandas DataFrame, you must pass at least one colum name. 
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
            default_range = xrange(1, len(data)+1, 1)
            values = [{"x": x, "y": y} for x, y in zip(default_range, data)]
            
        if isinstance(data, dict):
            values = [{"x": x, "y": y} for x, y in data.iteritems()]
            
        if isinstance(data, pd.DataFrame):
            if len(columns) > 1 and use_index: 
                raise ValueError('If using index as x-axis, len(columns)'
                                 'cannot be > 1')
            if use_index or len(columns) == 1: 
                values = [{"x": x[0], "y": x[1][columns[0]]} 
                           for x in data.iterrows()]
            
            values = [{"x": x[1][columns[0]], "y": x[1][columns[1]]} 
                      for x in data.iterrows()]
             
        self.data.append({"name": name, "values": values})
        self._build_vega()                 
                      
class Bar(Vega):
    '''Create a bar chart in Vega grammar'''
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
           
           