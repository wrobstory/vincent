.. currentmodule:: vincent.visualization
.. currentmodule:: vincent.data
.. currentmodule:: vincent.scale

Vega API Reference
==================

The full Vega specification is exposed through a set of object-relational
JSON classes.


Visualization
+++++++++++++

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

Data
++++

Field properties for :class:`Data`:

.. autofield:: data.Data.name
.. autofield:: data.Data.url
.. autofield:: data.Data.values
.. autofield:: data.Data.source
.. autofield:: data.Data.transform
.. autofield:: data.Data.format


Scale
+++++

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

