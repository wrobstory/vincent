# -*- coding: utf-8 -*-
"""

Vincent Grouped Bar Examples

"""

#Build a Grouped Bar Chart from scratch

import pandas as pd
from vincent import *
from vincent.core import KeyedList

farm_1 = {'apples': 10, 'berries': 32, 'squash': 21, 'melons': 13, 'corn': 18}
farm_2 = {'apples': 15, 'berries': 40, 'squash': 17, 'melons': 10, 'corn': 22}
farm_3 = {'apples': 6, 'berries': 24, 'squash': 22, 'melons': 16, 'corn': 30}
farm_4 = {'apples': 12, 'berries': 30, 'squash': 15, 'melons': 9, 'corn': 15}
farm_5 = {'apples': 20, 'berries': 35, 'squash': 19, 'melons': 17, 'corn': 19}
farm_6 = {'apples': 3, 'berries': 28, 'squash': 21, 'melons': 11, 'corn': 23}

data = [farm_1, farm_2, farm_3, farm_4, farm_5, farm_6]
index = ['Farm 1', 'Farm 2', 'Farm 3', 'Farm 4', 'Farm 5', 'Farm 6']

df = pd.DataFrame(data, index=index)

vis = Visualization(width=500, height=300)
vis.padding = {'top': 10, 'left': 50, 'bottom': 50, 'right': 100}

data = Data.from_pandas(df, grouped=True)
vis.data['table'] = data

vis.scales['x'] = Scale(name='x', type='ordinal', range='width',
                        domain=DataRef(data='table', field="data.idx"),
                        padding=0.2)
vis.scales['y'] = Scale(name='y', range='height', nice=True,
                        domain=DataRef(data='table', field="data.val"))
vis.scales['color'] = Scale(name='color', type='ordinal',
                            domain=DataRef(data='table', field='data.col'),
                            range='category20')
vis.axes.extend([Axis(type='x', scale='x'),
                 Axis(type='y', scale='y')])

enter_props = PropertySet(x=ValueRef(scale='pos', field="data.group"),
                          y=ValueRef(scale='y', field="data.val"),
                          width=ValueRef(scale='pos', band=True, offset=-1),
                          y2=ValueRef(value=0, scale='y'),
                          fill=ValueRef(scale='color', field='data.col'))
mark = Mark(type='group', from_=transform,
            marks=[Mark(type='rect',
            properties=MarkProperties(enter=enter_props))])
vis.marks.append(mark)

#Mark group properties
facet = Transform(type='facet', keys=['data.idx'])
transform = MarkRef(data='table',transform=[facet])
group_props = PropertySet(x=ValueRef(scale='x', field="key"),
                                     width=ValueRef(scale='x', band=True))
vis.marks[0].properties = MarkProperties(enter=group_props)
vis.marks[0].scales = KeyedList()
vis.marks[0].scales['pos'] = Scale(name='pos', type='ordinal',
                                   range='width',
                                   domain=DataRef(field='data.group'))

vis.axis_titles(x='Farms', y='Total Produce')
vis.legend(title='Produce Type')
vis.to_json('vega.json')

#Convenience method
vis = GroupedBar(df)
vis.axis_titles(x='Farms', y='Total Produce')
vis.width = 700
vis.legend(title='Produce Type')
vis.colors(brew='Pastel1')
vis.to_json('vega.json')
