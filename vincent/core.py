# -*- coding: utf-8 -*-
import json
import time

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None


def _assert_is_type(name, value, value_type):
    """Assert that a value must be a given type."""
    if not isinstance(value, value_type):
        if type(value_type) is tuple:
            raise TypeError(name + ' must be one of (' +
                            ', '.join(t.__name__ for t in value_type) + ')')
        else:
            raise TypeError(name + ' must be ' + value_type.__name__)


def field_property(field_type=None, field_name=None):
    """Decorator to define properties that map to the internal `_field`
    dict.

    The argument is a "validator" function that should return no value but
    raise an exception if the provided value is not valid Vega. If the
    validator throws no exception, then the value is assigned to the
    `_field` dict using the validator function name as the key.

    The validator function should take only one argument, so that no `self`
    argument is included - the validator should not modify the class.

    The docstring for the property is taken from the validator's docstring.

    The decorator takes an optional string argument, which will be used as
    the key for the internal `_field` dict. This can be useful if the
    property name conflicts with a Python keyword.
    """
    def field_property_creator(validator, name):
        def setter(self, value):
            if isinstance(field_type, (type, tuple)):
                _assert_is_type(validator.__name__, value, field_type)
            validator(value)
            self._field[name] = value

        def getter(self):
            return self._field.get(name, None)

        def deleter(self):
            if name in self._field:
                del self._field[name]

        return property(getter, setter, deleter, validator.__doc__)

    if isinstance(field_type, (type, tuple)):
        # If field_type is a type, return another decorator.
        def field_property_dec(validator):
            # Make sure to use the field name if it's there.
            if field_name:
                return field_property_creator(validator, field_name)
            else:
                return field_property_creator(validator, validator.__name__)
        return field_property_dec
    elif isinstance(field_name, str):
        # If field_name is a string, use that name and return another
        # decorator.
        def field_property_dec(validator):
            return field_property_creator(validator, field_name)
        return field_property_dec
    else:
        # Otherwise we assume that field_type is actually the function being
        # decorated.
        return field_property_creator(field_type, field_type.__name__)


class FieldClass(object):
    """Base class for objects that rely on an internal `_field` dict
    """
    def __init__(self, **kwargs):
        """Initialize a FieldClass

        **kwargs are attribute-value pairs that are set on initialization.
        """
        self._field = {}

        for attr, value in kwargs.iteritems():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise ValueError('unknown keyword argument ' + attr)

    def validate(self):
        """Validate the contents of the object.

        This calls `setattr` for each attribute that has been set.
        """
        for key, val in self._field.iteritems():
            setattr(self, key, val)

    def to_json(self, validate=True):
        """Convert object to JSON

        Parameters
        ----------
        validate : boolean
            If True (default), call the object's `validate` method before
            serializing.
        """
        if validate:
            self.validate()

        return json.dumps(self._field)

    def from_json(self):
        """Load object from JSON
        """
        raise NotImplementedError()


