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
    """Decorator to define properties that map to the internal ``_field``
    dict

    This decorator is intended for classes that map to some pre-defined JSON
    structure. It is assumed that this decorates functions with an instance
    of ``self._field``.

    Parameters
    ----------
    field_type : type or tuple of types
        If the argument to the decorated function is not of the given types,
        then a ValueError is raised. No type checking is done if the type is
        None (default).
    field_name : string
        An optional name to map to the internal ``_field`` dict. If None
        (default), then the key for the dict is the name of the function
        being decorated. If not None, then it will be the name specified
        here. This is useful if the expected JSON field name is a Python
        keyword or has an un-Pythonic name.

    This should decorate a "validator" function that should return no value
    but raise an exception if the provided value is not valid Vega. If the
    validator throws no exception, then the value is assigned to the
    ``_field`` dict.

    The validator function should take only one argument - the value to be
    validated - so that no ``self`` argument is included; the validator
    should not modify the class.

    If no arguments are given, then no type-checking is done the property
    will be mapped to a field with the name of the decorated function.

    The doc string for the property is taken from the validator functions's
    doc string.
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


class ValidationError(Exception):
    """Exception raised with validation fails

    This exception is raised only when the ``validate`` functions of classes
    that inherit from ``FieldClass`` are called. It implies that the classes
    do not contain valid Vega JSON."""
    pass


class FieldClass(object):
    """Base class for objects that rely on an internal ``_field`` dict

    This should be used as a superclass for classes that map to some JSON
    structure. The JSON content is stored in an internal dict named
    ``_field``.
    """
    def __init__(self, **kwargs):
        """Initialize a FieldClass

        **kwargs are attribute-value pairs that are set on initialization.
        These will generally be keys for the ``_field`` dict. If the
        attribute does not already exist as a property, then a
        ``ValueError`` is raised.
        """
        self._field = {}

        for attr, value in kwargs.iteritems():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise ValueError('unknown keyword argument ' + attr)

    def validate(self):
        """Validate the contents of the object.

        This calls ``setattr`` for each of the class's field properties. It
        will catch ``ValueError``s raised by the field property's setters
        and re-raise them as :class:`ValidationError`.
        """
        for key, val in self._field.iteritems():
            try:
                setattr(self, key, val)
            except ValueError as e:
                raise ValidationError('invalid contents: ' + e.message)

    def to_json(self, validate=False, pretty_print=True):
        """Convert object to JSON

        Parameters
        ----------
        validate : boolean
            If True, call the object's `validate` method before
            serializing. Default is False.
        pretty_print : boolean
            If True (default), JSON is printed in more-readable form with
            indentation and spaces.

        Returns
        -------
        string
            JSON serialization of the class's field properties.
        """
        if validate:
            self.validate()

        if pretty_print:
            dumps_args = {'indent': 4, 'separators': (',', ': ')}
        else:
            dumps_args = {}

        return json.dumps(self._field, **dumps_args)

    def from_json(self):
        """Load object from JSON

        Not yet implemented.
        """
        raise NotImplementedError()


class KeyedList(list):
    """A list that can optionally be indexed by the ``name`` attribute of
    its elements"""
    def __getitem__(self, item):
        if isinstance(item, str):
            names = [x.name for x in self]
            if len(names) != len(set(names)):
                raise ValidationError('duplicate names in list')
            elif item not in names:
                raise KeyError('invalid name %s' % item)
            else:
                return self[names.index(item)]
        else:
            return list.__getitem__(self, item)


class Visualization(FieldClass):
    """Visualization container class.

    This class defines the full visualization. Calling its ``to_json``
    method should return a complete Vega definition.
    """
    def __init__(self, *args, **kwargs):
        """Initialize a Visualization

        In addition to setting any attributes, this sets the data, marks,
        scales, and axes properties to empty KeyedLists if they aren't
        defined by the arguments.
        """
        for attrib in ('data', 'marks', 'scales', 'axes'):
            setattr(self, attrib, KeyedList())
        super(Visualization, self).__init__(*args, **kwargs)

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

    @field_property((int, dict))
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
                    raise ValueError('padding must have keys %s' %
                                     ', '.join(required_keys))
                _assert_is_type('padding: %s' % key, value[key], int)
                if value[key] < 0:
                    raise ValueError('padding cannot be negative')
        else:
            if value < 0:
                raise ValueError('padding cannot be negative')

    @field_property((list, KeyedList))
    def data(value):
        """list or KeyedList of ``Data`` : Data definitions

        This defines the data being visualized. See the :class:`Data` class
        for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('data[%g]' % i, entry,  Data)

    @field_property((list, KeyedList))
    def scales(value):
        """list or KeyedList of ``Scale`` : Scale definitions

        Scales map the data from the domain of the data to some
        visualization space (such as an x-axis). See the :class:`Scale`
        class for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('scales[%g]' % i, entry, Scale)

    @field_property((list, KeyedList))
    def axes(value):
        """list or KeyedList of ``Axis`` : Axis definitions

        Axes define the locations of the data being mapped by the scales.
        See the :class:`Axis` class for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('axes[%g]' % i, entry, Axis)

    @field_property((list, KeyedList))
    def marks(value):
        """list or KeyedList of ``Mark`` : Mark definitions

        Marks are the visual objects (such as lines, bars, etc.) that
        represent the data in the visualization space. See the :class:`Mark`
        class for details.
        """
        for i, entry in enumerate(value):
            _assert_is_type('marks[%g]' % i, entry, Mark)

    def validate(self, require_all_fields=True):
        """Validate the visualization contents.

        Parameters
        ----------
        require_all_fields : boolean
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
            elif require_all_fields:
                raise ValidationError(
                    elem + ' must be defined for valid visualization')


class LoadError(Exception):
    """Exception for errors on loading data from third-party objects"""
    pass


class Data(FieldClass):
    _default_index_key = '_index'

    def __init__(self, name=None, **kwargs):
        """Initialize a Data object

        Parameters
        ----------
        name : string
            Name of the data set. If None (default), then the name will be
            set to ``'table'``.
        **kwargs : dict
            Attributes to set on initialization.
        """
        super(self.__class__, self).__init__(**kwargs)
        self.name = name if name else 'table'

    @field_property(str)
    def name(value):
        """string : Name of the data

        This is used by other components (``Mark``, etc.) for reference.
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

    def validate(self, *args):
        """Validate contents of class
        """
        super(self.__class__, self).validate(*args)
        if not self.name:
            raise ValidationError('name is required for Data')

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

    @classmethod
    def from_iters(cls, name=None, **kwargs):
        """Load values from lists

        Parameters
        ----------
        name : string
            Name of the data set. If None (default), the name will be set to
            ``'table'``.
        **kwargs : dict of iterables
            The ``values`` field will contain dictionaries with keys for
            each of the iterables provided. For example,

                d = Data.from_iters(x=[0, 1, 5], y=(10, 20, 30))

            would result in ``d`` having a ``values`` field with

                [{'x': 0, 'y': 10}, {'x': 1, 'y': 20}, {'x': 5, 'y': 30}]

            If the iterables are not the same length, then ValueError is
            raised.
        """
        lengths = [len(v) for v in kwargs.values()]
        if len(set(lengths)) != 1:
            raise ValueError('iterables must all be same length')
        else:
            values = [{} for i in xrange(lengths[0])]

        for k, v in kwargs.iteritems():
            for i, x in enumerate(v):
                values[i][k] = x

        return cls(name, values=values)

    def to_json(self, validate=False, pretty_print=True, data_path=None):
        """Convert data to JSON

        Parameters
        ----------
        data_path : string
            If not None, then data is written to a separate file at the
            specified path. Note that the ``url`` attribute if the data must
            be set independently for the data to load correctly.

        Returns
        -------
        string
            Valid Vega JSON.
        """
        #TODO: support writing to separate file
        return super(self.__class__, self).to_json(validate, pretty_print)


