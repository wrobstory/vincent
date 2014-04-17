# -*- coding: utf-8 -*-
"""

Visualization: Top level class for Vega Grammar

"""
from __future__ import (print_function, division)
from uuid import uuid4
from .core import (_assert_is_type, ValidationError,
                   KeyedList, grammar, GrammarClass)
from .data import Data
from .scales import Scale
from .marks import Mark
from .axes import Axis, AxisProperties
from .legends import Legend, LegendProperties
from .properties import PropertySet
from .values import ValueRef
from .colors import brews
from ._compat import str_types


class Visualization(GrammarClass):
    """Visualization container class.

    This class defines the full visualization. Calling its ``to_json``
    method should return a complete Vega definition.

    The sub-elements of the visualization are stored in the ``data``,
    ``axes``, ``marks``, and ``scales`` attributes. See the docs for each
    attribute for details.
    """
    def __init__(self, *args, **kwargs):
        """Initialize a Visualization

        In addition to setting any attributes, this sets the data, marks,
        scales, and axes properties to empty KeyedLists if they aren't
        defined by the arguments.
        """
        super(Visualization, self).__init__(*args, **kwargs)

        for attrib in ('data', 'scales'):
            if not getattr(self, attrib):
                setattr(self, attrib, KeyedList(attr_name='name'))

        for attrib in ('axes', 'marks'):
            if not getattr(self, attrib):
                setattr(self, attrib, KeyedList(attr_name='type'))

        # Legends don't get keyed.
        if not self.legends:
            self.legends = []

    @grammar(str_types)
    def name(value):
        """string : Name of the visualization (optional)
        """

    @grammar(int)
    def width(value):
        """int : Width of the visualization in pixels

        Default is 500 if undefined.
        """
        if value < 0:
            raise ValueError('width cannot be negative')

    @grammar(int)
    def height(value):
        """int : Height of the visualization in pixels

        Default is 500 if undefined.
        """
        if value < 0:
            raise ValueError('height cannot be negative')

    @grammar(list)
    def viewport(value):
        """2-element list of ints : Dimensions of the viewport

        The viewport is a bounding box containing the visualization. If the
        dimensions of the visualization are larger than the viewport, then
        the visualization will be scrollable.

        If undefined, then the full visualization is shown.
        """
        if len(value) != 2:
            raise ValueError('viewport must have 2 dimensions')
        for v in value:
            _assert_is_type('viewport dimension', v, int)
            if v < 0:
                raise ValueError('viewport dimensions cannot be negative')

    @grammar((int, dict,) + str_types)
    def padding(value):
        """int or dict : Padding around visualization

        The padding defines the distance between the edge of the
        visualization canvas to the visualization box. It does not count as
        part of the visualization width/height. Values cannot be negative.

        If a dict, padding must have all keys ``''top'``, ``'left'``,
        ``'right'``, and ``'bottom'`` with int values.
        """
        if isinstance(value, dict):
            required_keys = ['top', 'left', 'right', 'bottom']
            for key in required_keys:
                if key not in value:
                    error = ('Padding must have keys "{0}".'
                             .format('", "'.join(required_keys)))
                    raise ValueError(error)
                _assert_is_type('padding: {0}'.format(key), value[key], int)
                if value[key] < 0:
                    raise ValueError('Padding cannot be negative.')
        elif isinstance(value, int):
            if value < 0:
                raise ValueError('Padding cannot be negative.')
        else:
            if value not in ("auto", "strict"):
                raise ValueError('Padding can only be auto or strict.')

    @grammar((list, KeyedList))
    def data(value):
        """list or KeyedList of ``Data`` : Data definitions

        This defines the data being visualized. See the :class:`Data` class
        for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('data[{0}]'.format(i), entry,  Data)

    @grammar((list, KeyedList))
    def scales(value):
        """list or KeyedList of ``Scale`` : Scale definitions

        Scales map the data from the domain of the data to some
        visualization space (such as an x-axis). See the :class:`Scale`
        class for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('scales[{0}]'.format(i), entry, Scale)

    @grammar((list, KeyedList))
    def axes(value):
        """list or KeyedList of ``Axis`` : Axis definitions

        Axes define the locations of the data being mapped by the scales.
        See the :class:`Axis` class for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('axes[{0}]'.format(i), entry, Axis)

    @grammar((list, KeyedList))
    def marks(value):
        """list or KeyedList of ``Mark`` : Mark definitions

        Marks are the visual objects (such as lines, bars, etc.) that
        represent the data in the visualization space. See the :class:`Mark`
        class for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('marks[{0}]'.format(i), entry, Mark)

    @grammar((list, KeyedList))
    def legends(value):
        """list or KeyedList of ``Legends`` : Legend definitions

        Legends visualize scales, and take one or more scales as their input.
        They can be customized via a LegendProperty object.
        """
        for i, entry in enumerate(value):
            _assert_is_type('legends[{0}]'.format(i), entry, Legend)

    def axis_titles(self, x=None, y=None):
        """Apply axis titles to the figure.

        This is a convenience method for manually modifying the "Axes" mark.

        Parameters
        ----------
        x: string, default 'null'
            X-axis title
        y: string, default 'null'
            Y-axis title

        Example
        -------
        >>>vis.axis_titles(y="Data 1", x="Data 2")

        """
        keys = self.axes.get_keys()

        if keys:
            for key in keys:
                if key == 'x':
                    self.axes[key].title = x
                elif key == 'y':
                    self.axes[key].title = y
        else:
            self.axes.extend([Axis(type='x', title=x),
                              Axis(type='y', title=y)])
        return self

    def _set_axis_properties(self, axis):
        """Set AxisProperties and PropertySets"""
        if not getattr(axis, 'properties'):
            axis.properties = AxisProperties()
            for prop in ['ticks', 'axis', 'major_ticks', 'minor_ticks',
                         'title', 'labels']:
                setattr(axis.properties, prop, PropertySet())

    def _set_all_axis_color(self, axis, color):
        """Set axis ticks, title, labels to given color"""
        for prop in ['ticks', 'axis', 'major_ticks', 'minor_ticks', 'title',
                     'labels']:
            prop_set = getattr(axis.properties, prop)
            if color and prop in ['title', 'labels']:
                prop_set.fill = ValueRef(value=color)
            elif color and prop in ['axis', 'major_ticks', 'minor_ticks',
                                    'ticks']:
                prop_set.stroke = ValueRef(value=color)

    def _axis_properties(self, axis, title_size, title_offset, label_angle,
                         label_align, color):
        """Assign axis properties"""
        if self.axes:
            axis = [a for a in self.axes if a.scale == axis][0]
            self._set_axis_properties(axis)
            self._set_all_axis_color(axis, color)

            if title_size:
                axis.properties.title.font_size = ValueRef(value=title_size)
            if label_angle:
                axis.properties.labels.angle = ValueRef(value=label_angle)
            if label_align:
                axis.properties.labels.align = ValueRef(value=label_align)
            if title_offset:
                axis.properties.title.dy = ValueRef(value=title_offset)
        else:
            raise ValueError('This Visualization has no axes!')

    def common_axis_properties(self, color=None, title_size=None):
        """Set common axis properties such as color

        Parameters
        ----------
        color: str, default None
            Hex color str, etc
        """
        if self.axes:
            for axis in self.axes:
                self._set_axis_properties(axis)
                self._set_all_axis_color(axis, color)
                if title_size:
                    ref = ValueRef(value=title_size)
                    axis.properties.title.font_size = ref
        else:
            raise ValueError('This Visualization has no axes!')
        return self

    def x_axis_properties(self, title_size=None, title_offset=None,
                          label_angle=None, label_align=None, color=None):
        """Change x-axis title font size and label angle

        Parameters
        ----------
        title_size: int, default None
            Title size, in px
        title_offset: int, default None
            Pixel offset from given axis
        label_angle: int, default None
            label angle in degrees
        label_align: str, default None
            Label alignment
        color: str, default None
            Hex color
        """
        self._axis_properties('x', title_size, title_offset, label_angle,
                              label_align, color)
        return self

    def y_axis_properties(self, title_size=None, title_offset=None,
                          label_angle=None, label_align=None, color=None):
        """Change y-axis title font size and label angle

        Parameters
        ----------
        title_size: int, default None
            Title size, in px
        title_offset: int, default None
            Pixel offset from given axis
        label_angle: int, default None
            label angle in degrees
        label_align: str, default None
            Label alignment
        color: str, default None
            Hex color
        """
        self._axis_properties('y', title_size, title_offset, label_angle,
                              label_align, color)
        return self

    def legend(self, title=None, scale='color', text_color=None):
        """Convience method for adding a legend to the figure.

        Important: This defaults to the color scale that is generated with
        Line, Area, Stacked Line, etc charts. For bar charts, the scale ref is
        usually 'y'.

        Parameters
        ----------
        title: string, default None
            Legend Title
        scale: string, default 'color'
            Scale reference for legend
        text_color: str, default None
            Title and label color
        """

        self.legends.append(Legend(title=title, fill=scale, offset=0,
                                   properties=LegendProperties()))
        if text_color:
            color_props = PropertySet(fill=ValueRef(value=text_color))
            self.legends[0].properties.labels = color_props
            self.legends[0].properties.title = color_props
        return self

    def colors(self, brew=None, range_=None):
        """Convenience method for adding color brewer scales to charts with a
        color scale, such as stacked or grouped bars.

        See the colors here: http://colorbrewer2.org/

        Or here: http://bl.ocks.org/mbostock/5577023

        This assumes that a 'color' scale exists on your chart.

        Parameters
        ----------
        brew: string, default None
            Color brewer scheme (BuGn, YlOrRd, etc)
        range: list, default None
            List of colors. Ex: ['#ac4142', '#d28445', '#f4bf75']
        """
        if brew:
            self.scales['color'].range = brews[brew]
        elif range_:
            self.scales['color'].range = range_
        return self

    def validate(self, require_all=True, scale='colors'):
        """Validate the visualization contents.

        Parameters
        ----------
        require_all : boolean, default True
            If True (default), then all fields ``data``, ``scales``,
            ``axes``, and ``marks`` must be defined. The user is allowed to
            disable this if the intent is to define the elements
            client-side.

        If the contents of the visualization are not valid Vega, then a
        :class:`ValidationError` is raised.
        """
        super(self.__class__, self).validate()
        required_attribs = ('data', 'scales', 'axes', 'marks')
        for elem in required_attribs:
            attr = getattr(self, elem)
            if attr:
                # Validate each element of the sets of data, etc
                for entry in attr:
                    entry.validate()
                names = [a.name for a in attr]
                if len(names) != len(set(names)):
                    raise ValidationError(elem + ' has duplicate names')
            elif require_all:
                raise ValidationError(
                    elem + ' must be defined for valid visualization')

    def _repr_html_(self):
        """Build the HTML representation for IPython."""
        vis_id = str(uuid4()).replace("-", "")
        html = """<div id="vis%s"></div>
<script>
   ( function() {
     var _do_plot = function() {
       if (typeof vg === 'undefined') {
         window.addEventListener('vincent_libs_loaded', _do_plot)
         return;
       }
       vg.parse.spec(%s, function(chart) {
         chart({el: "#vis%s"}).update();
       });
     };
     _do_plot();
   })();
</script>
<style>.vega canvas {width: 100%%;}</style>
        """ % (vis_id, self.to_json(pretty_print=False), vis_id)
        return html

    def display(self):
        """Display the visualization inline in the IPython notebook.

        This is deprecated, use the following instead::

            from IPython.display import display
            display(viz)
        """
        from IPython.core.display import display, HTML
        display(HTML(self._repr_html_()))
