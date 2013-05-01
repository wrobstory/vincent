import pandas as pd
import Quandl
import vincent

abbvs = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 
         'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 
         'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 
         'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 
         'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
data = {'Unemployment': {'Code': 'UR', 'data': []}, 
        'House Price Index': {'Code': 'STHPI', 'data': []}}
date = '2012-10-01'
df_list = []
for key, value in data.iteritems():
    for state in abbvs:
        quandl_code = 'FRED/{0}{1}'.format(state, value['Code'])
        df = Quandl.get(quandl_code, 
                        authtoken='*****',
                        startdate=date,
                        enddate=date)
        df = df.rename(columns={'Value': state}, 
                       index={pd.to_datetime(date): key})              
        value['data'].append(df.T)
        
    stacked = pd.concat(data[key]['data'])
    data[key]['data'] = stacked
    df_list.append(stacked)
    
all_data = pd.concat(df_list, axis=1)

us_states = r'data/us-states.json'
vis = vincent.Map(width=1000, height=800)
vis.tabular_data(all_data, columns=['Unemployment'])
vis.geo_data(projection='albersUsa', scale=1000, bind_data='data.id', states=us_states)
vis += (['#c9cedb', '#0b0d11'], 'scales', 0, 'range')
vis.to_json(path, html=True)
    

