# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Bar(), then plots 
the output to the ipython notebook
'''

import vincent
vis = vincent.Bar()
vis.tabular_data((('A', 28), ('B', 55), ('C', 43), ('D', 91), ('E', 81), 
                  ('F', 53), ('G', 19), ('H', 87), ('I', 52)))
vincent.ipynb_init_d3()
vincent.ipynb_init_vg()
vincent.ipynb_display(vis)