class ValueRef(FieldClass):
    """Define values for Mark properties
    """
    @field_property((str, int, float))
    def value(value):
        """int, float, or string : used for constant values

        This is ignored if the ``field`` property is defined.
        """

    @field_property(str)
    def field(value):
        """string : references field of the data in dot-notation

        The data is taken from the Mark's ``from_`` property. For instance, if
        the data has a definition
        ``[{'x': 2}, {'x': 3}, {'x': 1}]``
        then the data should be referenced as ``data.x``. Note that the first
        element is always `data` regardless of the name of the data.
        """

    @field_property(str)
    def scale(value):
        """string : references the name of a ``Scale``

        The scale is applied to the ``value`` and ``field`` attributes.
        """

    @field_property((int, float))
    def mult(value):
        """int or float : multiplier applied to the data after any scaling
        """

    @field_property((int, float))
    def offset(value):
        """int or float : additive offset applied to the data after any
        scaling and multipliers
        """

    @field_property(bool)
    def band(value):
        """boolean : use the range of the scale if applicable

        If this is True and ``scale`` is defined, then the value referenced
        is the range band referenced scale. See the d3 documentation on
        ``ordinal.rangeBand`` for more info.
        """


class PropertySet(FieldClass):
    """Definition of properties for ``Mark`` objects and labels of ``Axis``
    objects"""

    @field_property(ValueRef)
    def x(value):
        """ValueRef : number, left-most x-coordinate

        For most marks, this will be equal to the field of the independent
        variable. For example,
        ``{"scale": "x", "field": "data.x"}``
        will place a mark with its left-most coordinate at the x-values of
        the data. Something like
        ``{"scale": "x", "value": 10}``
        will place a single mark at given x-coordinate.
        """

    @field_property(ValueRef)
    def x2(value):
        """ValueRef : number, right-most x-coordinate

        Generally, for marks where the width is significant, it's better to
        use the ``width`` property.
        """

    @field_property(ValueRef)
    def width(value):
        """ValueRef : number, width of the mark

        Set the ``band`` property of the ``ValueRef`` to True to use the
        full width.
        """

    @field_property(ValueRef)
    def y(value):
        """ValueRef : number, top-most y-coordinate

        The same remarks for the ``x`` property apply here.
        """

    @field_property(ValueRef)
    def y2(value):
        """ValueRef : number, bottom-most y-coordinate

        The same remarks for the ``x2`` property apply here.
        """

    @field_property(ValueRef)
    def height(value):
        """ValueRef : number, height of the mark
        """

    @field_property(ValueRef)
    def opacity(value):
        """ValueRef : number, overall opacity (0 to 1)
        """

    @field_property(ValueRef)
    def fill(value):
        """ValueRef : color, fill color for the mark
        """

    @field_property(field_type=ValueRef, field_name='fillOpacity')
    def fill_opacity(value):
        """ValueRef : number, opacity of the fill (0 to 1)
        """

    @field_property(ValueRef)
    def stroke(value):
        """ValueRef : color, stroke color for the mark
        """

    @field_property(field_type=ValueRef, field_name='strokeWidth')
    def stroke_width(value):
        """ValueRef : number, width of the stroke in pixels
        """

    @field_property(field_type=ValueRef, field_name='strokeOpacity')
    def stroke_opacity(value):
        """ValueRef : number, opacity of the stroke (0 to 1)
        """

    @field_property(ValueRef)
    def size(value):
        """ValueRef : number, area of the mark in pixels

        This is the total area of a symbol. For example, a value of 500 and
        a ``shape`` of ``'circle'`` would result in circles with an area of
        500 square pixels. Only used if ``type`` is ``'symbol'``.
        """

    @field_property(ValueRef)
    def shape(value):
        """ValueRef : string, type of symbol to use

        Possible values are ``'circle'`` (default), ``'square'``,
        ``'cross'``, ``'diamond'``, ``'triangle-up'``, and
        ``'triangle-down'``. Only used if ``type`` is ``'symbol'``.
        """

    @field_property(ValueRef)
    def path(value):
        """ValueRef : string, SVG path string

        This would typically be used for maps and other things where the
        path is taken from the data.
        """

    @field_property(field_type=ValueRef, field_name='innerRadius')
    def inner_radius(value):
        """ValueRef : number, inner radius of arc in pixels

        Only used if ``type`` is ``'arc'``."""

    @field_property(field_type=ValueRef, field_name='outerRadius')
    def outer_radius(value):
        """ValueRef : number, outer radius of the arc in pixels

        Only used if ``type`` is ``'arc'``."""

    @field_property(field_type=ValueRef, field_name='startAngle')
    def start_angle(value):
        """ValueRef : number, start angle of the arc in radians

        Only used if ``type`` is ``'arc'``."""

    @field_property(field_type=ValueRef, field_name='endAngle')
    def end_angle(value):
        """ValueRef : number, end angle of the arc in radians

        Only used if ``type`` is ``'arc'``."""

    @field_property(ValueRef)
    def interpolate(value):
        """ValueRef : string, line interpolation method to use

        Possible values for ``area`` types are `'linear'`,
        ``'step-before'``, ``'step-after'``, ``'basis'``, ``'basis-open'``,
        ``'cardinal'``, ``'cardinal-open'``, ``'monotone'``. ``line`` types
        have all values for ``area`` as well as ``'basis-closed'``,
        ``'bundle'``, and ``'cardinal-closed'``.

        Only used if ``type`` is ``'area'`` or ``'line'``.
        """
        #TODO check values

    @field_property(ValueRef)
    def tension(value):
        """ValueRef : number, tension used for interpolation

        Only used if ``type`` is ``'area'`` or ``'line'``.
        """

    @field_property(ValueRef)
    def url(value):
        """ValueRef : string, url of image

        Only used if ``type`` is ``'image'``.
        """

    @field_property(ValueRef)
    def align(value):
        """ValueRef : string, horizontal alignment of mark

        Possible values are ``'left'``, ``'right'``, and ``'center'``. Only
        used if ``type`` is ``'image'`` or ``'text'``.
        """
        #TODO check values

    @field_property(ValueRef)
    def baseline(value):
        """ValueRef : string, vertical alignment of mark

        Possible values are ``'top'``, ``'middle'``, and ``'bottom'``. Only
        used if ``type`` is ``'image'`` or ``'text'``.
        """
        #TODO check values

    @field_property(ValueRef)
    def text(value):
        """ValueRef : string, text to display

        Only used if ``type`` is ``'text'``."""

    @field_property(ValueRef)
    def dx(value):
        """ValueRef : number, horizontal margin between text and anchor
        point in pixels

        Ignored if ``align`` is ``'center'``. Only used if ``type`` is
        ``'text'``.
        """

    @field_property(ValueRef)
    def dy(value):
        """ValueRef : number, vertical margin between text and anchor
        point in pixels

        Ignored if ``baseline`` is ``'middle'``. Only used if ``type`` is
        ``'text'``.
        """

    @field_property(ValueRef)
    def angle(value):
        """ValueRef : number, rotation of text in degrees

        Only used if ``type`` is ``'text'``.
        """

    @field_property(ValueRef)
    def font(value):
        """ValueRef : string, typeface for text

        Only used if ``type`` is ``'text'``.
        """

    @field_property(field_type=ValueRef, field_name='fontSize')
    def font_size(value):
        """ValueRef : number, font size in pixels

        Only used if ``type`` is ``'text'``.
        """

    @field_property(field_type=ValueRef, field_name='fontWeight')
    def font_weight(value):
        """ValueRef : string, font weight

        Should be a valid SVG font weight. Only used if ``type`` is
        ``'text'``.
        """

    @field_property(field_type=ValueRef, field_name='fontStyle')
    def font_style(value):
        """ValueRef : string, font style

        Should be a valid SVG font style. Only used if ``type`` is
        ``'text'``.
        """


