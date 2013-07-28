# -*- coding: utf-8 -*-
"""

Vincent Bar Chart Example

"""

#Build a Bar Chart from scratch

from vincent import *
import pandas as pd

farm_1 = {'apples': 10, 'berries': 32, 'squash': 21, 'melons': 13, 'corn': 18}
farm_2 = {'apples': 15, 'berries': 43, 'squash': 17, 'melons': 10, 'corn': 22}
farm_3 = {'apples': 6, 'berries': 24, 'squash': 22, 'melons': 16, 'corn': 30}
farm_4 = {'apples': 12, 'berries': 30, 'squash': 15, 'melons': 9, 'corn': 15}

data = [farm_1, farm_2, farm_3, farm_4]
index = ['Farm 1', 'Farm 2', 'Farm 3', 'Farm 4']

df = pd.DataFrame(data, index=index)

vis = Visualization(width=500, height=300)
vis.scales['x'] = Scale(name='x', type='ordinal', range='width',
                        domain=DataRef(data='table', field="data.idx"))
vis.scales['y'] = Scale(name='y', range='height', nice=True,
                        domain=DataRef(data='table', field="data.val"))
vis.axes.extend([Axis(type='x', scale='x'),
                 Axis(type='y', scale='y')])

#Marks
enter_props = PropertySet(x=ValueRef(scale='x', field="data.idx"),
                          y=ValueRef(scale='y', field="data.val"),
                          width=ValueRef(scale='x', band=True, offset=-1),
                          y2=ValueRef(scale='y', value=0))

update_props = PropertySet(fill=ValueRef(value='steelblue'))

mark = Mark(type='rect', from_=MarkRef(data='table'),
            properties=MarkProperties(enter=enter_props,
                                      update=update_props))
vis.marks.append(mark)

data = Data.from_pandas(df['apples'])

#Using a Vincent KeyedList here
vis.data['table'] = data
vis.axis_titles(x='Farms', y='Data')
vis.to_json('vega.json')

#Convenience methods

vis = Bar(df['apples'])

#Fruit
trans = df.T
vis = Bar(trans['Farm 1'])

#From dict
vis = Bar(farm_1)

#From dict of iterables
vis = Bar({'x': ['apples', 'berries', 'squash', 'melons', 'corn'],
           'y': [10, 32, 21, 13, 18]}, iter_idx='x')

#Finally, a boring bar chart from a list
vis = Bar([10, 20, 30, 15, 35, 10, 20])
