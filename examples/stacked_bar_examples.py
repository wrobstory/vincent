# -*- coding: utf-8 -*-
"""

Vincent Stacked Bar Examples

"""

#Build a Stacked Bar Chart from scratch

import pandas as pd
from vincent import *

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

data = Data.from_pandas(df)
vis.data['table'] = data
facets = Transform(type='facet', groupby=['idx'])
stats = Transform(type='aggregate', value='val')
stat_dat = Data(name='stats', source='table', transform=[facets, stats])
vis.data['stats'] = stat_dat


vis.scales['x'] = Scale(name='x', type='ordinal', range='width',
                        domain=DataRef(data='table', field="idx"))
vis.scales['y'] = Scale(name='y', range='height', type='linear', nice=True,
                        domain=DataRef(data='stats', field="sum"))
vis.scales['color'] = Scale(name='color', type='ordinal',
                            domain=DataRef(data='table', field='col'),
                            range='category20')
vis.axes.extend([Axis(type='x', scale='x'),
                 Axis(type='y', scale='y')])


facet = Transform(type='facet', groupby=['col'])
stack = Transform(type='stack', point='idx', height='val')
transform = MarkRef(data='table',transform=[facet, stack])
enter_props = PropertySet(x=ValueRef(scale='x', field="idx"),
                          y=ValueRef(scale='y', field="y"),
                          width=ValueRef(scale='x', band=True, offset=-1),
                          y2=ValueRef(field='y2', scale='y'),
                          fill=ValueRef(scale='color', field='col'))
mark = Mark(type='group', from_=transform,
            marks=[Mark(type='rect',
            properties=MarkProperties(enter=enter_props))])
vis.marks.append(mark)

vis.axis_titles(x='Farms', y='Total Produce')
vis.legend(title='Produce Type')
vis.to_json('vega.json')

#Convenience method
vis = StackedBar(df)
vis.axis_titles(x='Farms', y='Total Produce')
vis.legend(title='Produce Type')
vis.scales['x'].padding = 0.2
vis.colors(brew='Set2')
vis.to_json('vega.json')
