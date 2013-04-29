# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from scratch
'''

import vincent

vis = vincent.Vega()
vis.tabular_data((('A', 28), ('B', 55), ('C', 43), ('D', 91), ('E', 81), 
                  ('F', 53), ('G', 19), ('H', 87), ('I', 52)))
vis.build_component(axes=[{"type":"x", "scale":"x"},{"type":"y", "scale":"y"}],
                    scales=[{"name":"x", "type":"ordinal", "range":"width", 
                             "domain":{"data":"table", "field":"data.x"}},
                            {"name":"y", "range":"height", "nice":True, 
                             "domain":{"data":"table", "field":"data.y"}}],
                    marks=[{"type": "rect", "from": {"data": "table"},
                            "properties": {
                                     "enter": {
                                     "x": {"scale": "x", "field": "data.x"},
                                     "width": {"scale": "x", "band": True,
                                               "offset": -1},
                                     "y": {"scale": "y", "field": "data.y"},
                                     "y2": {"scale": "y", "value": 0}
                                     },
                                     "update": {"fill": {"value": "#2a3140"}},
                                     "hover": {"fill": {"value": "#a63737"}}
                                      }}])

#Generate both the Vega JSON and a data JSON. 
path = r'vega.json'
vis.to_json(path, split_data=True, html=True)

#Fire up a server on the path you saved the JSONs to: 
import os
import SimpleHTTPServer
import SocketServer
import webbrowser
os.chdir(os.path.dirname(path))
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(("", 8000), Handler)
httpd.serve_forever()

#Go to http://localhost:8000/vega_template.html in your browser