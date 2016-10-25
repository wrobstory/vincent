# Status

#### 2016-06-18 Update

If you are interested in this library, I would direct you to the Altair project: https://github.com/altair-viz/altair It supports the latest version of vega, is fully-featured, has a great development team, and has been developed with the support of the Vega team at UW. 

There will be no more updates, closed issues, or PR merges for the Vincent project. Thanks so much to everyone who tried it or used it along the way. 

#Vincent

[![Travs-CI status](https://travis-ci.org/wrobstory/vincent.png)](https://travis-ci.org/wrobstory/vincent)

![Vincent](http://farm9.staticflickr.com/8521/8644902478_0d1513db92_o.jpg)

###A Python to Vega translator

The folks at Trifacta are making it easy to build visualizations on top of D3 with Vega. Vincent makes it easy to build Vega with Python.

Concept
-------
The data capabilities of Python. The visualization capabilities of JavaScript.

Vincent takes Python data structures and translates them into [Vega](https://github.com/trifacta/vega) visualization grammar. It allows for quick iteration of visualization designs via getters and setters on grammar elements, and outputs the final visualization to JSON.

Perhaps most importantly, Vincent groks Pandas DataFrames and Series in an intuitive way.

Installation
------------

```$pip install vincent```

Warning: requires Pandas, which isn't a simple pip install if you don't already have Numpy installed. If you want to go all-pip, I recommend ```$pip install numpy``` then ```$pip install pandas```. Or just use [Anaconda](http://www.continuum.io/downloads).

Docs
----

[Here.](https://vincent.readthedocs.org/en/latest/)

Quickstart
---------------

Let's start with some varying [data](https://vincent.readthedocs.org/en/latest/quickstart.html#data), and then show some different ways to visualize them with Vincent.

Starting with a simple bar chart:

```python
import vincent
bar = vincent.Bar(multi_iter1['y1'])
bar.axis_titles(x='Index', y='Value')
bar.to_json('vega.json')
```

![bars](http://farm4.staticflickr.com/3720/9388500423_b3493bbba7_o.jpg)

Plotting a number of lines:

```python
line = vincent.Line(multi_iter1, iter_idx='index')
line.axis_titles(x='Index', y='Value')
line.legend(title='Categories')
```

![lines](http://farm6.staticflickr.com/5543/9388500445_0bdf2a22e3_o.jpg)

Or a real use case, plotting stock data:

```python
line = vincent.Line(price[['GOOG', 'AAPL']])
line.axis_titles(x='Date', y='Price')
line.legend(title='GOOG vs AAPL')
```

![stocks1](http://farm4.staticflickr.com/3774/9391272680_67e323de24_o.jpg)

Color brewer scales are built-in. For example, plotting a scatter plot with the ```Set3``` colors:

```python
scatter = vincent.Scatter(multi_iter2, iter_idx='index')
scatter.axis_titles(x='Index', y='Data Value')
scatter.legend(title='Categories')
scatter.colors(brew='Set3')
```

![scatter](http://farm6.staticflickr.com/5341/9391272876_724d5fca0d_o.jpg)

Area charts:

```python
area = vincent.Area(list_data)
```

![area](http://farm3.staticflickr.com/2825/9388500487_b7c1a67771_o.jpg)

Stacked Area Charts from a DataFrame:
```python
stacked = vincent.StackedArea(df_1)
stacked.axis_titles(x='Index', y='Value')
stacked.legend(title='Categories')
stacked.colors(brew='Spectral')
```

![areastack](http://farm4.staticflickr.com/3827/9388500389_88ca0f0e5f_o.jpg)

```python
stacked = vincent.StackedArea(price)
stacked.axis_titles(x='Date', y='Price')
stacked.legend(title='Tech Stocks')
```
![areastack2](http://farm8.staticflickr.com/7355/9388540267_823111c78d_o.jpg)

Stacked Bar Charts from a DataFrame:

```python
stack = vincent.StackedBar(df_2)
stack.legend(title='Categories')
stack.scales['x'].padding = 0.1
```
![barstack1](http://farm6.staticflickr.com/5528/9391272710_c92d21da11_o.jpg)

```python
stack = vincent.StackedBar(df_farm.T)
stack.axis_titles(x='Total Produce', y='Farms')
stack.legend(title='Produce Types')
stack.colors(brew='Pastel1')
```
![barstack2](http://farm4.staticflickr.com/3784/9388530799_623084dbe0_o.jpg)

Grouped Bars from a DataFrame:

```python
group = vincent.GroupedBar(df_2)
group.legend(title='Categories')
group.colors(brew='Spectral')
group.width=750
```
![groupbar1](http://farm6.staticflickr.com/5507/9388500521_1ec446c0e9_o.jpg)

```python
group = vincent.GroupedBar(df_farm)
group.axis_titles(x='Total Produce', y='Farms')
group.legend(title='Produce Types')
group.colors(brew='Set2')
```
![groupbar2](http://farm6.staticflickr.com/5518/9391272912_706055754a_o.jpg)

Pie charts:

```python
vis = vincent.Pie(farm_1)
vis.legend('Farm 1 Fruit')
```
![pie](https://farm4.staticflickr.com/3684/11391908745_227ffba829.jpg)

Donut charts:

```
vis = vincent.Pie(farm_1, inner_radius=200)
vis.colors(brew="Set2")
vis.legend('Farm 1 Fruit')
```
![donut](http://farm6.staticflickr.com/5530/11391917226_598fbdf3e2.jpg)

Simple maps can be built quickly (all data can be found in the [vincent_map_data](https://github.com/wrobstory/vincent_map_data) repo):

```python
world_topo = r'world-countries.topo.json'
geo_data = [{'name': 'countries',
             'url': world_topo,
             'feature': 'world-countries'}]

vis = vincent.Map(geo_data=geo_data, scale=200)
```

![simplemap](http://farm3.staticflickr.com/2852/10140081393_fa46545724_c.jpg)

Also with multiple map layers:

```python
geo_data = [{'name': 'counties',
             'url': county_topo,
             'feature': 'us_counties.geo'},
            {'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'}]

vis = vincent.Map(geo_data=geo_data, scale=1000, projection='albersUsa')
del vis.marks[1].properties.update
vis.marks[0].properties.update.fill.value = '#084081'
vis.marks[1].properties.enter.stroke.value = '#fff'
vis.marks[0].properties.enter.stroke.value = '#7bccc4'

```

![multiplelayer](http://farm4.staticflickr.com/3797/10140037456_8256fbd32d_c.jpg)

Maps can be bound with data to Pandas DataFrames for choropleth visualizations (see [here](https://vincent.readthedocs.org/en/latest/quickstart.html#data) for map data munging):

```python
geo_data = [{'name': 'counties',
             'url': county_topo,
             'feature': 'us_counties.geo'}]

vis = vincent.Map(data=merged, geo_data=geo_data, scale=1100, projection='albersUsa',
          data_bind='Unemployment_rate_2011', data_key='FIPS',
          map_key={'counties': 'properties.FIPS'})
vis.marks[0].properties.enter.stroke_opacity = ValueRef(value=0.5)
vis.to_json('vega.json')
```

![binding1](http://farm8.staticflickr.com/7414/10139958645_681c6dd006_c.jpg)

It can be rebound on the fly with new data and color brewer scales:

```python
vis.rebind(column='Median_Household_Income_2011', brew='YlGnBu')
```

![binding2](http://farm3.staticflickr.com/2833/10140081893_4f5fa762c5_c.jpg)


For more examples, including how to build these from scratch, see the [examples](https://github.com/wrobstory/vincent) directory, or the [docs](https://vincent.readthedocs.org/en/latest/index.html).


Built from Scratch
------------------

To see how the charts are being built with Vincent -> Vega grammar, see the ```charts.py``` module.

Building the bar chart from scratch will provide a quick example of building with Vincent:

```python
import pandas as pd
from vincent import (Visualization, Scale, DataRef, Data, PropertySet,
                     Axis, ValueRef, MarkRef, MarkProperties, Mark)

df = pd.DataFrame({'Data 1': [15, 29, 63, 28, 45, 73, 15, 62],
                   'Data 2': [42, 27, 52, 18, 61, 19, 62, 33]})

#Top level Visualization
vis = Visualization(width=500, height=300)
vis.padding = {'top': 10, 'left': 50, 'bottom': 50, 'right': 100}

#Data. We're going to key Data 2 on Data 1
vis.data.append(Data.from_pandas(df, columns=['Data 2'], key_on='Data 1', name='table'))

#Scales
vis.scales.append(Scale(name='x', type='ordinal', range='width',
                        domain=DataRef(data='table', field="data.idx")))
vis.scales.append(Scale(name='y', range='height', nice=True,
                        domain=DataRef(data='table', field="data.val")))

#Axes
vis.axes.extend([Axis(type='x', scale='x'), Axis(type='y', scale='y')])

#Marks
enter_props = PropertySet(x=ValueRef(scale='x', field="data.idx"),
                                     y=ValueRef(scale='y', field="data.val"),
                                     width=ValueRef(scale='x', band=True, offset=-1),
                                     y2=ValueRef(scale='y', value=0))
update_props = PropertySet(fill=ValueRef(value='steelblue'))
mark = Mark(type='rect', from_=MarkRef(data='table'),
            properties=MarkProperties(enter=enter_props,
            update=update_props))

vis.marks.append(mark)
vis.axis_titles(x='Data 1', y='Data 2')
vis.to_json('vega.json')
```
![barscratch](http://farm3.staticflickr.com/2866/9341688818_c154660c3f_o.jpg)

Because the Vega elements are represented by Python classes, it can be difficult to get a good idea of what the Vega grammar looks like:
```python
In [5]: vis.marks[0]
<vincent.marks.Mark at 0x110d630d0>
```

However, at almost any point in the Vincent stack, you can call the ```grammar()``` method to output the Vega grammar as Python data structures:

```python
>>>vis.marks[0].grammar()
{u'from': {u'data': u'table'},
 u'properties': {u'enter': {u'width': {u'band': True,
    u'offset': -1,
    u'scale': u'x'},
   u'x': {u'field': u'data.idx', u'scale': u'x'},
   u'y': {u'field': u'data.val', u'scale': u'y'},
   u'y2': {u'scale': u'y', u'value': 0}},
  u'update': {u'fill': {u'value': u'steelblue'}}},
 u'type': u'rect'}
>>>vis.marks[0].properties.enter.x.grammar()
{u'field': u'data.idx', u'scale': u'x'}
```

or you can simply output it to a string of JSON:
```python
>>>print(vis.marks[0].to_json())
{
  "type": "rect",
  "from": {
    "data": "table"
  },
  "properties": {
    "update": {
      "fill": {
        "value": "steelblue"
      }
    },
    "enter": {
      "y": {
        "field": "data.val",
        "scale": "y"
      },
      "width": {
        "band": true,
        "scale": "x",
        "offset": -1
      },
      "y2": {
        "scale": "y",
        "value": 0
      },
      "x": {
        "field": "data.idx",
        "scale": "x"
      }
    }
  }
}
```

Vincent is built around classes and attributes that map 1:1 to Vega grammar, for easy getting, setting,
and deleting of grammar elements:

```python
>>>vis.marks[0].properties.enter.grammar()
{u'width': {u'band': True, u'offset': -1, u'scale': u'x'},
 u'x': {u'field': u'data.idx', u'scale': u'x'},
 u'y': {u'field': u'data.val', u'scale': u'y'},
 u'y2': {u'scale': u'y', u'value': 0}}
 >>> del vis.marks[0].properties.enter.width
 >>> vis.marks[0].properties.enter.y2.scale = 'y2'
 >>> vis.marks[0].properties.enter.grammar()
{u'x': {u'field': u'data.idx', u'scale': u'x'},
 u'y': {u'field': u'data.val', u'scale': u'y'},
 u'y2': {u'scale': u'y2', u'value': 0}}
```

Contributors
------------
Huge thanks to all who have contributed to Vincent development:

 * Rob Story (wrobstory)
 * Dan Miller (dnmiller)
 * Peter Lubell-Doughtie (pld)
 * Lx Yu (lxyu)
 * Damien Garaud (garaud)
 * Abraham Flaxman (aflaxman)
 * Mahdi Yusuf (myusuf3)
 * Richard Maisano (maisano)
 * Julian Berman (Julian)
 * Chris Rebert (cvrebert)
 * Wojciech Bederski (wuub)
 * Min RK (minrk)
 * Drazen Lucanin (kermit666)
 * tlukasiak


Dependencies
------------

 * pandas
 * pkgtools

Testing:

 * mock
 * nose

PSA: you can use pieces of Vincent without Pandas, but its tricky. Besides, Pandas is awesome- try it!




