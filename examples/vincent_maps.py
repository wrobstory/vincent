# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Map()
'''
import vincent
import pandas as pd

us_states = r'../data/us-states.json'
us_counties = r'../data/us-counties.json'
world_countries = r'../data/world-countries.json'
county_data = r'../data/us_county_data.csv'
state_unemployment = r'../data/US_Unemployment_Oct2012.csv'
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

vis = vincent.Map(width=1000, height=800)
#Add our county data first
vis.geo_data(projection='albersUsa', scale=1000, counties=us_counties)
vis + ('2B4ECF', 'marks', 0, 'properties', 'enter', 'stroke', 'value')

#The projection and scale will stay fixed unless you 'reset' the map
vis.geo_data(states=us_states)
vis - ('fill', 'marks', 1, 'properties', 'enter')
vis.to_json(path)

#Swap out data for state data, reset our map
vis.geo_data(projection='albersUsa', scale=1000, reset=True, states=us_states)
vis.to_json(path)