# -*- coding: utf-8 -*-
'''
Plotting some Pandas data with Vincent
'''

import vincent
import pandas as pd

#All of the following import code comes from Wes McKinney's book, Python for Data Analysis

import pandas.io.data as web

all_data = {}

for ticker in ['AAPL', 'GOOG']:
    all_data[ticker] = web.get_data_yahoo(ticker, '1/1/2010', '1/1/2013')
    
price = pd.DataFrame({tic: data['Adj Close']
                      for tic, data in all_data.iteritems()})

#Create line graph, with monthly plotting on the axes                       
line = vincent.Line()
line.tabular_data(price, columns=['AAPL'])
line + ({'labels': {'angle': {'value': 45}}}, 'axes', 0, 'properties')
line + ({'value': 20}, 'axes', 0, 'properties', 'labels', 'dx')
line + ({'value': 5}, 'axes', 0, 'properties', 'labels', 'dy')
line.update_vis(padding={'bottom': 60, 'left': 30, 'right': 30, 'top': 10})
line.update_vis(width=800)
line.to_json(path)
