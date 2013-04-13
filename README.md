#Vincent
![Vincent](http://farm9.staticflickr.com/8521/8644902478_0d1513db92_o.jpg)
###A Python to Vega translator

The folks at Trifeca are making it easy to visualize data with D3. Lets make it easy with Python too. 

Concept
-------
Vincent takes Python data structures (lists, dicts, and Pandas DataFrames) and translates them into [Vega](https://github.com/trifacta/vega) visualization grammer. It allows for quick iteration of visualization designs via simple addition and subtraction of grammer elements, and outputs the final visualization to JSON.

Getting Started
---------------

Lets build the Vega [bar chart example](https://github.com/trifacta/vega/wiki/Tutorial) with Vincent manually, then show some shortcuts to help get there a little faster and methods for manipulating the components. First, create a Vincent object, which will initialize with some default parameters for the visualization: 
```python
>>>import vincent
>>>vis = vincent.Vega()
```
Now add some data. We could pass a dict, but nested tuples will keep our data sorted properly: 
```python
>>>vis.tabular_data((('A', 28), ('B', 55), ('C', 43), ('D', 91), ('E', 81), ('F', 53),
                     ('G', 19), ('H', 87), ('I', 52)))
```
Pass components to the visualization grammer as keyword arguments (skipping 'marks' component for brevity): 
```python
>>>vis.build_component(axes=[{"type":"x", "scale":"x"},{"type":"y", "scale":"y"}],
                       scales=[{"name":"x", "type":"ordinal", "range":"width", 
                                "domain":{"data":"table", "field":"data.x"}},
                               {"name":"y", "range":"height", "nice":True, 
                                "domain":{"data":"table", "field":"data.y"}}])
```
Output to JSON:
```python
>>>vis.to_json(path)
```
Then copy/paste the JSON output to [Vega's online editor](http://trifacta.github.io/vega/editor/) and you should see a replica of the example. 

Creating visualizations manually is a little tedious. The vincent.Vega() object can be subclassed to pre-define components and parameters. Lets take a shortcut and use the Bar class this time:  
```python
>>>import random
>>>vis = vincent.Bar()
>>>vis.tabular_data([random.randint(10, 100) for x in range(0, 21, 1)])
>>>vis.to_json(path)
```
Vincent allows you to add and subtract components at varying levels of depth in order to change the visualization. For example, if we wanted to change the bar plot to an area plot: 
```python
>>>vis.marks #Before
[{'from': {'data': 'table'},
  'properties': {'enter': {'width': {'band': True, 'offset': -1, 'scale': 'x'},
    'x': {'field': 'data.x', 'scale': 'x'},
    'y': {'field': 'data.y', 'scale': 'y'},
    'y2': {'scale': 'y', 'value': 0}},
   'hover': {'fill': {'value': '#a63737'}},
   'update': {'fill': {'value': '#2a3140'}}},
  'type': 'rect'}]
>>>vis - ('width', 'marks', 0, 'properties', 'enter')
>>>vis + ('area', 'marks', 0, 'type')
>>>vis + ({'value': 'basis'}, 'marks', 0, 'properties', 'enter', 'interpolate')
>>>vis.marks #After
[{'from': {'data': 'table'},
  'properties': {'enter': {'interpolate': {'value': 'basis'},
    'x': {'field': 'data.x', 'scale': 'x'},
    'y': {'field': 'data.y', 'scale': 'y'},
    'y2': {'scale': 'y', 'value': 0}},
   'hover': {'fill': {'value': '#a63737'}},
   'update': {'fill': {'value': '#2a3140'}}},
  'type': 'area'}]
>>>vis + ('linear', 'scales', 0, 'type')
>>>vis.to_json(path)
```
