# -*- coding: utf-8 -*-
"""

Vincent Map Examples

"""

#Build a map from scratch

from vincent import *

vis = Visualization(width=960, height=500)
vis.data['countries'] = Data(
    name='countries',
    url='world-countries.topo.json',
    format={'type': 'topojson', 'feature': 'world-countries'}
    )

geo_transform = Transform(
                type='geopath', value="data", projection='winkel3', scale=200,
                translate=[480, 250]
                )

geo_from = MarkRef(data='countries', transform=[geo_transform])

enter_props = PropertySet(
    stroke=ValueRef(value='#000000'),
    path=ValueRef(field='path')
    )

update_props = PropertySet(fill=ValueRef(value='steelblue'))

mark_props = MarkProperties(enter=enter_props, update=update_props)

vis.marks.append(
    Mark(type='path', from_=geo_from, properties=mark_props)
    )

vis.to_json('vega.json')

#Convenience Method

geo_data = [{'name': 'countries',
             'url': 'world-countries.topo.json',
             'feature': 'world-countries'}]

vis = Map(geo_data=geo_data, scale=200)
vis.to_json('vega.json')

#States & Counties

geo_data = [{'name': 'counties',
             'url': 'us-counties.topo.json',
             'feature': 'us-counties'},
            {'name': 'states',
             'url': 'us-states.topo.json',
             'feature': 'us-states'}
             ]

vis = Map(geo_data=geo_data, scale=1000, projection='albersUsa')
del vis.marks[1].properties.update
vis.marks[0].properties.update.fill.value = '#084081'
vis.marks[1].properties.enter.stroke.value = '#fff'
vis.marks[0].properties.enter.stroke.value = '#7bccc4'
vis.to_json('vega.json')