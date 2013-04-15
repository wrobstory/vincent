# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Line()
'''

import vincent
import random

vis = vincent.Line()
vis.tabular_data([random.randint(10, 100) for x in range(0, 101, 1)])

#Generate both the Vega JSON and a data JSON. 
path = r'/vega.json'
vis.to_json(path, split_data=True, html=True)

#Make the visualization bigger, lines thicker, and do some point interpolation

vis.update_vis(height=400, width=800)

vis + (4, 'marks', 0, 'properties','enter', 'strokeWidth', 'value')
vis + ({'value': 'basis'}, 'marks', 0, 'properties', 'enter', 'interpolate')
       
vis.to_json(path, split_data=True, html=True)
