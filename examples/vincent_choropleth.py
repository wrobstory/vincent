import json
import pandas as pd
import vincent

county_data = r'data/us_county_data.csv'
county_geo = r'data/us-counties.json'
state_geo = r'data/us-states.json'
state_unemployment = r'data/US_Unemployment_Oct2012.csv'

#We want to map the county codes we have in our geometry to those in the
#county_data file, which contains additional rows we don't need
with open(county_geo, 'r') as f:
    get_id = json.load(f)
    
county_codes = [x['id'] for x in get_id['features']]
county_df = pd.DataFrame({'FIPS_Code': county_codes}, dtype=str)

#Read into Dataframe, cast to string for consistency
df = pd.read_csv(county_data, na_values=[' '])
df['FIPS_Code'] = df['FIPS_Code'].astype(str)

#Perform an inner join, pad NA's with data from nearest county
merged = pd.merge(df, county_df, on='FIPS_Code', how='inner')
merged = merged.fillna(method='pad')

path = 'vega.json'

#Map different data sets
vis = vincent.Map(width=1000, height=800)
vis.tabular_data(merged, columns=['FIPS_Code', 'Unemployment_rate_2011']) 
vis.geo_data(projection='albersUsa', scale=1000, bind_data='data.id', counties=county_geo)
vis += (["#f5f5f5","#000045"], 'scales', 0, 'range')
vis.to_json(path, html=True)

vis.tabular_data(merged, columns=['FIPS_Code', 'Median_Household_Income_2011'])
vis.to_json(path)

vis.tabular_data(merged, columns=['FIPS_Code', 'Civilian_labor_force_2011']) 
vis.to_json(path, html=True)

#Swap county data for state data, reset map
state_data = pd.read_csv(state_unemployment)
vis.tabular_data(state_data, columns=['State', 'Unemployment'])
vis.geo_data(bind_data='data.id', reset=True, states=state_geo)
vis.update_map(scale=1000, projection='albersUsa')
vis += (['#c9cedb', '#0b0d11'], 'scales', 0, 'range')
vis.to_json(path, html=True)
