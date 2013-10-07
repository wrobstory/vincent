# -*- coding: utf-8 -*-
"""

Vincent Map Examples

"""

#Build a map from scratch

from vincent import *

vis = Visualization(width=960, height=500)
vis.data['countries'] = Data(
    name='countries',
    url='data/world-countries.topo.json',
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
             'url': 'data/world-countries.topo.json',
             'feature': 'world-countries'}]

vis = Map(geo_data=geo_data, scale=200)
vis.to_json('vega.json')

#States & Counties

geo_data = [{'name': 'counties',
             'url': 'us-counties.topo.json',
             'feature': 'us-counties'},
            {'name': 'states',
             'url': 'us-states.topo.json',
             'feature': 'us-states'}
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
with open('data/us-counties.json', 'r') as f:
    get_id = json.load(f)

#Grab the FIPS codes and load them into a dataframe
county_codes = [x['id'] for x in get_id['features']]
county_df = pd.DataFrame({'FIPS_Code': county_codes}, dtype=str)

#Read into Dataframe, cast to string for consistency
df = pd.read_csv('data/us_county_data.csv', na_values=[' '])
df['FIPS_Code'] = df['FIPS_Code'].astype(str)

#Perform an inner join, pad NA's with data from nearest county
merged = pd.merge(df, county_df, on='FIPS_Code', how='inner')
merged = merged.fillna(method='pad')

geo_data = [{'name': 'counties',
             'url': 'data/us-counties.topo.json',
             'feature': 'us-counties'}]

vis = Map(data=merged, geo_data=geo_data, scale=1000, projection='albersUsa',
          data_bind='Employed_2011', data_key='FIPS_Code',
          map_key={'counties': 'id'})
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