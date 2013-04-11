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
        
        self.test_default = vincent.Vega()
        self.test_inputs = vincent.Vega(name='test', width=800, height=400,
                                        padding={'top': 20, 'left': 40, 
                                                 'bottom': 60, 'right': 10},
                                        viewport=[1000, 500])
                                     
        self.default_vega = {'name': 'Vega', 'width': 400, 'height': 200,
                             'viewport': None, 'axes': [],
                             'padding': {'top': 10, 'left': 30, 
                                         'bottom': 20, 'right': 10}, 
                             'data': [], 'marks': [], 'scales': []}
    
    def test_atts(self):
        '''Test init attributes'''
        
        assert self.test_default.name == 'Vega'
        assert self.test_default.width == 400
        assert self.test_default.height == 200
        assert self.test_default.padding == {'top': 10, 'left': 30, 
                                             'bottom': 20, 'right': 10}
        assert self.test_default.viewport == None
        assert self.test_default.vega == self.default_vega
        
        assert self.test_inputs.name == 'test'
        assert self.test_inputs.width == 800
        assert self.test_inputs.height == 400
        assert self.test_inputs.padding == {'top':20, 'left': 40, 
                                             'bottom': 60, 'right': 10}
        assert self.test_inputs.viewport == [1000, 500]
        
    def test_build(self):
        '''Test vega build'''
        keys = ['name', 'width', 'height', 'padding', 'viewport', 'data', 
                'scales', 'axes', 'marks']
        for key in keys: 
            self.test_default.build_vega(key)
            dict = self.default_vega.copy()
            dict.pop(key)
            assert self.test_default.vega == dict
            

        