# -*- coding: utf-8 -*-
"""

Vincent Area Examples

"""

#Build an Area Chart from scratch

from vincent import *
import pandas.io.data as web
all_data = {}
for ticker in ['AAPL', 'GOOG', 'IBM', 'YHOO', 'MSFT']:
    all_data[ticker] = web.get_data_yahoo(ticker, '1/1/2010', '1/1/2013')
price = pd.DataFrame({tic: data['Adj Close']
                      for tic, data in all_data.items()})

vis = Visualization(width=500, height=300)
vis.padding = {'top': 10, 'left': 50, 'bottom': 50, 'right': 100}
vis.scales['x'] = Scale(name='x', type='time', range='width',
                        domain=DataRef(data='table', field="data.idx"))
vis.scales['y'] = Scale(name='y', range='height', type='linear', nice=True,
                        domain=DataRef(data='table', field="data.val"))
vis.scales['color'] = Scale(name='color', type='ordinal',
                            domain=DataRef(data='table', field='data.col'),
                            range='category20')
vis.axes.extend([Axis(type='x', scale='x'),
                 Axis(type='y', scale='y')])

#Marks
transform = MarkRef(data='table',
                    transform=[Transform(type='facet', keys=['data.col'])])
enter_props = PropertySet(x=ValueRef(scale='x', field="data.idx"),
                          y=ValueRef(scale='y', field="data.val"),
                          interpolate=ValueRef(value='monotone'),
                          y2=ValueRef(value=0, scale='y'),
                          fill=ValueRef(scale='color', field='data.col'))
mark = Mark(type='group', from_=transform,
            marks=[Mark(type='area',
            properties=MarkProperties(enter=enter_props))])
vis.marks.append(mark)

data = Data.from_pandas(price['AAPL'])

#Using a Vincent Keyed List here
vis.data['table'] = data
vis.axis_titles(x='Date', y='AAPL Price')
vis.to_json('vega.json')

#Convenience method

vis = Area(price['AAPL'])
vis.axis_titles(x='Date', y='AAPL Price')
vis.to_json('vega.json')
