# -*- coding: utf-8 -*-
"""

Vincent Pie Chart Example

"""

#Build a Pie Chart from scratch


from vincent import *

farm_1 = {'apples': 10, 'berries': 32, 'squash': 21, 'melons': 13, 'corn': 18}

vis = Visualization(width=960, height=500)
outer_radius = min(vis.width, vis.height)/2
inner_radius = 0
data = Data.from_iter(farm_1)
vis.data['table'] = data

vis.scales["color"] = Scale(
    name="color", type="ordinal", range="category10",
    domain=DataRef(data="table", field="data.idx"))

transform = MarkRef(
    data="table", transform=[Transform(type="pie", value="data.val")])

enter_props = PropertySet(
    x=ValueRef(group="width", mult=0.5),
    y=ValueRef(group="height", mult=0.5),
    start_angle=ValueRef(field="startAngle"),
    end_angle=ValueRef(field="endAngle"),
    inner_radius=ValueRef(value=inner_radius),
    outer_radius=ValueRef(value=outer_radius),
    stroke=ValueRef(value="white"),
    fill=ValueRef(scale="color", field="data.idx"))

mark = Mark(type="arc", from_=transform,
            properties=MarkProperties(enter=enter_props))

vis.marks.append(mark)
vis.legend('Farm 1 Fruit')
vis.to_json('vega.json')

#Convenience method
vis = vincent.Pie(farm_1)
vis.legend('Farm 1 Fruit')
vis.to_json('vega.json')

#Donut chart, different colors
vis = vincent.Pie(farm_1, inner_radius=200)
vis.colors(brew="Set2")
vis.legend('Farm 1 Fruit')
vis.to_json('vega.json')