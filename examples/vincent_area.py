# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Area()
'''

import vincent
import random

vis = vincent.Area()
vis.tabular_data([random.randint(10, 100) for x in range(0, 16, 1)])

#Generate both the Vega JSON and a data JSON. 
path = r'/vega.json'
vis.to_json(path, split_data=True, html=True)

#Lets add a data interpolation parameter and resave the JSON
vis + ({'value': 'basis'}, 'marks', 0, 'properties', 'enter', 'interpolate')
vis.to_json(path, split_data=True, html=True)