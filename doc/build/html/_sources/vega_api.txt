.. currentmodule:: vincent.visualization
.. currentmodule:: vincent.data
.. currentmodule:: vincent.scale
.. currentmodule:: vincent.axes
.. currentmodule:: vincent.marks
.. currentmodule:: vincent.properties
.. currentmodule:: vincent.transforms
.. currentmodule:: vincent.values

.. _API_header:

Vega API Reference
==================

The full Vega specification is exposed through a set of object-relational
JSON classes. Vincent also pr

.. _API_Visualization:

Visualization
-------------

Field properties for :class:`Visualization`:

.. autofield:: visualization.Visualization.name
.. autofield:: visualization.Visualization.width
.. autofield:: visualization.Visualization.height
.. autofield:: visualization.Visualization.viewport
.. autofield:: visualization.Visualization.padding
.. autofield:: visualization.Visualization.data
.. autofield:: visualization.Visualization.scales
.. autofield:: visualization.Visualization.axes
.. autofield:: visualization.Visualization.marks
.. autofield:: visualization.Visualization.legends

.. _API_Data:

Data
----

Field properties for :class:`Data`:

.. autofield:: data.Data.name
.. autofield:: data.Data.url
.. autofield:: data.Data.values
.. autofield:: data.Data.source
.. autofield:: data.Data.transform
.. autofield:: data.Data.format

.. _API_Scale:

Scale
-----

Field properties for :class:`Scale`:

.. autofield:: scales.Scale.name
.. autofield:: scales.Scale.type
.. autofield:: scales.Scale.domain
.. autofield:: scales.Scale.domain_min
.. autofield:: scales.Scale.domain_max
.. autofield:: scales.Scale.range
.. autofield:: scales.Scale.range_min
.. autofield:: scales.Scale.range_max
.. autofield:: scales.Scale.reverse
.. autofield:: scales.Scale.round
.. autofield:: scales.Scale.points
.. autofield:: scales.Scale.clamp
.. autofield:: scales.Scale.nice
.. autofield:: scales.Scale.exponent
.. autofield:: scales.Scale.zero
.. autofield:: scales.Scale.padding

.. _API_DataRef:

DataRef
--------

Field properties for :class:`DataRef`:

.. autofield:: scales.DataRef.data
.. autofield:: scales.DataRef.field

.. _API_ValueRef:

ValueRef
++++++++

Field properties for :class:`ValueRef`:

.. autofield:: values.ValueRef.value
.. autofield:: values.ValueRef.field
.. autofield:: values.ValueRef.scale
.. autofield:: values.ValueRef.mult
.. autofield:: values.ValueRef.offset
.. autofield:: values.ValueRef.band

.. _API_MarkRef:

Mark
----

Field properties for :class:`Mark`:

.. autofield:: marks.Mark.name
.. autofield:: marks.Mark.description
.. autofield:: marks.Mark.type
.. autofield:: marks.Mark.from_
.. autofield:: marks.Mark.properties
.. autofield:: marks.Mark.key
.. autofield:: marks.Mark.delay
.. autofield:: marks.Mark.ease

.. _API_MarkPropertyRef:

Mark Properties
---------------

Field properties for :class:`MarkProperties`:

.. autofield:: marks.MarkProperties.enter
.. autofield:: marks.MarkProperties.exit
.. autofield:: marks.MarkProperties.update
.. autofield:: marks.MarkProperties.hover

.. _API_PropertySet:

PropertySet
-----------

Field properties for :class:`PropertySet`:

.. autofield:: properties.PropertySet.x
.. autofield:: properties.PropertySet.x2
.. autofield:: properties.PropertySet.width
.. autofield:: properties.PropertySet.y
.. autofield:: properties.PropertySet.y2
.. autofield:: properties.PropertySet.height
.. autofield:: properties.PropertySet.opacity
.. autofield:: properties.PropertySet.fill
.. autofield:: properties.PropertySet.fill_opacity
.. autofield:: properties.PropertySet.stroke
.. autofield:: properties.PropertySet.stroke_width
.. autofield:: properties.PropertySet.stroke_opacity
.. autofield:: properties.PropertySet.size
.. autofield:: properties.PropertySet.shape
.. autofield:: properties.PropertySet.path
.. autofield:: properties.PropertySet.inner_radius
.. autofield:: properties.PropertySet.outer_radius
.. autofield:: properties.PropertySet.start_angle
.. autofield:: properties.PropertySet.end_angle
.. autofield:: properties.PropertySet.interpolate
.. autofield:: properties.PropertySet.tension
.. autofield:: properties.PropertySet.url
.. autofield:: properties.PropertySet.align
.. autofield:: properties.PropertySet.baseline
.. autofield:: properties.PropertySet.text
.. autofield:: properties.PropertySet.dx
.. autofield:: properties.PropertySet.dy
.. autofield:: properties.PropertySet.font
.. autofield:: properties.PropertySet.font_size
.. autofield:: properties.PropertySet.font_weight
.. autofield:: properties.PropertySet.font_style

.. _API_Transforms:

Transforms
----------

Field properties for :class:`Transform`:

.. autofield:: transforms.Transform.type
.. autofield:: transforms.Transform.fields
.. autofield:: transforms.Transform.from_
.. autofield:: transforms.Transform.as_
.. autofield:: transforms.Transform.keys
.. autofield:: transforms.Transform.sort
.. autofield:: transforms.Transform.test
.. autofield:: transforms.Transform.field
.. autofield:: transforms.Transform.expr
.. autofield:: transforms.Transform.by
.. autofield:: transforms.Transform.value
.. autofield:: transforms.Transform.median
.. autofield:: transforms.Transform.with_
.. autofield:: transforms.Transform.key
.. autofield:: transforms.Transform.with_key
.. autofield:: transforms.Transform.links
.. autofield:: transforms.Transform.size
.. autofield:: transforms.Transform.iterations
.. autofield:: transforms.Transform.charge
.. autofield:: transforms.Transform.link_distance
.. autofield:: transforms.Transform.link_strength
.. autofield:: transforms.Transform.friction
.. autofield:: transforms.Transform.theta
.. autofield:: transforms.Transform.gravity
.. autofield:: transforms.Transform.alpha
.. autofield:: transforms.Transform.point
.. autofield:: transforms.Transform.height
.. autofield:: transforms.Transform.offset
.. autofield:: transforms.Transform.order

