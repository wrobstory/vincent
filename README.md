#Vincent
![Vincent](http://farm9.staticflickr.com/8521/8644902478_0d1513db92_o.jpg)
###A Python to Vega translator

The folks at Trifacta are making it easy to visualize data with D3. Lets make it easy with Python too. 

Concept
-------
Vincent takes Python data structures (tuples, lists, dicts, and Pandas DataFrames) and translates them into [Vega](https://github.com/trifacta/vega) visualization grammar. It allows for quick iteration of visualization designs via simple addition and subtraction of grammar elements, and outputs the final visualization to JSON.

Getting Started
---------------

Lets build the Vega [bar chart example](https://github.com/trifacta/vega/wiki/Tutorial) with Vincent manually, then show some shortcuts to help get there a little faster, as well as methods for manipulating the components. First, create a Vincent object, which will initialize with some default parameters for the visualization: 
```python
>>>import vincent
>>>vis = vincent.Vega()
```
Now add some data. We could pass a dict, but nested tuples will keep our data sorted properly: 
```python
>>>vis.tabular_data((('A', 28), ('B', 55), ('C', 43), ('D', 91), ('E', 81), ('F', 53),
                     ('G', 19), ('H', 87), ('I', 52)))
```
Pass components to the visualization grammer as keyword arguments (skipping the 'marks' component here for brevity): 
```python
>>>vis.build_component(axes=[{"type":"x", "scale":"x"},{"type":"y", "scale":"y"}],
                       scales=[{"name":"x", "type":"ordinal", "range":"width", 
                                "domain":{"data":"table", "field":"data.x"}},
                               {"name":"y", "range":"height", "nice":True, 
                                "domain":{"data":"table", "field":"data.y"}}])
```
One option is to output to JSON:
```python
>>>vis.to_json(path)
```
Then copy/paste the JSON output to [Vega's online editor](http://trifacta.github.io/vega/editor/), where you should see a replica of the example. 

The other option is to output the Vega grammar and data into separate JSONs, as well as a simple [HTML scaffold](https://github.com/trifacta/vega/wiki/Runtime), then fire up a simple Python server locally: 

```python
>>>vis.to_json(path, split_data=True, html=True)
```
```
$python -m SimpleHTTPServer 8000
```

Point your browser at http://localhost:8000/vega_template.html to see your visualization.

Creating visualizations manually is a little tedious. The vincent.Vega() object can be subclassed to pre-define components and parameters. Lets take a shortcut and use the Bar class:  
```python
>>>import random
>>>vis = vincent.Bar()
>>>vis.tabular_data([random.randint(10, 100) for x in range(0, 21, 1)])
>>>vis.to_json(path)
```
![Bar](http://farm9.staticflickr.com/8532/8645065132_3f96e1be49.jpg)

Vincent also allows you to add and subtract components at varying levels of nesting depth in order to change the visualization. Vincent syntax for modifying component pieces on the fly is:
> Addition: ( **New Value**, **Component**, **Component index**, **Keywords into nested structure** )

> Removal: ( **Old key**, **Component**, **Component index**, **Keywords into nested structure** ) 

For example, if we wanted to change the bar plot to an area plot: 
```python
>>>vis - ('width', 'marks', 0, 'properties', 'enter') 
>>>vis + ('area', 'marks', 0, 'type')
>>>vis + ({'value': 'basis'}, 'marks', 0, 'properties', 'enter', 'interpolate')
>>>vis + ('linear', 'scales', 0, 'type')
>>>vis.to_json(path)
```
![Area](http://farm9.staticflickr.com/8540/8645065128_d2cf65bdf9_o.jpg)
 