class Vis(FieldClass):
    """Visualization container class.

    This class defines an entire visualization.
    """
    @field_property(str)
    def name(value):
        """string : Name of the visualization (optional)
        """

    @field_property(int)
    def width(value):
        """int : Width of the visualization in pixels

        Default is 500 if undefined.
        """
        if value < 0:
            raise ValueError('width cannot be negative')

    @field_property(int)
    def height(value):
        """int : Height of the visualization in pixels

        Default is 500 if undefined.
        """
        if value < 0:
            raise ValueError('height cannot be negative')

    @field_property(list)
    def viewport(value):
        """2-element list of ints : Dimensions of the viewport

        The viewport is a bounding box containing the visualization. If the
        dimensions are smaller than the height and/or width, the
        visualization will pan within the viewport's box.

        Default is visualization width and height if undefined.
        """
        if len(value) != 2:
            raise ValueError('viewport must have 2 dimensions')
        for v in value:
            _assert_is_type('viewport dimension', v, int)

    @field_property((int, dict))
    def padding(value):
        """int or dict : Padding around visualization

        The padding defines the distance between the edge of the
        visualization canvas to the visualization box. It does not count as
        part of the visualization width/height.

        If a dict, padding must have all keys 'top', 'left', 'right',
        'bottom' with int values.
        """
        if isinstance(value, dict):
            required_keys = ['top', 'left', 'right', 'bottom']
            for key in required_keys:
                if key not in value:
                    raise ValueError('padding must have keys %s' %
                                     ', '.join(required_keys))
                _assert_is_type('padding: %s' % key, value[key], int)
                if value[key] < 0:
                    raise ValueError('padding cannot be negative')
        else:
            if value < 0:
                raise ValueError('padding cannot be negative')

    @field_property(list)
    def data(value):
        """list with elements of `Data` : Data definitions
        """
        for i, entry in enumerate(value):
            _assert_is_type('data[%g]' % i, entry,  Data)

    @field_property(list)
    def scales(value):
        """list with elements of `Scale` or dict : Scale definitions
        """
        for i, entry in enumerate(value):
            _assert_is_type('scales[%g]' % i, entry, (dict, Scale))

    @field_property(list)
    def axes(value):
        """list of `Axis` : Axis definitions
        """

    @field_property(list)
    def marks(value):
        """list of `Mark` : Mark definitions
        """

    def validate(self):
        """Validate the visualization contents.
        """
        super(self.__class__, self).validate()
        for elem in (self.data + self.scales + self.axes + self.marks):
            elem.validate()

    def load_pandas(self, pd_obj, name=None, append=False):
        if not append:
            self.data = []
            self._table_idx = 1

        if not (name or hasattr(pd_obj, 'name')):
            name = 'table%g' % self._table_idx
            self._table_idx += 1

        self.data.append(Data.from_pandas(pd_obj, name=name))


class LoadError(Exception):
    """Exception for errors on loading data from third-party objects"""
    pass


