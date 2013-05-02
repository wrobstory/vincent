In order to see the visualization, you will need to start a simple Python HTTP server and serve the html and javascript. In order to do so, run the code in the example file, then the following in the Python REPL (Ctrl-C to shutdown): 

```python
import os
import SimpleHTTPServer
import SocketServer
import webbrowser
try: 
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", 8000), Handler)
    httpd.serve_forever()
except KeyboardInterrupt: 
    httpd.shutdown()
    httpd.server_close()
```

Alternatively, within the terminal/cmd window you can cd to your directory containing the vega.json and vega_template.html files and run the following command: 

```shell
$python -m SimpleHTTPServer 8000
```

Point your webbrowser to http://localhost:8000/vega_template.html to see the visualization. 

