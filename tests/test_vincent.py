  # -*- coding: utf-8 -*-
'''
Test Vincent
---------

'''

import pandas as pd
import vincent

class TestVincent(object):
    '''Test vincent.py'''
    
    def setup(self):
        '''Setup method'''
        
        self.testvin = vincent.Vega()
                                     
        self.default_vega = {'width': 400, 'height': 200,
                             'viewport': None, 'axes': [],
                             'padding': {'top': 10, 'left': 30, 
                                         'bottom': 20, 'right': 10}, 
                             'data': [], 'marks': [], 'scales': []}
    
    def test_atts(self):
        '''Test init attributes'''
        
        assert self.testvin.width == 400
        assert self.testvin.height == 200
        assert self.testvin.padding == {'top': 10, 'left': 30, 
                                             'bottom': 20, 'right': 10}
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
        
        self.testvin.build_component(scales={"domain": {"data": "area",
                                                        "field": "data.z"},
                                             "name":"z", "type":"ordinal", 
                                             "range":"height"})
        assert self.testvin.scales[-1] == {"domain": {"data": "area",
                                                      "field": "data.z"},
                                           "name":"z", "type":"ordinal", 
                                           "range":"height"}
        assert self.testvin.scales == self.testvin.vega['scales']
        
        self.testvin.build_component(axes=[{"scale": "x", type: "x"},
                                           {"scale": "y", type: "y"},
                                           {"scale": "z", type: "z"}], 
                                     append=False)
        assert self.testvin.axes == [{"scale": "x", type: "x"},
                                     {"scale": "y", type: "y"},
                                     {"scale": "z", type: "z"}]
        assert self.testvin.axes == self.testvin.vega['axes']
        
    def test_update_component(self):
        '''Test component update'''
        
        self.testvin.build_component(axes={"scale": "x", type: "x"})
        self.testvin.update_component('add', 'w', 'axes', 0, 'scale')
        assert self.testvin.axes[0]["scale"] == 'w'
        
        self.testvin.build_component(scales=[{"domain": {"data": "table",
                                                        "field": "data.x"},
                                             "name":"x", "type":"ordinal", 
                                             "range":"width"}], append=False)
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
          
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            

        