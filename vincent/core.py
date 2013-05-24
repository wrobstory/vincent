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


def field_property(arg):
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
    def _field_property_creator(validator, name):
        def setter(self, value):
            validator(value)
            self._field[name] = value

        def getter(self):
            return self._field.get(name, None)

        def deleter(self):
            if name in self._field:
                del self._field[name]

        return property(getter, setter, deleter, validator.__doc__)

    if isinstance(arg, str):
        def field_property(validator):
            return _field_property_creator(validator, arg)
        return field_property
    else:
        # Assume the argument is a function.
        return _field_property_creator(arg, arg.__name__)


class FieldClass(object):
    """Base class for objects that rely on an internal `_field` dict.
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
    @field_property
    def name(value):
        """string : Name of the visualization (optional)
        """
        _assert_is_type('name', value, str)

    @field_property
    def width(value):
        """int : Width of the visualization in pixels

        Default is 500 if undefined.
        """
        _assert_is_type('width', value, int)

    @field_property
    def height(value):
        """int : Height of the visualization in pixels

        Default is 500 if undefined.
        """
        _assert_is_type('height', value, int)

    @field_property
    def viewport(value):
        """2-element list of ints : Dimensions of the viewport

        The viewport is a bounding box containing the visualization. If the
        dimensions are smaller than the height and/or width, the
        visualization will pan within the viewport's box.

        Default is visualization width and height if undefined.
        """
        _assert_is_type('viewport', value, list)
        if len(value) != 2:
            raise ValueError('viewport must have 2 dimensions')
        for v in value:
            _assert_is_type('viewport dimension', v, int)

    @field_property
    def padding(value):
        """int or dict : Padding around visualization

        The padding defines the distance between the edge of the
        visualization canvas to the visualization box. It does not count as
        part of the visualization width/height.

        If a dict, padding must have all keys 'top', 'left', 'right',
        'bottom' with int values.
        """
        _assert_is_type('padding', value, (int, dict))
        if isinstance(value, dict):
            required_keys = ['top', 'left', 'right', 'bottom']
            for key in required_keys:
                if key not in value:
                    raise ValueError('padding must have keys %s' %
                                     ', '.join(required_keys))
                _assert_is_type('padding: %s' % key, value[key], int)

    @field_property
    def data(value):
        """list with elements of `Data` : Data definitions
        """
        _assert_is_type('data', value, list)
        for i, entry in enumerate(value):
            _assert_is_type('data[%g]' % i, entry,  Data)

    @field_property
    def scales(value):
        """list with elements of `Scale` or dict : Scale definitions
        """
        _assert_is_type('scales', value, list)
        for i, entry in enumerate(value):
            _assert_is_type('scales[%g]' % i, entry, (dict, Scale))

    @field_property
    def axes(value):
        """list of `Axis` : Axis definitions
        """
        _assert_is_type('axes', value, list)

    @field_property
    def marks(value):
        """list of `Mark` : Mark definitions
        """
        _assert_is_type('marks', value, list)

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

    @field_property
    def name(value):
        """String containing the name of the data. This is used by other
        components (marks, etc.) for reference.
        """
        _assert_is_type('name', value, str)

    @field_property
    def url(value):
        """String containing URL from which to load the data. This can be
        used as an alternative to defining the data in the `values`
        attribute.
        """
        _assert_is_type('url', value, str)

    @field_property
    def values(value):
        """List containing data.

        Data is represented in tabular form, where each element of `values`
        corresponds to a "row" of data.  Each row of data is represented by
        a dict or a raw number. The keys of the dict are columns and the
        values are individual data points. The keys of the dicts must be
        strings for the data to correctly serialize to JSON.

        The data will often have an `index` column representing the
        independent variable, with the remaining columns representing the
        dependent variables, though this is not required. The `Data` class
        itself, however, is agnostic to which columns are dependent and
        independent.

        For example, the values attribute

            [{'x': 0, 'y': 3.2}, {'x': 1, 'y': 1.3}]

        could represent two rows of two variables - possibly an independent
        variable 'x' and a dependent variable 'y'.

        For simple data sets, an alternative values attribute could be a
        simple list of numbers:

            [2, 12, 3, 5]

        It may be more convenient to load data from pandas or NumPy objects.
        See the functions `Data.from_pandas` and `Data.from_numpy`.
        """
        _assert_is_type('values', value, list)
        for row in value:
            _assert_is_type('values row', row, (float, int, dict))

    @field_property
    def source(value):
        """String containing the `name` of another data set to use for this
        data set. Typically used with data transforms.
        """
        _assert_is_type('source', value, str)

    @field_property
    def transform(value):
        """A list of possible transforms to apply to the data.

        Note: No additional validation is currently implemented.
        """
        _assert_is_type('transform', value, list)

    @field_property
    def format(value):
        """A dict containing information about the data format. Only used
        when loading data from a URL.

        Note: No additional validation is currently implemented.
        """
        _assert_is_type('format', value, dict)

    @staticmethod
    def serialize(obj):
        """Convert an object into a JSON-serializable value

        This is used by the `from_pandas` and `from_numpy` functions to
        convert data to JSON-serializable types when loading.
        """
        if isinstance(obj, str):
            return obj
        elif hasattr(obj, 'timetuple'):
            return int(time.mktime(obj.timetuple())) * 1000
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
        """Load values from a pandas Series or DataFrame

        Parameters
        ----------
        pd_obj : pandas Series or DataFrame
            Pandas object to import data from.
        name : string
            Applies to the `name` attribute of the generated class. If None
            (default), then `pd_obj` the `name` attribute is used if it
            exists, or 'table' if it doesn't.
        index_key : string
            In each dict entry of the `values` attribute, the index of the
            pandas object will have this key. If None, then `_index` is
            used.
        data_key : string
            Applies only to Series. If None (default), then the data is
            indexed by the `name` attribute of the generated class.
            Otherwise, the data will be indexed by this key. For example, if
            `data_key` is `x`, then the entries of the `values` list will be

                {'_index': ..., 'x': ...}

        **kwargs : dict
            Additional arguments passed to the `Data` constructor.
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
        """Load values from a NumPy array

        Parameters
        ----------
        np_obj : numpy.ndarray
            NumPy array to load data from.
        name : string
            `name` field of the data.
        columns : iterable
            Sequence of column names, from left to right. Must have same
            length as the number of columns of `np_obj`.
        index : iterable
            Sequence of indices from top to bottom. If None (default), then
            the indices are integers starting at 0. Must have same length as
            the number of rows of `np_obj`.
        index_key : string
            Key to use for the index. If None, `_index` is used.
        **kwargs : dict
            Additional arguments passed to the `Data` constructor.

        The individual elements of `np_obj`, `columns`, and `index` must
        return valid values from the `Data.serialize` function.
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


class Mark(FieldClass):

    class Properties(FieldClass):
        @field_property
        def x(value):
            _assert_is_type('x', value, ValueRef)

        @field_property
        def x2(value):
            _assert_is_type('x2', value, ValueRef)

        @field_property
        def width(value):
            _assert_is_type('width', value, ValueRef)

        @field_property
        def y(value):
            _assert_is_type('y', value, ValueRef)

        @field_property
        def y2(value):
            _assert_is_type('y2', value, ValueRef)

        @field_property
        def height(value):
            _assert_is_type('height', value, ValueRef)

        @field_property
        def opacity(value):
            _assert_is_type('opacity', value, ValueRef)

        @field_property
        def fill(value):
            _assert_is_type('fill', value, ValueRef)

        @field_property('fillOpacity')
        def fill_opacity(value):
            _assert_is_type('fill_opacity', value, ValueRef)

        @field_property
        def stroke(value):
            _assert_is_type('stroke', value, ValueRef)

        @field_property('strokeWidth')
        def stroke_width(value):
            _assert_is_type('stroke_width', value, ValueRef)

        @field_property('strokeOpacity')
        def stroke_opacity(value):
            _assert_is_type('stroke_opacity', value, ValueRef)

        @field_property
        def size(value):
            _assert_is_type('size', value, ValueRef)

        @field_property
        def shape(value):
            _assert_is_type('shape', value, ValueRef)

        @field_property
        def path(value):
            _assert_is_type('path', value, ValueRef)

        @field_property('innerRadius')
        def inner_radius(value):
            """ValueRef - number, inner radius of arc in pixels

            Only used if `type` is `'arc'`."""
            _assert_is_type('inner_radius', value, ValueRef)

        @field_property('outerRadius')
        def outer_radius(value):
            """ValueRef - number, outer radius of the arc in pixels

            Only used if `type` is `'arc'`."""
            _assert_is_type('outer_radius', value, ValueRef)

        @field_property('startAngle')
        def start_angle(value):
            """ValueRef - number, start angle of the arc in radians

            Only used if `type` is `'arc'`."""
            _assert_is_type('start_angle', value, ValueRef)

        @field_property('endAngle')
        def end_angle(value):
            """ValueRef - number, end angle of the arc in radians

            Only used if `type` is `'arc'`."""
            _assert_is_type('end_angle', value, ValueRef)

        @field_property
        def interpolate(value):
            """ValueRef - string, line interpolation method to use

            Possible values for `area` types are `'linear'`,
            `'step-before'`, `'step-after'`, `'basis'`, `'basis-open'`,
            `'cardinal'`, `'cardinal-open'`, `'monotone'`. `line` types
            have all values for `area` as well as `'basis-closed'`,
            `'bundle'`, and `'cardinal-closed'`.

            Only used if `type` is `'area'` or `'line'`."""
            _assert_is_type('interpolate', value, ValueRef)
            #TODO check values

        @field_property
        def tension(value):
            """ValueRef - number, tension used for interpolation

            Only used if `type` is `'area'` or `'line'`."""
            _assert_is_type('tension', value, ValueRef)

        @field_property
        def url(value):
            """ValueRef - string, url of image

            Only used if `type` is `'image'`."""
            _assert_is_type('url', value, ValueRef)

        @field_property
        def align(value):
            """ValueRef - string, horizontal alignment of mark

            Possible values are `'left'`, `'right'`, and `'center'`. Only
            used if `type` is `'image'` or `'text'`."""
            _assert_is_type('align', value, ValueRef)
            #TODO check values

        @field_property
        def baseline(value):
            """ValueRef - string, vertical alignment of mark

            Possible values are `'top'`, `'middle'`, and `'bottom'`. Only
            used if `type` is `'image'` or `'text'`."""
            _assert_is_type('baseline', value, ValueRef)
            #TODO check values

        @field_property
        def text(value):
            """ValueRef - string, text to display

            Only used if `type` is `'text'`."""
            _assert_is_type('text', value, ValueRef)

        @field_property
        def dx(value):
            """ValueRef - number, horizontal margin between text and anchor
            point in pixels

            Ignored if `align` is `'center'`. Only used if `type` is
            `'text'`."""
            _assert_is_type('dx', value, ValueRef)

        @field_property
        def dy(value):
            """ValueRef - number, vertical margin between text and anchor
            point in pixels

            Ignored if `baseline` is `'middle'`. Only used if `type` is
            `'text'`."""
            _assert_is_type('dy', value, ValueRef)

        @field_property
        def angle(value):
            """ValueRef - number, rotation of text in degrees

            Only used if `type` is `'text'`."""
            _assert_is_type('angle', value, ValueRef)

        @field_property
        def font(value):
            """ValueRef - string, typeface for text

            Only used if `type` is `'text'`."""
            _assert_is_type('font', value, ValueRef)

        @field_property('fontSize')
        def font_size(value):
            """ValueRef - number, font size in pixels

            Only used if `type` is `'text'`."""
            _assert_is_type('font_size', value, ValueRef)

        @field_property('fontWeight')
        def font_weight(value):
            """ValueRef - string, font weight

            Should be a valid SVG font weight. Only used if `type` is
            `'text'`."""
            _assert_is_type('font_weight', value, ValueRef)

        @field_property('fontStyle')
        def font_style(value):
            """ValueRef - string, font style

            Should be a valid SVG font style. Only used if `type` is
            `'text'`."""
            _assert_is_type('font_style', value, ValueRef)

    _valid_type_values = [
        'rect', 'symbol', 'path', 'arc', 'area', 'line', 'image', 'text']

    @field_property
    def name(value):
        _assert_is_type('name', value, str)

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

    @field_property('from')
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


class ValueRef(FieldClass):
    @field_property
    def value(value):
        _assert_is_type('value', value, (str, int, float))

    @field_property
    def field(value):
        _assert_is_type('field', value, str)

    @field_property
    def scale(value):
        _assert_is_type('scale', value, str)

    @field_property
    def mult(value):
        _assert_is_type('mult', value, (int, float))

    @field_property
    def offset(value):
        _assert_is_type('offset', value, (int, float))

    @field_property
    def band(value):
        _assert_is_type('band', value, bool)


class Scale(FieldClass):
    pass
