# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Map()
'''

import json
import random
import vincent
import pandas as pd

us_states = r'../us-states.json'
us_counties = r'../us-counties.json'
path = r'../vega.json'

with open(us_counties, 'r') as f:
    get_names = json.load(f)
    
county_names = [x['properties']['name'] for x in get_names['features']]
random_data = [random.randint(10, 100) for y in range(len(county_names))]
data_dict = {key: value for key, value in zip(county_names, random_data)}

vis = vincent.Map()
vis.tabular_data(data_dict)
vis.geo_data(projection='albersUsa', scale=1000, 
             bind_data='data.properties.name', counties=us_counties)
vis.to_json(path)