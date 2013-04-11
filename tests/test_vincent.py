  # -*- coding: utf-8 -*-
'''
Test Vincent
---------

'''

import vincent

class TestVincent(object):
    '''Test vincent.py'''
    
    def setup(self):
        '''Setup method'''
        
        self.testvin = vincent.Vega()
                                     
        self.default_vega = {'name': 'Vega', 'width': 400, 'height': 200,
                             'viewport': None, 'axes': [],
                             'padding': {'top': 10, 'left': 30, 
                                         'bottom': 20, 'right': 10}, 
                             'data': [], 'marks': [], 'scales': []}
    
    def test_atts(self):
        '''Test init attributes'''
        
        assert self.testvin.name == 'Vega'
        assert self.testvin.width == 400
        assert self.testvin.height == 200
        assert self.testvin.padding == {'top': 10, 'left': 30, 
                                             'bottom': 20, 'right': 10}
        assert self.testvin.viewport == None
        assert self.testvin.vega == self.default_vega
        
    def test_keypop(self):
        '''Test vega build key removal'''
        keys = ['name', 'width', 'height', 'padding', 'viewport', 'data', 
                'scales', 'axes', 'marks']
        for key in keys: 
            self.testvin.build_vega(key)
            dict = self.default_vega.copy()
            dict.pop(key)
            assert self.testvin.vega == dict
            
    def test_updatevis(self):
        '''Test updating the visualization'''
        
        self.testvin.update_vis(height=300, width=1000, name='Foo', 
                                padding={'bottom': 40,
                                         'left': 40, 
                                         'right': 40,
                                         'top': 40})
        assert self.testvin.name == 'Foo'
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
        self.testvin.update_component('w', 'axes', 0, 'scale')
        assert self.testvin.axes[0]["scale"] == 'w'
        
        self.testvin.build_component(scales=[{"domain": {"data": "table",
                                                        "field": "data.x"},
                                             "name":"x", "type":"ordinal", 
                                             "range":"width"}], append=False)
        self.testvin.update_component('data.y', 'scales', 0, 'domain', 'field')
        assert self.testvin.vega['scales'][0]['domain']['field'] == 'data.y'
        
    def test_tabular_data(self):
        '''Test tabular data input'''
        
        self.testvin.tabular_data([10, 20, 30, 40, 50])
        assert self.testvin.data[0]['values'][0:2] == [{'x': 1, 'y': 10}, 
                                                       {'x': 2, 'y': 20}]
        self.testvin.tabular_data([60, 70, 80, 90, 100], append=True)
        assert self.testvin.data[0]['values'][-2:] == [{'x': 1, 'y': 90}, 
                                                       {'x': 2, 'y': 100}]        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            

        