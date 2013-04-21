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
line.tabular_data(price, columns=['AAPL'], axis_time='month')
line.to_json(path)

#Play with the axes labels a bit
line + ({'labels': {'angle': {'value': 25}}}, 'axes', 0, 'properties')
line + ({'value': 22}, 'axes', 0, 'properties', 'labels', 'dx')
line.update_vis(width=800, height=300)
line.axis_label(y_label='AAPL Price', title='AAPL Stock Price 1/1/2010-1/1/2013')
line.update_vis(padding={'bottom': 50, 'left': 30, 'right': 50, 'top': 10})
line.to_json(path)