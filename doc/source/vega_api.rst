.. currentmodule:: vincent.core

Vega API Reference
==================

The full Vega specification is exposed through a set of object-relational
JSON classes.


Visualization
+++++++++++++

Field properties for :class:`Visualization`:

.. autofield:: core.Visualization.name
.. autofield:: core.Visualization.width
.. autofield:: core.Visualization.height
.. autofield:: core.Visualization.viewport
.. autofield:: core.Visualization.padding
.. autofield:: core.Visualization.data
.. autofield:: core.Visualization.scales
.. autofield:: core.Visualization.axes
.. autofield:: core.Visualization.marks

Data
++++

Field properties for :class:`Data`:

.. autofield:: core.Data.name
.. autofield:: core.Data.url
.. autofield:: core.Data.values
.. autofield:: core.Data.source
.. autofield:: core.Data.transform
.. autofield:: core.Data.format


Scale
+++++

Field properties for :class:`Scale`:

.. autofield:: core.Scale.name
.. autofield:: core.Scale.type
.. autofield:: core.Scale.domain
.. autofield:: core.Scale.domain_min
.. autofield:: core.Scale.domain_max
.. autofield:: core.Scale.range
.. autofield:: core.Scale.range_min
.. autofield:: core.Scale.range_max
.. autofield:: core.Scale.reverse
.. autofield:: core.Scale.round
.. autofield:: core.Scale.points
.. autofield:: core.Scale.clamp
.. autofield:: core.Scale.nice
.. autofield:: core.Scale.exponent
.. autofield:: core.Scale.zero


DataRef
+++++++

Field properties for :class:`DataRef`:

.. autofield:: core.DataRef.data
.. autofield:: core.DataRef.field


ValueRef
++++++++

Field properties for :class:`ValueRef`:

.. autofield:: core.ValueRef.value
.. autofield:: core.ValueRef.field
.. autofield:: core.ValueRef.scale
.. autofield:: core.ValueRef.mult
.. autofield:: core.ValueRef.offset
.. autofield:: core.ValueRef.band


Mark
++++

Field properties for :class:`Mark`:

.. autofield:: core.Mark.name
.. autofield:: core.Mark.description
.. autofield:: core.Mark.type
.. autofield:: core.Mark.from_
.. autofield:: core.Mark.properties
.. autofield:: core.Mark.key
.. autofield:: core.Mark.delay
.. autofield:: core.Mark.ease


Properties
++++++++++

Field properties for :class:`Properties`:

.. autofield:: core.Properties.enter
.. autofield:: core.Properties.exit
.. autofield:: core.Properties.update
.. autofield:: core.Properties.hover


PropertySet
+++++++++++

Field properties for :class:`PropertySet`:

.. autofield:: core.PropertySet.x
.. autofield:: core.PropertySet.x2
.. autofield:: core.PropertySet.width
.. autofield:: core.PropertySet.y
.. autofield:: core.PropertySet.y2
.. autofield:: core.PropertySet.height
.. autofield:: core.PropertySet.opacity
.. autofield:: core.PropertySet.fill
.. autofield:: core.PropertySet.fill_opacity
.. autofield:: core.PropertySet.stroke
.. autofield:: core.PropertySet.stroke_width
.. autofield:: core.PropertySet.stroke_opacity
.. autofield:: core.PropertySet.size
.. autofield:: core.PropertySet.shape
.. autofield:: core.PropertySet.path
.. autofield:: core.PropertySet.inner_radius
.. autofield:: core.PropertySet.outer_radius
.. autofield:: core.PropertySet.start_angle
.. autofield:: core.PropertySet.end_angle
.. autofield:: core.PropertySet.interpolate
.. autofield:: core.PropertySet.tension
.. autofield:: core.PropertySet.url
.. autofield:: core.PropertySet.align
.. autofield:: core.PropertySet.baseline
.. autofield:: core.PropertySet.text
.. autofield:: core.PropertySet.dx
.. autofield:: core.PropertySet.dy
.. autofield:: core.PropertySet.font
.. autofield:: core.PropertySet.font_size
.. autofield:: core.PropertySet.font_weight
.. autofield:: core.PropertySet.font_style

