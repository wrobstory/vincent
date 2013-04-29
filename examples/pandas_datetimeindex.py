# -*- coding: utf-8 -*-
'''
A timeseries example for Vincent
'''

import vincent
import pandas as pd
import random

path = 'vega.json'

#Daily data
dates = pd.date_range('4/1/2013 00:00:00', periods=1441, freq='T')
data = [random.randint(20, 100) for x in range(len(dates))]
series = pd.Series(data, index=dates)
vis = vincent.Line()
vis.tabular_data(series, axis_time='day')
vis + ({'value': 'basis'}, 'marks', 0, 'properties', 'enter', 'interpolate')
vis.update_vis(width=800)
vis.axis_label(x_label='Time', y_label='Data')
vis.to_json(path)

#Resample to hourly, which can take a lambda function in addition to the 
#standard mean, max, min, etc. 
half_day = series['4/1/2013 00:00:00':'4/1/2013 12:00:00']
hourly = half_day.resample('H', how=lambda x: x.mean() + random.randint(-30, 40))
area = vincent.Area()
area.tabular_data(hourly, axis_time='hour')
area + ({'value': 'basis'}, 'marks', 0, 'properties', 'enter', 'interpolate')
area.update_vis(width=800)
area.axis_label(x_label='Time (Hourly)', y_label='Data')
area.to_json(path)

#Subset of minute data
half_hour = series['4/1/2013 00:00:00':'4/1/2013 00:30:00']
vis.tabular_data(half_hour, axis_time='minute')
vis.axis_label(x_label='Time (Minutes)', title='Data vs. Time')
vis.to_json(path)




