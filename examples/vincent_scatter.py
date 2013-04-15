# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Scatter()
'''

import vincent
import random

vis = vincent.Scatter()
vis.tabular_data([random.randint(10, 100) for x in range(0, 201, 1)])

#Generate both the Vega JSON and a data JSON. 
path = r'/vega.json'
vis.to_json(path, split_data=True, html=True)

#Make the visualization wider, and add a hover to the points

vis.update_vis(width=800)

vis + ({'fill': {'value': '#2a3140'}, 'size': {'value': '100'}}, 
       'marks', 0, 'properties', 'update')

vis + ({'fill': {'value': '#a63737'}, 'size': {'value': '300'}}, 
       'marks', 0, 'properties', 'hover')
       
vis.to_json(path, split_data=True, html=True)