class Data(FieldClass):
    _default_index_key = '_index'

    def __init__(self, name, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.name = name

    @field_property(str)
    def name(value):
        """string : Name of the data

        This is used by other components (`Mark`, etc.) for reference.
        """

    @field_property(str)
    def url(value):
        """string : URL from which to load the data

        This can be used as an alternative to defining the data in the
        ``values`` attribute.
        """

    @field_property(list)
    def values(value):
        """list : Data contents

        Data is represented in tabular form, where each element of
        ``values`` corresponds to a row of data.  Each row of data is
        represented by a dict or a raw number. The keys of the dict are
        columns and the values are individual data points. The keys of the
        dicts must be strings for the data to correctly serialize to JSON.

        The data will often have an "index" column representing the
        independent variable, with the remaining columns representing the
        dependent variables, though this is not required. The ``Data`` class
        itself, however, is agnostic to which columns are dependent and
        independent.

        For example, the values attribute
        ``[{'x': 0, 'y': 3.2}, {'x': 1, 'y': 1.3}]``
        could represent two rows of two variables - possibly an independent
        variable ``'x'`` and a dependent variable ``'y'``.
        For simple data sets, an alternative values attribute could be a
        simple list of numbers such as
        ``[2, 12, 3, 5]``.

        It may be more convenient to load data from pandas or NumPy objects.
        See the methods :func:`Data.from_pandas` and
        :func:`Data.from_numpy`.
        """
        for row in value:
            _assert_is_type('values row', row, (float, int, dict))

    @field_property(str)
    def source(value):
        """string : ``name`` field of another data set

        This is typically used with data transforms to create new data
        values.
        """

    @field_property(list)
    def transform(value):
        """list : transforms to apply to the data

        Note: Transform-relational classes are not yet implemented.
        """

    @field_property(dict)
    def format(value):
        """dict : information about the data format

        This is only used when loading data from the ``url`` attribute.
        Format-relational classes are not yet implemented.
        """

    @staticmethod
    def serialize(obj):
        """Convert an object into a JSON-serializable value

        This is used by the ``from_pandas`` and ``from_numpy`` functions to
        convert data to JSON-serializable types when loading.
        """
        if isinstance(obj, str):
            return obj
        elif hasattr(obj, 'timetuple'):
            return int(time.mktime(obj.timetuple())) * 1000
        elif hasattr(obj, 'item'):
            return obj.item()
        elif hasattr(obj, '__float__'):
            return float(obj)
        elif hasattr(obj, '__int__'):
            return int(obj)
        else:
            raise LoadError('cannot serialize index of type '
                            + type(obj).__name__)

    @classmethod
    def from_pandas(cls, pd_obj, name=None, index_key=None, data_key=None,
                    **kwargs):
        """Load values from a pandas ``Series`` or ``DataFrame`` object

        Parameters
        ----------
        pd_obj : pandas ``Series`` or ``DataFrame``
            Pandas object to import data from.
        name : string
            Applies to the ``name`` attribute of the generated class. If
            ``None`` (default), then the ``name`` attribute of ``pd_obj`` is
            used if it exists, or ``'table'`` if it doesn't.
        index_key : string
            In each :class:`dict` entry of the ``values`` attribute, the
            index of the pandas object will have this key. If ``None``
            (default), then ``_index`` is used.
        data_key : string
            Applies only to ``Series``. If ``None`` (default), then the data is
            indexed by the ``name`` attribute of the generated class.
            Otherwise, the data will be indexed by this key. For example, if
            ``data_key`` is ``'x'``, then the entries of the ``values`` list
            will be ``{'_index': ..., 'x': ...}``.
        **kwargs : dict
            Additional arguments passed to the :class:`Data` constructor.
        """
        # Note: There's an experimental JSON encoder floating around in
        # pandas land that hasn't made it into the main branch. This
        # function should be revisited if it ever does.
        if not pd:
            raise LoadError('pandas could not be imported')

        if name:
            data = cls(name=name, **kwargs)
        elif hasattr(pd_obj, 'name') and pd_obj.name:
            data = cls(name=pd_obj.name, **kwargs)
        else:
            data = cls(name='table', **kwargs)

        index_key = index_key or cls._default_index_key

        if isinstance(pd_obj, pd.Series):
            data_key = data_key or data.name
            data.values = [
                dict([(index_key, cls.serialize(i))] +
                     [(data_key, cls.serialize(v))])
                for i, v in pd_obj.iterkv()]
        elif isinstance(pd_obj, pd.DataFrame):
            # We have to explicitly convert the column names to strings
            # because the json serializer doesn't allow for integer keys.
            data.values = [
                dict([(index_key, cls.serialize(i))] +
                     [(str(k), cls.serialize(v)) for k, v in row.iterkv()])
                for i, row in pd_obj.iterrows()]
        else:
            raise ValueError('cannot load from data type '
                             + type(pd_obj).__name__)
        return data

    @classmethod
    def from_numpy(cls, np_obj, name, columns, index=None, index_key=None,
                   **kwargs):
        """Load values from a numpy array

        Parameters
        ----------
        np_obj : numpy.ndarray
            numpy array to load data from
        name : string
            ``name`` field for the data
        columns : iterable
            Sequence of column names, from left to right. Must have same
            length as the number of columns of ``np_obj``.
        index : iterable
            Sequence of indices from top to bottom. If ``None`` (default),
            then the indices are integers starting at 0. Must have same
            length as the number of rows of ``np_obj``.
        index_key : string
            Key to use for the index. If ``None`` (default), ``_index`` is
            used.
        **kwargs : dict
            Additional arguments passed to the :class:`Data` constructor

        Notes
        -----
        The individual elements of ``np_obj``, ``columns``, and ``index``
        must return valid values from :func:`Data.serialize`.

        Raises
        ------
        LoadError : if numpy could not be imported or dimensions of
        arguments do not agree
        TypeError : if ``np_obj`` is not an instance of ``ndarray``
        """
        if not np:
            raise LoadError('numpy could not be imported')
        _assert_is_type('numpy object', np_obj, np.ndarray)

        # Integer index if none is provided
        index = index or range(np_obj.shape[0])
        # Explicitly map dict-keys to strings for JSON serializer.
        columns = map(str, columns)

        index_key = index_key or cls._default_index_key

        if len(index) != np_obj.shape[0]:
            raise LoadError(
                'length of index must be equal to number of rows of array')
        elif len(columns) != np_obj.shape[1]:
            raise LoadError(
                'length of columns must be equal to number of columns of '
                'array')

        data = cls(name=name, **kwargs)
        data.values = [
            dict([(index_key, cls.serialize(idx))] +
                 [(col, x) for col, x in zip(columns, row)])
            for idx, row in zip(index, np_obj.tolist())]

        return data

    def to_json(self, data_path=None):
        """Convert data to JSON

        Parameters
        ----------
        data_path : string
            If not None, then data is written to a separate file at the
            specified path. Note that the `url` attribute must be set
            independently.

        Returns
        -------
        vega_json : string
            Valid Vega JSON.
        """
        #TODO: support writing to separate file
        return json.dumps(self._field)


class ValueRef(FieldClass):
    """Define values for Mark properties
    """
    @field_property((str, int, float))
    def value(value):
        """number or string, used for constant values

        This is ignored if the `field` property is defined.
        """

    @field_property(str)
    def field(value):
        """string, references field of the data in dot-notation

        The data is taken from the Mark's `from_` property. For instance, if
        the data has a definition

            [{'x': 2}, {'x': 3}, {'x': 1}]

        then the data should be referenced as `data.x`. Note that the first
        element is always `data` regardless of the name of the data.
        """

    @field_property(str)
    def scale(value):
        """string, references the name of a `Scale`

        The scale is applied to the `value` and `field` attributes.
        """

    @field_property((int, float))
    def mult(value):
        """number, multiplier applied to the data after any scaling
        """

    @field_property((int, float))
    def offset(value):
        """number, additive offset applied to the data after any scaling and
        multipliers
        """

    @field_property(bool)
    def band(value):
        """boolean, use the range of the scale if applicable

        If this is True and `scale` is defined, then the value referenced
        is the range band referenced scale. See the d3 documentation on
        `ordinal.rangeBand` for more info.
        """


class MarkPropertySet(FieldClass):
    """Define a set of properties for `Mark` objects"""

    # This is only imported as Mark.PropertySet, so this is a bit of a hack
    # to make TypeError messages more useful.
    __name__ = 'Mark.PropertySet'

    @field_property(ValueRef)
    def x(value):
        """ValueRef - number, left-most x-coordinate

        For most marks, this will be equal to the field of the independent
        variable. For example,

            {"scale": "x", "field": "data.x"}

        will place a mark with its left-most coordinate at the x-values of
        the data. Something like

            {"scale": "x", "value": 10}

        will place a single mark at given x-coordinate.
        """

    @field_property(ValueRef)
    def x2(value):
        """ValueRef - number, right-most x-coordinate

        Generally, for marks where the width is significant, it's better to
        use the `width` property.
        """

    @field_property(ValueRef)
    def width(value):
        """ValueRef - number, width of the mark

        Set the `band` property of the `ValueRef` to True to use the full
        width.
        """

    @field_property(ValueRef)
    def y(value):
        """ValueRef - number, top-most y-coordinate

        The same remarks for the `x` property are valid here.
        """

    @field_property(ValueRef)
    def y2(value):
        """ValueRef - number, bottom-most y-coordinate

        The same remarks for the `x2` property are valid here.
        """

    @field_property(ValueRef)
    def height(value):
        """ValueRef - number, height of the mark
        """

    @field_property(ValueRef)
    def opacity(value):
        """ValueRef - number, overall opacity (0 to 1)
        """

    @field_property(ValueRef)
    def fill(value):
        """ValueRef - color, fill color for the mark
        """

    @field_property(field_type=ValueRef, field_name='fillOpacity')
    def fill_opacity(value):
        """ValueRef - number, opacity of the fill (0 to 1)
        """

    @field_property(ValueRef)
    def stroke(value):
        """ValueRef - color, stroke color for the mark
        """

    @field_property(field_type=ValueRef, field_name='strokeWidth')
    def stroke_width(value):
        """ValueRef - number, width of the stroke in pixels
        """

    @field_property(field_type=ValueRef, field_name='strokeOpacity')
    def stroke_opacity(value):
        """ValueRef - number, opacity of the stroke (0 to 1)
        """

    @field_property(ValueRef)
    def size(value):
        """ValueRef - number, area of the mark in pixels

        This is the total area of a symbol. For example, a value of 500
        and a `shape` of `'circle'` would result in circles with an area of
        500 square pixels. Only used if `type` is `'symbol'`.
        """

    @field_property(ValueRef)
    def shape(value):
        """ValueRef - string, type of symbol to use

        Possible values are `'circle'` (default), `'square'`, `'cross'`,
        `'diamond'`, `'triangle-up'`, and `'triangle-down'`. Only used if
        `type` is `'symbol'`.
        """

    @field_property(ValueRef)
    def path(value):
        """ValueRef - string, SVG path string

        This would typically be used for maps and other things where the
        path is taken from the data.
        """

    @field_property(field_type=ValueRef, field_name='innerRadius')
    def inner_radius(value):
        """ValueRef - number, inner radius of arc in pixels

        Only used if `type` is `'arc'`."""

    @field_property(field_type=ValueRef, field_name='outerRadius')
    def outer_radius(value):
        """ValueRef - number, outer radius of the arc in pixels

        Only used if `type` is `'arc'`."""

    @field_property(field_type=ValueRef, field_name='startAngle')
    def start_angle(value):
        """ValueRef - number, start angle of the arc in radians

        Only used if `type` is `'arc'`."""

    @field_property(field_type=ValueRef, field_name='endAngle')
    def end_angle(value):
        """ValueRef - number, end angle of the arc in radians

        Only used if `type` is `'arc'`."""

    @field_property(ValueRef)
    def interpolate(value):
        """ValueRef - string, line interpolation method to use

        Possible values for `area` types are `'linear'`,
        `'step-before'`, `'step-after'`, `'basis'`, `'basis-open'`,
        `'cardinal'`, `'cardinal-open'`, `'monotone'`. `line` types
        have all values for `area` as well as `'basis-closed'`,
        `'bundle'`, and `'cardinal-closed'`.

        Only used if `type` is `'area'` or `'line'`."""
        #TODO check values

    @field_property(ValueRef)
    def tension(value):
        """ValueRef - number, tension used for interpolation

        Only used if `type` is `'area'` or `'line'`."""

    @field_property(ValueRef)
    def url(value):
        """ValueRef - string, url of image

        Only used if `type` is `'image'`."""

    @field_property(ValueRef)
    def align(value):
        """ValueRef - string, horizontal alignment of mark

        Possible values are `'left'`, `'right'`, and `'center'`. Only
        used if `type` is `'image'` or `'text'`."""
        #TODO check values

    @field_property(ValueRef)
    def baseline(value):
        """ValueRef - string, vertical alignment of mark

        Possible values are `'top'`, `'middle'`, and `'bottom'`. Only
        used if `type` is `'image'` or `'text'`."""
        #TODO check values

    @field_property(ValueRef)
    def text(value):
        """ValueRef - string, text to display

        Only used if `type` is `'text'`."""

    @field_property(ValueRef)
    def dx(value):
        """ValueRef - number, horizontal margin between text and anchor
        point in pixels

        Ignored if `align` is `'center'`. Only used if `type` is
        `'text'`."""

    @field_property(ValueRef)
    def dy(value):
        """ValueRef - number, vertical margin between text and anchor
        point in pixels

        Ignored if `baseline` is `'middle'`. Only used if `type` is
        `'text'`."""

    @field_property(ValueRef)
    def angle(value):
        """ValueRef - number, rotation of text in degrees

        Only used if `type` is `'text'`."""

    @field_property(ValueRef)
    def font(value):
        """ValueRef - string, typeface for text

        Only used if `type` is `'text'`."""

    @field_property(field_type=ValueRef, field_name='fontSize')
    def font_size(value):
        """ValueRef - number, font size in pixels

        Only used if `type` is `'text'`."""

    @field_property(field_type=ValueRef, field_name='fontWeight')
    def font_weight(value):
        """ValueRef - string, font weight

        Should be a valid SVG font weight. Only used if `type` is
        `'text'`."""

    @field_property(field_type=ValueRef, field_name='fontStyle')
    def font_style(value):
        """ValueRef - string, font style

        Should be a valid SVG font style. Only used if `type` is
        `'text'`."""


class Mark(FieldClass):

    PropertySet = MarkPropertySet

    class Properties(FieldClass):
        @field_property(MarkPropertySet)
        def enter(value):
            """PropertySet, properties applied when data is loaded
            """

        @field_property(MarkPropertySet)
        def exit(value):
            """PropertySet, properties applied when data is removed
            """

        @field_property(MarkPropertySet)
        def update(value):
            """PropertySet, properties applied for all non-exiting data

            (This is vague. Need better Vega docs.)
            """

        @field_property(MarkPropertySet)
        def hover(value):
            """PropertySet, properties applied on mouse-over

            On mouse out, the `update` properties are applied.
            """

    _valid_type_values = [
        'rect', 'symbol', 'path', 'arc', 'area', 'line', 'image', 'text']

    @field_property(str)
    def name(value):
        """name"""

    @field_property
    def description(value):
        _assert_is_type('description', value, str)

    @field_property
    def type(value):
        _assert_is_type('type', value, str)
        if value not in Mark._valid_type_values:
            raise ValueError(
                'invalid mark type %s, valid types are %s' % (
                    value, Mark._valid_type_values))

    @field_property(field_name='from')
    def from_(value):
        """dict : Description of data to visualize

        Note that although the property has the name `from_` (using `from`
        is invalid Python syntax), the JSON will contain the correct
        property `from`.
        """
        _assert_is_type('from_', value, dict)

    @field_property
    def properties(value):
        _assert_is_type('properties', value, Mark.Properties)

    @field_property
    def key(value):
        _assert_is_type('key', value, str)

    @field_property
    def delay(value):
        _assert_is_type('delay', value, dict)

    @field_property
    def ease(value):
        _assert_is_type('ease', value, str)


class DataRef(FieldClass):
    @field_property(str)
    def data(value):
        """string : Name of data-set containing the domain values"""

    @field_property((list, str))
    def field(value):
        """string or list of strings : Reference to desired data field(s)

        If multiple fields are given, then the values of all fields are
        included in the domain.
        """


class Scale(FieldClass):
    @field_property(str)
    def name(value):
        """string : Unique name for the scale

        This is used for referencing by other components (mainly ``Mark``).
        """

    @field_property(str)
    def type(value):
        """string : Type of the scale

        Valid types are as follows:

        * ``'ordinal'``: ordinal scale types
        * ``'time'`` or ``'utc'``: time scale types
        * ``'linear'``, ``'log'``, ``'pow'``, ``'sqrt'``, ``'quantile'``,
          ``'quantize'``, and ``'threshold'``: quantitative scale types

        For time scales, the value should be a Javascript-style numeric
        value of seconds.  ``'time'`` implies the value is in local time.

        If unspecified, then the scale is assumed to be linear. See the d3
        documentation for scale type details.
        """

    @field_property((list, DataRef))
    def domain(value):
        """list or DataRef : Domain of the scale
        """

    @field_property(field_type=(float, int, DataRef), field_name='domainMin')
    def domain_min(value):
        """float, int, or DataRef : Minimum domain value

        Only used for quantitative/time scales. This takes precedence over
        the minimum of the ``domain`` property.
        """

    @field_property(field_type=(float, int, DataRef),
                    field_name='domainMax')
    def domain_max(value):
        """float, int, or DataRef : Maximum domain value

        Only used for quantitative/time scales. This takes precedence over
        the maximum of the ``domain`` property.
        """

    @field_property((list, str))
    def range(value):
        """list or string : Range of the scale

        For quantitative scales, the range may be specified as a two-element
        list of min/max values. For ordinal scales, the range should be a
        list of output values mapped to the input values.

        String values may be used to automatically set a range:
            - ``'width'``: Set the range to the width of the visualization
            - ``'height'``: Set the range to the height of the visualization
            - ``'shapes'``: Equivalent to the symbol types:
                ``["circle", "cross", "diamond", "square", "triangle-down",
                "triangle-up"]``
            - ``'category10'``: A pre-determined 10-color pallet
            - ``'category20'``: A pre-determined 20-color pallet
        """

    @field_property(field_type=(float, int, DataRef), field_name='rangeMin')
    def range_min(value):
        """float, int, or DataRef : Minimum range value

        Only used for quantitative/time scales. This takes precedence over
        the minimum of the ``range`` property.
        """

    @field_property(field_type=(float, int, DataRef), field_name='rangeMax')
    def range_max(value):
        """float, int, or DataRef : Maximum range value

        Only used for quantitative/time scales. This takes precedence over
        the maximum of the ``range`` property.
        """

    @field_property(bool)
    def reverse(value):
        """boolean : If True, flip the scale range"""

    @field_property(bool)
    def round(value):
        """boolean : If True, numeric output values are rounded to
        integers"""

    @field_property(bool)
    def points(value):
        """boolean : If True, distribute ordinal values over evenly spaced
        points between ``range_min`` and ``range_max``

        Ignored for non-ordinal scales.
        """

    @field_property(bool)
    def clamp(value):
        """boolean : If True, values that exceed the domain are clamped to
        within the domain

        Ignored for ordinal scales.
        """

    @field_property((bool, str))
    def nice(value):
        """boolean or string : scale the domain to a more human-friendly set

        If the scale ``type`` is ``'time'`` or ``'utc'``, then the value
        should be one of ``'second'``, ``'minute'``, ``'hour'``, ``'day'``,
        ``'week'``, ``'month'``, or ``'year'``.

        If the scale ``type`` is a quantitative scale, then the value should
        be a boolean. The input values are rounded to a more human-friendly
        value. The details of the rounding are in the d3 documentation.

        Ignored for ordinal scales.
        """

    @field_property((float, int))
    def exponent(value):
        """float or int : Exponent for ``'pow'`` scale types

        Ignored for all scale types other than ``'pow'``.
        """

    @field_property(bool)
    def zero(value):
        """boolean : If True, include zero in the domain

        Only valid for quantitative scale types. This is useful if the
        domain is defined as a DataRef that may not include 0 exactly.
        """


class Axis(FieldClass):
    @field_property(str)
    def type(value):
        """string : Type of axis - `'x'` or `'y'`"""
        if value not in ('x', 'y'):
            raise ValueError('Axis.type must be "x" or "y"')

    @field_property(str)
    def scale(value):
        """string : Name of scale used for axis"""

    @field_property(str)
    def orient(value):
        """string : Orientation of the axis

        Should be one of `'top'`, `'bottom'`, `'left'`, or `'right'`.
        """

    @field_property(str)
    def format(value):
        """string : Formatting to use for axis labels

        See d3's formatting documentation for format pattern.
        """
