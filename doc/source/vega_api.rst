.. currentmodule:: vincent.vega

Vega API Reference
==================

The full Vega specification is exposed through a set of object-relational
JSON classes.


Visualization
+++++++++++++

Field properties for :class:`Visualization`:

.. autofield:: vega.Visualization.name
.. autofield:: vega.Visualization.width
.. autofield:: vega.Visualization.height
.. autofield:: vega.Visualization.viewport
.. autofield:: vega.Visualization.padding
.. autofield:: vega.Visualization.data
.. autofield:: vega.Visualization.scales
.. autofield:: vega.Visualization.axes
.. autofield:: vega.Visualization.marks

Data
++++

Field properties for :class:`Data`:

.. autofield:: vega.Data.name
.. autofield:: vega.Data.url
.. autofield:: vega.Data.values
.. autofield:: vega.Data.source
.. autofield:: vega.Data.transform
.. autofield:: vega.Data.format


Scale
+++++

Field properties for :class:`Scale`:

.. autofield:: vega.Scale.name
.. autofield:: vega.Scale.type
.. autofield:: vega.Scale.domain
.. autofield:: vega.Scale.domain_min
.. autofield:: vega.Scale.domain_max
.. autofield:: vega.Scale.range
.. autofield:: vega.Scale.range_min
.. autofield:: vega.Scale.range_max
.. autofield:: vega.Scale.reverse
.. autofield:: vega.Scale.round
.. autofield:: vega.Scale.points
.. autofield:: vega.Scale.clamp
.. autofield:: vega.Scale.nice
.. autofield:: vega.Scale.exponent
.. autofield:: vega.Scale.zero


DataRef
+++++++

Field properties for :class:`DataRef`:

.. autofield:: vega.DataRef.data
.. autofield:: vega.DataRef.field


ValueRef
++++++++

Field properties for :class:`ValueRef`:

.. autofield:: vega.ValueRef.value
.. autofield:: vega.ValueRef.field
.. autofield:: vega.ValueRef.scale
.. autofield:: vega.ValueRef.mult
.. autofield:: vega.ValueRef.offset
.. autofield:: vega.ValueRef.band


Mark
++++

Field properties for :class:`Mark`:

.. autofield:: vega.Mark.name
.. autofield:: vega.Mark.description
.. autofield:: vega.Mark.type
.. autofield:: vega.Mark.from_
.. autofield:: vega.Mark.properties
.. autofield:: vega.Mark.key
.. autofield:: vega.Mark.delay
.. autofield:: vega.Mark.ease


Properties
++++++++++

Field properties for :class:`Properties`:

.. autofield:: vega.Properties.enter
.. autofield:: vega.Properties.exit
.. autofield:: vega.Properties.update
.. autofield:: vega.Properties.hover


PropertySet
+++++++++++

Field properties for :class:`PropertySet`:

.. autofield:: vega.PropertySet.x
.. autofield:: vega.PropertySet.x2
.. autofield:: vega.PropertySet.width
.. autofield:: vega.PropertySet.y
.. autofield:: vega.PropertySet.y2
.. autofield:: vega.PropertySet.height
.. autofield:: vega.PropertySet.opacity
.. autofield:: vega.PropertySet.fill
.. autofield:: vega.PropertySet.fill_opacity
.. autofield:: vega.PropertySet.stroke
.. autofield:: vega.PropertySet.stroke_width
.. autofield:: vega.PropertySet.stroke_opacity
.. autofield:: vega.PropertySet.size
.. autofield:: vega.PropertySet.shape
.. autofield:: vega.PropertySet.path
.. autofield:: vega.PropertySet.inner_radius
.. autofield:: vega.PropertySet.outer_radius
.. autofield:: vega.PropertySet.start_angle
.. autofield:: vega.PropertySet.end_angle
.. autofield:: vega.PropertySet.interpolate
.. autofield:: vega.PropertySet.tension
.. autofield:: vega.PropertySet.url
.. autofield:: vega.PropertySet.align
.. autofield:: vega.PropertySet.baseline
.. autofield:: vega.PropertySet.text
.. autofield:: vega.PropertySet.dx
.. autofield:: vega.PropertySet.dy
.. autofield:: vega.PropertySet.font
.. autofield:: vega.PropertySet.font_size
.. autofield:: vega.PropertySet.font_weight
.. autofield:: vega.PropertySet.font_style

