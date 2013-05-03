# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Map(), performs shapefile
conversion with the Ogre web tool: http://ogre.adc4gis.com/

'''

import vincent

#Add Oceans
vis = vincent.Map(width=1200, height=800)
vis.geo_data(scale=200, shapefile=True, ocean=r'data/ne_110m_ocean.zip')
vis += ('#75b9e7', 'marks', 0, 'properties', 'enter', 'fill', 'value')
vis.update_vis(padding={'bottom': 20, 'left': 50, 'right': 20, 'top': 50})

#Add Land
vis.geo_data(shapefile=True, world=r'data/ne_110m_land.zip')
vis += ('1a252f', 'marks', 1, 'properties', 'enter', 'fill', 'value')

#Add Lakes
vis.geo_data(shapefile=True, lakes=r'data/ne_50m_lakes.zip')
vis += ('#3498db', 'marks', 2, 'properties', 'enter', 'fill', 'value')
vis.to_json(path, html=True)