class MarkProperties(FieldClass):
    @field_property(PropertySet)
    def enter(value):
        """PropertySet : properties applied when data is loaded
        """

    @field_property(PropertySet)
    def exit(value):
        """PropertySet : properties applied when data is removed
        """

    @field_property(PropertySet)
    def update(value):
        """PropertySet : properties applied for all non-exiting data

        (This is vague. Need better Vega docs.)
        """

    @field_property(PropertySet)
    def hover(value):
        """PropertySet, properties applied on mouse-over

        On mouse out, the ``update`` properties are applied.
        """


class Mark(FieldClass):

    _valid_type_values = [
        'rect', 'symbol', 'path', 'arc', 'area', 'line', 'image', 'text']

    @field_property(str)
    def name(value):
        """string : Optional unique name for mark"""

    @field_property(str)
    def description(value):
        """string : Optional description for mark"""

    @field_property(str)
    def type(value):
        """string : Type of mark

        Valid types are ``'rect'``, ``'symbol'``, ``'path'``, ``'arc'``,
        ``'area'``, ``'line'``, ``'image'``, and ``'text'``.
        """
        if value not in Mark._valid_type_values:
            raise ValueError(
                'invalid mark type %s, valid types are %s' % (
                    value, Mark._valid_type_values))

    @field_property(field_type=dict, field_name='from')
    def from_(value):
        """dict : Description of data to visualize

        Note that although the property has the name ``from_`` (using
        ``from`` is invalid Python syntax), the JSON will contain the
        correct property ``from``.
        """

    @field_property(MarkProperties)
    def properties(value):
        """MarkProperties : Mark property set definitions"""

    @field_property(str)
    def key(value):
        """string : Field to use for data binding

        When updating data dynamically, restrict dynamic transitions from
        affecting data with the given key. This can be useful for something
        like scrolling time series. See the Vega examples.
        """

    @field_property(ValueRef)
    def delay(value):
        """ValueRef, number : Transitional delay in milliseconds.
        """

    @field_property(str)
    def ease(value):
        """string : Type of transition easing

        Valid types are ``'linear'``, ``'quad'``, ``'cubic'``, ``'sin'``,
        ``'exp'``, ``'circle'``, and ``'bounce'``, which can be appended
        with the modifiers ``'in'``, ``'out'``, ``'in-out'``, and
        ``'out-in'``. The default is ``'cubic-in-out'``.

        See the documentation for the d3 ease function for more details.
        """


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
            - ``'width'`` - Set the range to the width of the visualization
            - ``'height'`` - Set the range to the height of the visualization
            - ``'shapes'`` - Equivalent to the symbol types ``['circle',
              'cross', 'diamond', 'square', 'triangle-down',
              'triangle-up']``
            - ``'category10'`` - A pre-determined 10-color pallet
            - ``'category20'`` - A pre-determined 20-color pallet
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


