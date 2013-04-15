# -*- coding: utf-8 -*-
'''
Builds a Vega grammar specification from vincent.Bar()
'''

import vincent

vis = vincent.Bar()
vis.tabular_data((('A', 28), ('B', 55), ('C', 43), ('D', 91), ('E', 81), 
                  ('F', 53), ('G', 19), ('H', 87), ('I', 52)))

#Generate both the Vega JSON and a data JSON. 
path = r'/vega.json'
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