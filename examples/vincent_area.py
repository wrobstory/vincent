# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Area()
'''

import vincent
import random

vis = vincent.Area()
vis.tabular_data([random.randint(10, 100) for x in range(0, 16, 1)])
vis.axis_label(x_label='X Axis Label', y_label='Y Axis Label', title='Title')

#Generate both the Vega JSON and a data JSON. 
path = r'vega.json'
vis.to_json(path, split_data=True, html=True)

#Lets add a data interpolation parameter and resave the JSON
vis += ({'value': 'monotone'}, 'marks', 0, 'properties', 'enter', 'interpolate')
vis.to_json(path, split_data=True, html=True)