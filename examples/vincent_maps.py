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
world_countries = r'../world-countries.json'
path = r'../vega.json'

#Simple map of the US
states = vincent.Map(width=1000, height=800)
states.geo_data(projection='albersUsa', scale=1000, states=us_states)
states.to_json(path)

#Simple map of the world
world = vincent.Map(width=1200, height=1000)
world.geo_data(projection='winkel3', scale=200, world=world_countries)
world.to_json(path)

#Map with both US States and Counties

#Grab county names so that we can add random data to them
with open(us_counties, 'r') as f:
    get_names = json.load(f)
    
county_names = [x['properties']['name'] for x in get_names['features']]
random_data = [random.randint(10, 100) for y in range(len(county_names))]
data_dict = {key: value for key, value in zip(county_names, random_data)}

vis = vincent.Map(width=1000, height=800)
#Add our state data first
vis.geo_data(projection='albersUsa', scale=1000, states=us_states)

#Add our data that we want to visualize
vis.tabular_data(data_dict)

#The projection and scale will stay fixed unless you 'reset' the map
#Bind the tabular data to the counties, passing dot notation for the geoJSON
#parameter you are binding to
vis.geo_data(bind_data='data.properties.name', counties=us_counties)
vis.to_json(path)

#Change map back to just states
vis.geo_data(projection='albersUsa', scale=1000, reset=True, states=us_states)