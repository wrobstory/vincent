"""
Vincent IPython notebook
-------

A module for integrating vincent with the IPython notebook. Huge thanks to
https://github.com/aflaxman for putting this together. IPython might be seeing
significant changes with JS handling in the near future- until then, this
module will allow for embedding on a local server (but not in nbviewer)

"""

import random
from IPython.core.display import display, HTML, Javascript


def init_d3():
    '''Display html that loads d3 javascript library.'''

    display(HTML('''<script src="http://d3js.org/d3.v3.min.js"></script>'''))


def init_vg():
    '''Display html that loads vega javascript library.'''

    display(HTML('<script src="http://trifacta.github.com/vega/vega.js">'
                 '</script>'))


def display_vega(vis):
    '''Display graphic inline in IPython notebook'''

    # HACK: use a randomly chosen unique div id
    id = random.randint(0, 2**16)

    a = HTML('''<div id="vis%d"></div>''' % id)
    b = Javascript('''vg.parse.spec(%s, function(chart)
                        { chart({el:"#vis%d"}).update(); });''' %
                   (vis.to_json(), id))
    display(a, b)
