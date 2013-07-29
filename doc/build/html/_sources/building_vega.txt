.. _building_vega:

Building Vega with Vincent
=========================


The Vincent API attempts to map 1:1 to Vega grammar through a set of object relational classes. You can build complex Vega grammar directly with Vincent via simple getters and setters.

.. _build_grammar:

Grammar
-------

Here is an example of a simple set of marks for a bar chart in Vega JSON.

.. code-block:: json

        {
      "type": "rect",
      "from": {"data": "table"},
      "properties": {
        "enter": {
          "x": {"scale": "x", "field": "data.idx"},
          "width": {"scale": "x", "band": true, "offset": -1},
          "y": {"scale": "y", "field": "data.val"},
          "y2": {"scale": "y", "value": 0}
        },
        "update": {
          "fill": {"value": "steelblue"}
        },
        "hover": {
          "fill": {"value": "red"}
        }
      }
    }

Here's the same thing being built with Vincent's API::

    from vincent import *

    enter_props = PropertySet(x=ValueRef(scale='x', field="data.idx"),
                              y=ValueRef(scale='y', field="data.val"),
                              width=ValueRef(scale='x', band=True, offset=-1),
                              y2=ValueRef(scale='y', value=0))

    update_props = PropertySet(fill=ValueRef(value='steelblue'))

    mark = Mark(type='rect', from_=MarkRef(data='table'),
                properties=MarkProperties(enter=enter_props,update=update_props))

If you wanted to transform this into a line chart, Vincent makes spec changes simple. Let's change the fill color. Assuming that your Vincent object is named ``vis``::

    vis.marks[0].properties.update.fill.value = 'red'

If you want to check on the grammar, you can call ``grammar()`` to return a Python data structure representation of the Vega grammar at almost any level of nesting depth::

    >>>vis.marks[0].properties.grammar()
    {u'enter': {u'width': {u'band': True, u'offset': -1, u'scale': u'x'},
     u'x': {u'field': u'data.idx', u'scale': u'x'},
     u'y': {u'field': u'data.val', u'scale': u'y'},
     u'y2': {u'scale': u'y', u'value': 0}},
    u'update': {u'fill': {u'value': u'steelblue'}}}

Vincent also performs type-checking on grammar elements to try and avoid grammar errors::

    >>>vis.marks[0].properties.enter.y2.scale = 1

    ValueError: scale must be str

The best way to get an idea of how to build Vega grammar with Vincent is to see the examples in the `Github Repo <https://github.com/wrobstory/vincent/tree/master/examples>`_ . Building a bar chart from scratch using the Vincent API looks as follows::

    from vincent import *

    vis = Visualization(width=500, height=300)
    vis.scales['x'] = Scale(name='x', type='ordinal', range='width',
                            domain=DataRef(data='table', field="data.idx"))
    vis.scales['y'] = Scale(name='y', range='height', nice=True,
                            domain=DataRef(data='table', field="data.val"))
    vis.axes.extend([Axis(type='x', scale='x'),
                     Axis(type='y', scale='y')])

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

    data = Data.from_iter([10, 20, 30, 40, 50])
    #Using a Vincent KeyedList here
    vis.data['table'] = data

You'll notice two interesting pieces here: ``Data`` , and the ``KeyedList``

.. _build_keyedlist:

Keyed List
----------

The Vega specification consists of high level attributes such as scales, marks, axes, legends, etc, each with an array containing any number of individual marks, scales, etc. It's useful to be able to index these arrays by name, so Vincent has introduced a Python List that can also be
indexed by a name parameter.

So, for example, if we want to introduce a new color scale::

  scale = vincent.Scale(name='color', type='ordinal',
                        domain=DataRef(data='table', field='data.col'),
                        range='category20')

We can add it to the scales list and index it by name::

  vis.scales['color'] = scale

Note that the name must match the index you inserting::

  vis.scales['newscale'] = scale

  ValidationError: key must be equal to 'name' attribute

Data Importing
--------------

The Vincent Data class has a number of conveniences for import Python data types.

First, ``from_iter``, which will take lists, tuples, or key/value dicts::

  list_dat = [10, 20, 30, 40, 50]
  data = vincent.Data.from_iter(list_dat)

  data.values
  [{'col': 'data', 'idx': 0, 'val': 10},
   {'col': 'data', 'idx': 1, 'val': 20},
   {'col': 'data', 'idx': 2, 'val': 30},
   {'col': 'data', 'idx': 3, 'val': 40},
   {'col': 'data', 'idx': 4, 'val': 50}]

  dict_dat = {'x': 10, 'y': 20, 'z': 30}
  data = vincent.Data.from_iter(dict_dat)

  data.values
  [{'col': 'data', 'idx': 'y', 'val': 20},
   {'col': 'data', 'idx': 'x', 'val': 10},
   {'col': 'data', 'idx': 'z', 'val': 30}]


