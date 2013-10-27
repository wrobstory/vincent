# -*- coding: utf-8 -*-
"""

Vincent Map Examples

"""

#Build a map from scratch

from vincent import *

world_topo = r'world-countries.topo.json'
state_topo = r'us_states.topo.json'
lake_topo = r'lakes_50m.topo.json'
county_geo = r'us_counties.geo.json'
county_topo = r'us_counties.topo.json'
or_topo = r'or_counties.topo.json'

vis = Visualization(width=960, height=500)
vis.data['countries'] = Data(
    name='countries',
    url=world_topo,
    format={'type': 'topojson', 'feature': 'world-countries'}
    )

geo_transform = Transform(
                type='geopath', value="data", projection='winkel3', scale=200,
                translate=[480, 250]
                )

geo_from = MarkRef(data='countries', transform=[geo_transform])

enter_props = PropertySet(
    stroke=ValueRef(value='#000000'),
    path=ValueRef(field='path')
    )

update_props = PropertySet(fill=ValueRef(value='steelblue'))

mark_props = MarkProperties(enter=enter_props, update=update_props)

vis.marks.append(
    Mark(type='path', from_=geo_from, properties=mark_props)
    )

vis.to_json('vega.json')

#Convenience Method

geo_data = [{'name': 'countries',
             'url': world_topo,
             'feature': 'world-countries'}]

vis = Map(geo_data=geo_data, scale=200)
vis.to_json('vega.json')

#States & Counties

geo_data = [{'name': 'counties',
             'url': county_topo,
             'feature': 'us_counties.geo'},
            {'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'}
             ]

vis = Map(geo_data=geo_data, scale=1000, projection='albersUsa')
del vis.marks[1].properties.update
vis.marks[0].properties.update.fill.value = '#084081'
vis.marks[1].properties.enter.stroke.value = '#fff'
vis.marks[0].properties.enter.stroke.value = '#7bccc4'
vis.to_json('vega.json')

#Choropleth
import json
import pandas as pd
#Map the county codes we have in our geometry to those in the
#county_data file, which contains additional rows we don't need
with open('us_counties.topo.json', 'r') as f:
    get_id = json.load(f)

#A little FIPS code munging
new_geoms = []
for geom in get_id['objects']['us_counties.geo']['geometries']:
    geom['properties']['FIPS'] = int(geom['properties']['FIPS'])
    new_geoms.append(geom)

get_id['objects']['us_counties.geo']['geometries'] = new_geoms

with open('us_counties.topo.json', 'w') as f:
    json.dump(get_id, f)

#Grab the FIPS codes and load them into a dataframe
geometries = get_id['objects']['us_counties.geo']['geometries']
county_codes = [x['properties']['FIPS'] for x in geometries]
county_df = pd.DataFrame({'FIPS': county_codes}, dtype=str)
county_df = county_df.astype(int)

#Read into Dataframe, cast to int for consistency
df = pd.read_csv('data/us_county_data.csv', na_values=[' '])
df['FIPS'] = df['FIPS'].astype(int)

#Perform an inner join, pad NA's with data from nearest county
merged = pd.merge(df, county_df, on='FIPS', how='inner')
merged = merged.fillna(method='pad')

geo_data = [{'name': 'counties',
             'url': county_topo,
             'feature': 'us_counties.geo'}]

vis = Map(data=merged, geo_data=geo_data, scale=1100, projection='albersUsa',
          data_bind='Employed_2011', data_key='FIPS',
          map_key={'counties': 'properties.FIPS'})
vis.marks[0].properties.enter.stroke_opacity = ValueRef(value=0.5)
#Change our domain for an even inteager
vis.scales['color'].domain = [0, 189000]
vis.legend(title='Number Employed 2011')
vis.to_json('vega.json')

#Lets look at different stats
vis.rebind(column='Civilian_labor_force_2011', brew='BuPu')
vis.to_json('vega.json')

vis.rebind(column='Unemployed_2011', brew='PuBu')
vis.to_json('vega.json')

vis.rebind(column='Unemployment_rate_2011', brew='YlGnBu')
vis.to_json('vega.json')

vis.rebind(column='Median_Household_Income_2011', brew='RdPu')
vis.to_json('vega.json')

#Mapping US State Level Data

state_data = pd.read_csv('data/US_Unemployment_Oct2012.csv')
geo_data = [{'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'}]
vis = Map(data=state_data, geo_data=geo_data, scale=1000,
          projection='albersUsa', data_bind='Unemployment', data_key='NAME',
          map_key={'states': 'properties.NAME'})
vis.legend(title='Unemployment (%)')
vis.to_json('vega.json')

#Iterating State Level Data
yoy = pd.read_table('data/State_Unemp_YoY.txt', delim_whitespace=True)
#Standardize State names to match TopoJSON for keying
names = []
for row in yoy.iterrows():
    pieces = row[1]['NAME'].split('_')
    together = ' '.join(pieces)
    names.append(together.title())
yoy['NAME'] = names
geo_data = [{'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'}]
vis = Map(data=yoy, geo_data=geo_data, scale=1000,
          projection='albersUsa', data_bind='AUG_2012', data_key='NAME',
          map_key={'states': 'properties.NAME'}, brew='YlGnBu')
#Custom threshold scale
vis.scales[0].type='threshold'
vis.scales[0].domain = [0, 2, 4, 6, 8, 10, 12]
vis.legend(title='Unemployment (%)')
vis.to_json('vega.json')

#Rebind and set our scale again
vis.rebind(column='AUG_2013', brew='YlGnBu')
vis.scales[0].type='threshold'
vis.scales[0].domain = [0, 2, 4, 6, 8, 10, 12]
vis.to_json('vega.json')

vis.rebind(column='CHANGE', brew='YlGnBu')
vis.scales[0].type='threshold'
vis.scales[0].domain = [-1.5, -1.3, -1.1, 0, 0.1, 0.3, 0.5, 0.8]
vis.legends[0].title = "YoY Change in Unemployment (%)"
vis.to_json('vega.json')


#Oregon County-level population data
or_data = pd.read_table('data/OR_County_Data.txt', delim_whitespace=True)
or_data['July_2012_Pop']= or_data['July_2012_Pop'].astype(int)
#Standardize keys
with open('or_counties.topo.json', 'r') as f:
    counties = json.load(f)

def split_county(name):
    parts = name.split(' ')
    parts.pop(-1)
    return ''.join(parts).upper()

#A little FIPS code munging
new_geoms = []
for geom in counties['objects']['or_counties.geo']['geometries']:
    geom['properties']['COUNTY'] = split_county(geom['properties']['COUNTY'])
    new_geoms.append(geom)

counties['objects']['or_counties.geo']['geometries'] = new_geoms

with open('or_counties.topo.json', 'w') as f:
    json.dump(counties, f)

geo_data = [{'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'},
            {'name': 'or_counties',
             'url': or_topo,
             'feature': 'or_counties.geo'}]

vis = Map(data=or_data, geo_data=geo_data, scale=3700,
          translate=[1480, 830],
          projection='albersUsa', data_bind='July_2012_Pop', data_key='NAME',
          map_key={'or_counties': 'properties.COUNTY'})
vis.marks[0].properties.update.fill.value = '#c2c2c2'
vis.to_json('vega.json')

