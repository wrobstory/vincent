# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Bar()
'''

import vincent

vis = vincent.Bar()
vis.tabular_data((('A', 28), ('B', 55), ('C', 43), ('D', 91), ('E', 81), 
                  ('F', 53), ('G', 19), ('H', 87), ('I', 52)))

#Generate both the Vega JSON and a data JSON. 
path = r'vega.json'
vis.to_json(path, split_data=True, html=True)