class AxisProperties(FieldClass):
    @field_property(field_type=PropertySet, field_name='majorTicks')
    def major_ticks(value):
        """PropertySet : Definition of major tick marks"""

    @field_property(field_type=PropertySet, field_name='minorTicks')
    def minor_ticks(value):
        """PropertySet : Definition of minor tick marks"""

    @field_property(PropertySet)
    def label(value):
        """PropertySet : Definition of marks for axis labels"""

    @field_property(PropertySet)
    def axis(value):
        """PropertySet : Definition of axis line style"""


class Axis(FieldClass):
    @field_property(str)
    def type(value):
        """string : Type of axis - ``'x'`` or ``'y'``"""
        if value not in ('x', 'y'):
            raise ValueError('Axis.type must be "x" or "y"')

    @field_property(str)
    def scale(value):
        """string : Name of scale used for axis"""

    @field_property(str)
    def orient(value):
        """string : Orientation of the axis

        Should be one of ``'top'``, ``'bottom'``, ``'left'``, or ``'right'``.
        """

    @field_property(str)
    def format(value):
        """string : Formatting to use for axis labels

        See d3's formatting documentation for format pattern.
        """

    @field_property(int)
    def ticks(value):
        """int : Number of ticks to use"""

    @field_property(list)
    def values(value):
        """list of objects in scale's domain : Explicit definitions for
        values

        Values should be in the domain of the Axis's scale. Custom ticks can
        be used by setting ``properties``.
        """

    @field_property((int, float))
    def subdivide(value):
        """int or float : Number of minor ticks in between major ticks

        Only valid for quantitative scales.
        """

    @field_property(field_type=int, field_name='tickPadding')
    def tick_padding(value):
        """int : Pixels between ticks and text labels"""

    @field_property(field_type=int, field_name='tickSize')
    def tick_size(value):
        """int : Size in pixels of all ticks"""

    @field_property(field_type=int, field_name='tickSizeMajor')
    def tick_size_major(value):
        """int : Size in pixels of major ticks"""

    @field_property(field_type=int, field_name='tickSizeMinor')
    def tick_size_minor(value):
        """int : Size in pixels of minor ticks"""

    @field_property(field_type=int, field_name='tickSizeEnd')
    def tick_size_end(value):
        """int : Size in pixels of end ticks"""

    @field_property(int)
    def offset(value):
        """int : Offset in pixels to displace the edge of the axis from the
        referenced area
        """

    @field_property(AxisProperties)
    def properties(value):
        """AxisProperties : Custom styling for ticks and tick labels
        """