There's also a ``from_mult_iters`` convenience method, in which you must provide a common index::

  x = [0, 1, 2, 3, 4]
  y = [10, 20, 30, 40, 50]
  z = [70, 80, 90, 100, 110]
  data = vincent.Data.from_mult_iters(index=x, values1=y, values2=z, idx='index')

  data.values
  [{'col': 'values1', 'idx': 0, 'val': 10},
   {'col': 'values1', 'idx': 1, 'val': 20},
   {'col': 'values1', 'idx': 2, 'val': 30},
   {'col': 'values1', 'idx': 3, 'val': 40},
   {'col': 'values1', 'idx': 4, 'val': 50},
   {'col': 'values2', 'idx': 0, 'val': 70},
   {'col': 'values2', 'idx': 1, 'val': 80},
   {'col': 'values2', 'idx': 2, 'val': 90},
   {'col': 'values2', 'idx': 3, 'val': 100},
   {'col': 'values2', 'idx': 4, 'val': 110}]

This indexing structure allows for faceting on ``col`` or ``idx`` for charts like stacked or grouped bars.

The best way to get data into Vincent is with the Pandas Series and DataFrame. These provide built-in indexing and index sorting, and will generally make your charts appear nicer. We'll start with Series::

  series = pd.Series([10, 20, 30, 40, 50])
  data = vincent.Data.from_pandas(series)

  data.values
  [{'col': 'data', 'idx': 0, 'val': 10},
   {'col': 'data', 'idx': 1, 'val': 20},
   {'col': 'data', 'idx': 2, 'val': 30},
   {'col': 'data', 'idx': 3, 'val': 40},
   {'col': 'data', 'idx': 4, 'val': 50}]

If the series has a name, this will be your ``col`` value::

  series.name = 'metric'
  data = vincent.Data.from_pandas(series)

  data.values
  [{'col': 'metric', 'idx': 0, 'val': 10},
   {'col': 'metric', 'idx': 1, 'val': 20},
   {'col': 'metric', 'idx': 2, 'val': 30},
   {'col': 'metric', 'idx': 3, 'val': 40},
   {'col': 'metric', 'idx': 4, 'val': 50}]

DataFrames are just as simple::

  farm_1 = {'apples': 10, 'berries': 32, 'squash': 21}
  farm_2 = {'apples': 15, 'berries': 43, 'squash': 17}
  farm_3 = {'apples': 6, 'berries': 24, 'squash': 22}

  farm_data = [farm_1, farm_2, farm_3]
  farm_index = ['Farm 1', 'Farm 2', 'Farm 3']
  df = pd.DataFrame(farm_data, index=farm_index)
  data = vincent.Data.from_pandas(df)

  data.values
  [{'col': 'apples', 'idx': 'Farm 1', 'val': 10},
   {'col': 'berries', 'idx': 'Farm 1', 'val': 32},
   {'col': 'squash', 'idx': 'Farm 1', 'val': 21},
   {'col': 'apples', 'idx': 'Farm 2', 'val': 15},
   {'col': 'berries', 'idx': 'Farm 2', 'val': 43},
   {'col': 'squash', 'idx': 'Farm 2', 'val': 17},
   {'col': 'apples', 'idx': 'Farm 3', 'val': 6},
   {'col': 'berries', 'idx': 'Farm 3', 'val': 24},
   {'col': 'squash', 'idx': 'Farm 3', 'val': 22}]

You can also key on a column, rather than the index::

  data = vincent.Data.from_pandas(df, key_on='apples')

  data.values
  [{'col': 'apples', 'idx': 10, 'val': 10},
   {'col': 'berries', 'idx': 10, 'val': 32},
   {'col': 'squash', 'idx': 10, 'val': 21},
   {'col': 'apples', 'idx': 15, 'val': 15},
   {'col': 'berries', 'idx': 15, 'val': 43},
   {'col': 'squash', 'idx': 15, 'val': 17},
   {'col': 'apples', 'idx': 6, 'val': 6},
   {'col': 'berries', 'idx': 6, 'val': 24},
   {'col': 'squash', 'idx': 6, 'val': 22}]

Finally, if you turn on ``grouped``, it will add an additional iterative key for Vega grouping that groups on the column values::

  data = vincent.Data.from_pandas(df, grouped=True)]

  data.values
  [{'col': 'apples', 'group': 0, 'idx': 'Farm 1', 'val': 10},
   {'col': 'berries', 'group': 1, 'idx': 'Farm 1', 'val': 32},
   {'col': 'squash', 'group': 2, 'idx': 'Farm 1', 'val': 21},
   {'col': 'apples', 'group': 0, 'idx': 'Farm 2', 'val': 15},
   {'col': 'berries', 'group': 1, 'idx': 'Farm 2', 'val': 43},
   {'col': 'squash', 'group': 2, 'idx': 'Farm 2', 'val': 17},
   {'col': 'apples', 'group': 0, 'idx': 'Farm 3', 'val': 6},
   {'col': 'berries', 'group': 1, 'idx': 'Farm 3', 'val': 24},
   {'col': 'squash', 'group': 2, 'idx': 'Farm 3', 'val': 22}]