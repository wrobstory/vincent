# -*- coding: utf-8 -*-
"""

Vega: The core functionality for Vincent. Vega grammar is mapped 1:1
in ORM.

"""
from __future__ import (print_function, division)
import json
import time
import random
import copy

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None

#TODO: Keep local?
d3_js_url = 'http://trifacta.github.com/vega/d3.v3.min.js'
vega_js_url = 'http://trifacta.github.com/vega/vega.js'


def initialize_notebook():
    """Initialize the iPython notebook display elements"""
    try:
        from IPython.core.display import display, HTML, Javascript
    except ImportError:
        print('iPython Notebook could not be loaded.')

    display(HTML('<script src="%s"></script>' % d3_js_url))
    display(HTML('<script src="%s"></script>' % vega_js_url))

    return display, HTML, Javascript


def _assert_is_type(name, value, value_type):
    """Assert that a value must be a given type."""
    if not isinstance(value, value_type):
        if type(value_type) is tuple:
            types = ', '.join(t.__name__ for t in value_type)
            raise ValueError('{0} must be one of ({1})'.format(name, types))
        else:
            raise ValueError('{0} must be {1}'
                             .format(name, value_type.__name__))


class ValidationError(Exception):
    """Exception raised with validation fails

    This exception is raised only when the ``validate`` functions of classes
    that inherit from ``FieldClass`` are called. It implies that the classes
    do not contain valid Vega JSON."""
    pass


class KeyedList(list):
    """A list that can optionally be indexed by the ``name`` attribute of
    its elements"""
    def __init__(self, attr_name='name', *args, **kwargs):
        self.attr_name = attr_name
        list.__init__(self, *args, **kwargs)

    def __get_keys(self):
        keys = [getattr(x, self.attr_name) for x in self]
        if len(keys) != len(set(keys)):
            raise ValidationError('duplicate keys found')
        return keys

    def __getitem__(self, key):
        if isinstance(key, str):
            keys = self.__get_keys()
            if key not in keys:
                raise KeyError(' "{0}" is an invalid key'.format(key))
            else:
                return self[keys.index(key)]
        else:
            return list.__getitem__(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if not hasattr(value, self.attr_name):
                raise ValidationError(
                    'object must have ' + self.attr_name + ' attribute')
            elif getattr(value, self.attr_name) != key:
                raise ValidationError(
                    "key must be equal to '" + self.attr_name +
                    "' attribute")

            keys = self.__get_keys()
            if key not in keys:
                self.append(value)
            else:
                list.__setitem__(self, keys.index(key), value)
        else:
            list.__setitem__(self, key, value)


def grammar(grammar_type=None, grammar_name=None):
    """Decorator to define properties that map to the ``grammar``
    dict. This dict is the canonical representation of the Vega grammar
    within Vincent.

    This decorator is intended for classes that map to some pre-defined JSON
    structure, such as axes, data, marks, scales, etc. It is assumed that this
    decorates functions with an instance of ``self.grammar``.

    Parameters
    ----------
    grammar_type : type or tuple of types, default None
        If the argument to the decorated function is not of the given types,
        then a ValueError is raised. No type checking is done if the type is
        None (default).
    grammar_name : string, default None
        An optional name to map to the internal ``grammar`` dict. If None
        (default), then the key for the dict is the name of the function
        being decorated. If not None, then it will be the name specified
        here. This is useful if the expected JSON field name is a Python
        keyword or has an un-Pythonic name.

    This should decorate a "validator" function that should return no value
    but raise an exception if the provided value is not valid Vega grammar. If
    the validator throws no exception, then the value is assigned to the
    ``grammar`` dict.

    The validator function should take only one argument - the value to be
    validated - so that no ``self`` argument is included; the validator
    should not modify the class.

    If no arguments are given, then no type-checking is done the property
    will be mapped to a field with the name of the decorated function.

    The doc string for the property is taken from the validator functions's
    doc string.
    """
    def grammar_creator(validator, name):
        def setter(self, value):
            if isinstance(grammar_type, (type, tuple)):
                _assert_is_type(validator.__name__, value, grammar_type)
            validator(value)
            self.grammar[name] = value

        def getter(self):
            return self.grammar.get(name, None)

        def deleter(self):
            if name in self.grammar:
                del self.grammar[name]

        return property(getter, setter, deleter, validator.__doc__)

    if isinstance(grammar_type, (type, tuple)):
        # If grammar_type is a type, return another decorator.
        def grammar_dec(validator):
            # Make sure to use the grammar name if it's there.
            if grammar_name:
                return grammar_creator(validator, grammar_name)
            else:
                return grammar_creator(validator, validator.__name__)
        return grammar_dec
    elif isinstance(grammar_name, str):
        # If grammar_name is a string, use that name and return another
        # decorator.
        def grammar_dec(validator):
            return grammar_creator(validator, grammar_name)
        return grammar_dec
    else:
        # Otherwise we assume that grammar_type is actually the function being
        # decorated.
        return grammar_creator(grammar_type, grammar_type.__name__)


class GrammarDict(dict):
    """The Vega Grammar. When called, obj.grammar returns a Python data
    structure for the Vega Grammar. When printed, obj.grammar returns a
    string representation."""

    def __init__(self, *args, **kwargs):
        """Standard Dict init"""
        dict.__init__(self, *args, **kwargs)

    def encoder(self, obj):
        """Encode grammar objects for each level of hierarchy"""
        if hasattr(obj, 'grammar'):
            return obj.grammar

    def __call__(self):
        """When called, return the Vega grammar as a Python data structure."""

        return json.loads(json.dumps(self, default=self.encoder))

    def __str__(self):
        """String representation of Vega Grammar"""

        return json.dumps(self, default=self.encoder)


class GrammarClass(object):
    """Base class for objects that rely on an internal ``grammar`` dict. This
    dict contains the complete Vega grammar.

    This should be used as a superclass for classes that map to some JSON
    structure. The JSON content is stored in an internal dict named
    ``grammar``.
    """
    def __init__(self, **kwargs):
        """Initialize a GrammarClass

        **kwargs are attribute-value pairs that are set on initialization.
        These will generally be keys for the ``grammar`` dict. If the
        attribute does not already exist as a property, then a
        ``ValueError`` is raised.
        """
        self.grammar = GrammarDict()

        for attr, value in kwargs.iteritems():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise ValueError('unknown keyword argument ' + attr)

    def validate(self):
        """Validate the contents of the object.

        This calls ``setattr`` for each of the class's grammar properties. It
        will catch ``ValueError``s raised by the grammar property's setters
        and re-raise them as :class:`ValidationError`.
        """
        for key, val in self.grammar.iteritems():
            try:
                setattr(self, key, val)
            except ValueError as e:
                raise ValidationError('invalid contents: ' + e.message)

    def to_json(self, path=None, validate=False, pretty_print=True):
        """Convert object to JSON

        Parameters
        ----------
        path: string, default None
            Path to write JSON out. If there is no path provided, JSON
            will be returned as a string to the console.
        validate : boolean
            If True, call the object's `validate` method before
            serializing. Default is False.
        pretty_print : boolean
            If True (default), JSON is printed in more-readable form with
            indentation and spaces.

        Returns
        -------
        string
            JSON serialization of the class's grammar properties.
        """
        if validate:
            self.validate()

        if pretty_print:
            dumps_args = {'indent': 2, 'separators': (',', ': ')}
        else:
            dumps_args = {}

        def encoder(obj):
            if hasattr(obj, 'grammar'):
                return obj.grammar

        if path:
            with open(path, 'w') as f:
                json.dump(self.grammar, f, default=encoder, **dumps_args)
        else:
            return json.dumps(self.grammar, default=encoder, **dumps_args)

    def from_json(self):
        """Load object from JSON

        Not yet implemented.
        """
        raise NotImplementedError()


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
        # The axes get keyed by "type" instead of name.
        if not self.axes:
            self.axes = KeyedList(attr_name='type')
        # Marks don't get keyed.
        if not self.marks:
            self.marks = []

    @grammar(str)
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

    @grammar((int, dict))
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
        else:
            if value < 0:
                raise ValueError('Padding cannot be negative.')

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

    def validate(self, require_all=True):
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

    def display(self):
        """Display visualization inline in IPython notebook"""

        display, HTML, Javascript = initialize_notebook()

        # Copied from vincent.ipynb:
        # HACK: use a randomly chosen unique div id
        id = random.randint(0, 2 ** 16)
        a = HTML('<div id="vis%d"></div>' % id)
        b = Javascript('vg.parse.spec(%s, function(chart) '
                       '{ chart({el:"#vis%d"}).update(); });' %
                       (self.to_json(pretty_print=False), id))
        display(a, b)


class LoadError(Exception):
    """Exception for errors on loading data from third-party objects"""
    pass


class Data(GrammarClass):
    """Data container for visualization

    The Vega document may contain the data itself or a reference to a URL
    containing the data and formatting instructions. Additionally, new data
    can be created from old data via the transform fields.
    """
    _default_index_key = 'idx'

    def __init__(self, name=None, **kwargs):
        """Initialize a Data object

        Parameters
        ----------
        name : string, default None
            Name of the data set. If None (default), then the name will be
            set to ``'table'``.
        **kwargs : dict
            Attributes to set on initialization.
        """
        super(self.__class__, self).__init__(**kwargs)
        self.name = name if name else 'table'

    @grammar(str)
    def name(value):
        """string : Name of the data

        This is used by other components (``Mark``, etc.) for reference.
        """

    @grammar(str)
    def url(value):
        """string : URL from which to load the data

            This can be used as an alternative to defining the data in the
            ``values`` attribute.
        """

    @grammar(list)
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

    @grammar(str)
    def source(value):
        """string : ``name`` field of another data set

        This is typically used with data transforms to create new data
        values.
        """

    @grammar(list)
    def transform(value):
        """list : transforms to apply to the data

        Note: Transform-relational classes are not yet implemented.
        """

    @grammar(dict)
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
        name : string, default None
            Applies to the ``name`` attribute of the generated class. If
            ``None`` (default), then the ``name`` attribute of ``pd_obj`` is
            used if it exists, or ``'table'`` if it doesn't.
        index_key : string, default None
            In each :class:`dict` entry of the ``values`` attribute, the
            index of the pandas object will have this key. If ``None``
            (default), then ``idx`` is used.
        data_key : string, default None
            Applies only to ``Series``. If ``None`` (default), then the data is
            indexed by the ``name`` attribute of the generated class.
            Otherwise, the data will be indexed by this key. For example, if
            ``data_key`` is ``'x'``, then the entries of the ``values`` list
            will be ``{'idx': ..., 'x': ...}``.
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
        index : iterable, default None
            Sequence of indices from top to bottom. If ``None`` (default),
            then the indices are integers starting at 0. Must have same
            length as the number of rows of ``np_obj``.
        index_key : string, default None
            Key to use for the index. If ``None`` (default), ``idx`` is
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
    def from_mult_iters(cls, name=None, stacked=False, **kwargs):
        """Load values from multiple iters

        Parameters
        ----------
        name : string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.
        stacked: bool, default False
            Pass true to stack all passed iters on the common axis of the
            first iter.
        **kwargs : dict of iterables
            The ``values`` field will contain dictionaries with keys for
            each of the iterables provided. For example,

                d = Data.from_iters(x=[0, 1, 5], y=(10, 20, 30))

            would result in ``d`` having a ``values`` field with

                [{'x': 0, 'y': 10}, {'x': 1, 'y': 20}, {'x': 5, 'y': 30}]

            If the iterables are not the same length, then ValueError is
            raised.
        """
        if not name:
            name = 'table'

        lengths = [len(v) for v in kwargs.values()]
        if stacked:
            lengths = [x * 2 for x in lengths]

        if len(set(lengths)) != 1:
            raise ValueError('iterables must all be same length')
        else:
            values = [{} for i in xrange(lengths[0])]

        for k, v in kwargs.iteritems():
            # if stacked:
            #     for i, x in enumerate(range(len(values))):
            #         values[i][k]
            for i, x in enumerate(v):
                values[i][k] = x

        return cls(name, values=values)

    @classmethod
    def stacked(cls, data=None, name=None, stack_on=None, on_index=True, **kwargs):
        """"Load values from a Pandas DataFrame, a dict of iters, or multiple
        iters into stacked values for stacked area/bar charts

        Parameters
        ----------
        data: Pandas DataFrame or dict of iters, default None
            Pandas DataFrame or dict of iterables
        name: string, default None
            Name of the dataset. If None, the name will be set to ``'table'``.
        stack_on: string, default None
            Key to identify x-axis on which to stack other values. Can pass
            dict key or Pandas DataFrame column name.
        on_index: boolean, default True
            Pass True to stack Pandas DataFrames on index as common x-axis
        kwargs: dict of iterables
            The ``values`` field will contain dictionaries with keys for
            each of the iterables provided. For example,

                d = Data.from_iters(x=[0, 1, 5], y=(10, 20, 30))

            would result in ``d`` having a ``values`` field with

                [{'x': 0, 'y': 10}, {'x': 1, 'y': 20}, {'x': 5, 'y': 30}]

            If the iterables are not the same length, then ValueError is
            raised.

        Example
        -------
        >>>data = Data.stacked({'x': [0, 1, 2], 'y': [3, 4, 5],
                               'y2': [7, 8, 9]}, stack_on='x')
        >>>data = Data.stacked(df, stack_on='Column1')
        >>>data = Data.stacked(stack_on='x', x=[1,2,3], y=[4,5,6], y2=[7,8,9])

        """

        if hasattr(data, 'name'):
            name = data

        if kwargs:
            if len(set([len(v) for v in kwargs.values()])) != 1:
                raise ValueError('iterables must all be same length')
            data = kwargs

        values = []

        if data is not None:
            if isinstance(data, pd.DataFrame):
                if stack_on and on_index:
                    raise ValueError('Cannot stack on both column and index')
                if hasattr(data, 'name'):
                    name = data.name
                for i, row in data.iterrows():
                    if on_index:
                        key = cls.serialize(i)
                        stack_on = data.index.name or cls._default_index_key
                    else:
                        key = cls.serialize(row[stack_on])
                        row = row.drop(stack_on)
                    for cnt, (idx, val) in enumerate(row.iteritems()):
                        values.append({stack_on: key, idx: cls.serialize(val), 'c': cnt})

            elif isinstance(data, dict):
                copydat = copy.copy(data)
                if not stack_on:
                    raise ValueError('Data passed as a dict must include a key'
                                     ' for `stack_on` on which to stack')
                key = copydat.pop(stack_on)
                for cnt, (k, v) in enumerate(copydat.iteritems()):
                    for idx, val in zip(key, v):
                        values.append({stack_on: idx, k: val, 'c': cnt})

        return cls(name, values=sorted(values, key=lambda x: x['c']))

    @classmethod
    def from_iter(cls, data, name=None):
        """Convenience method for loading data from a single list. Defaults
        to numerical indexing for x-axis.

        Parameters
        ----------
        data: list
            List of data
        name: string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.

        """
        if not name:
            name = 'table'
        values = [{"x": x, "y": y}
                  for x, y in zip(range(len(data)), data)]
        return cls(name, values=values)

    @classmethod
    def from_iter_pairs(cls, data, name=None):
        """Convenience method for loading data from a tuple of tuples or list of lists.
        Defaults to numerical indexing for x-axis.

        Parameters
        ----------
        data: tuple
            Tuple of paired tuples
        name: string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.

        Example:
        >>>data = Data.from_tuples([(1,2), (3,4), (5,6)])

        """
        if not name:
            name = 'table'
        values = [{"x": x[0], "y": x[1]} for x in data]
        return cls(name, values=values)

    @classmethod
    def from_dict(cls, data, name=None):
        """Convenience method for loading data from dict

        Parameters
        ----------
        data: dict
            Dict of data
        name: string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.

        Example
        -------
        >>>data = Data.from_dict({'apples': 10, 'oranges': 2, 'pears': 3})

        """
        if not name:
            name = 'table'
        values = [{"x": x, "y": y} for x, y in data.iteritems()]
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


class ValueRef(GrammarClass):
    """Container for the value-referencing properties of marks

    It is often useful for marks to share properties to maintain consistency
    when parts of the visualization are changed. Additionally, the marks
    themselves may have properties somehow mapped from the data (i.e. mark
    size proportional to some data field). The ``ValueRef`` class can be
    used to either define values locally or reference other fields.

    ValueRefs can reference numbers, strings, or arbitrary objects,
    depending on their use.
    """
    @grammar((str, int, float))
    def value(value):
        """int, float, or string : used for constant values

        This is ignored if the ``field`` property is defined.
        """

    @grammar(str)
    def field(value):
        """string : reference to a field of the data in dot-notation

        The data is taken from the Mark's ``from_`` property. For instance, if
        the data has a definition
        ``[{'x': 2}, {'x': 3}, {'x': 1}]``
        then the data should be referenced as ``data.x``. Note that the first
        element is always `data` regardless of the name of the data.
        """

    @grammar(str)
    def scale(value):
        """string : reference to the name of a ``Scale``

        The scale is applied to the ``value`` and ``field`` attributes.
        """

    @grammar((int, float))
    def mult(value):
        """int or float : multiplier applied to the data after any scaling
        """

    @grammar((int, float))
    def offset(value):
        """int or float : additive offset applied to the data after any
        scaling and multipliers
        """

    @grammar(bool)
    def band(value):
        """boolean : use the range of the scale if applicable

        If this is True and ``scale`` is defined, then the value referenced
        is the range band referenced scale. See the d3 documentation on
        ``ordinal.rangeBand`` for more info.
        """


class PropertySet(GrammarClass):
    """Definition of properties for ``Mark`` objects and labels of ``Axis``
    objects

    These define the appearance details for marks and axes.

    All properties are defined by ``ValueRef`` classes. As a warning,
    validation of the values is only performed on the ``value`` field of the
    class, which is ignored by Vega if the ``field`` property is set.
    """
    @grammar(ValueRef)
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

    @grammar(ValueRef)
    def x2(value):
        """ValueRef : number, right-most x-coordinate

        Generally, for marks where the width is significant, it's better to
        use the ``width`` property.
        """

    @grammar(ValueRef)
    def width(value):
        """ValueRef : number, width of the mark

        Set the ``band`` property of the ``ValueRef`` to True to use the
        full width.
        """

    @grammar(ValueRef)
    def y(value):
        """ValueRef : number, top-most y-coordinate

        The same remarks for the ``x`` property apply here.
        """

    @grammar(ValueRef)
    def y2(value):
        """ValueRef : number, bottom-most y-coordinate

        The same remarks for the ``x2`` property apply here.
        """

    @grammar(ValueRef)
    def height(value):
        """ValueRef : number, height of the mark
        """

    @grammar(ValueRef)
    def opacity(value):
        """ValueRef : number, overall opacity (0 to 1)
        """

    @grammar(ValueRef)
    def fill(value):
        """ValueRef : string, fill color for the mark

        Colors can be specified in standard HTML hex notation or as CSS3
        compatible strings. The color string is not validated due to its
        large number of valid values.
        """
        if value.value:
            _assert_is_type('fill.value', value.value, str)

    @grammar(grammar_type=ValueRef, grammar_name='fillOpacity')
    def fill_opacity(value):
        """ValueRef : int or float, opacity of the fill (0 to 1)
        """
        if value.value:
            _assert_is_type('fill_opacity.value', value.value,
                            (float, int))
            if value.value < 0 or value.value > 1:
                raise ValueError(
                    'fill_opacity must be between 0 and 1')

    @grammar(ValueRef)
    def stroke(value):
        """ValueRef : color, stroke color for the mark

        Colors can be specified in standard HTML hex notation or as CSS3
        compatible strings. The color string is not validated due to its
        large number of valid values.
        """
        if value.value:
            _assert_is_type('stroke.value', value.value, str)

    @grammar(grammar_type=ValueRef, grammar_name='strokeWidth')
    def stroke_width(value):
        """ValueRef : int, width of the stroke in pixels
        """
        if value.value:
            _assert_is_type('stroke_width.value', value.value, int)
            if value.value < 0:
                raise ValueError('stroke width cannot be negative')

    @grammar(grammar_type=ValueRef, grammar_name='strokeOpacity')
    def stroke_opacity(value):
        """ValueRef : number, opacity of the stroke (0 to 1)
        """
        if value.value:
            _assert_is_type('stroke_opacity.value', value.value,
                            (float, int))
            if value.value < 0 or value.value > 1:
                raise ValueError(
                    'stroke_opacity must be between 0 and 1')

    @grammar(ValueRef)
    def size(value):
        """ValueRef : number, area of the mark in pixels

        This is the total area of a symbol. For example, a value of 500 and
        a ``shape`` of ``'circle'`` would result in circles with an area of
        500 square pixels. Only used if ``type`` is ``'symbol'``.
        """
        if value.value:
            _assert_is_type('size.value', value.value, int)
            if value.value < 0:
                raise ValueError('size cannot be negative')

    _valid_shapes = ('circle', 'square', 'cross', 'diamond', 'triangle-up',
                     'triangle-down')

    @grammar(ValueRef)
    def shape(value):
        """ValueRef : string, type of symbol to use

        Possible values are ``'circle'`` (default), ``'square'``,
        ``'cross'``, ``'diamond'``, ``'triangle-up'``, and
        ``'triangle-down'``. Only used if ``type`` is ``'symbol'``.
        """
        if value.value:
            _assert_is_type('shape.value', value.value, str)
            if value.value not in PropertySet._valid_shapes:
                raise ValueError(value.value + ' is not a valid shape')

    @grammar(ValueRef)
    def path(value):
        """ValueRef : string, SVG path string

        This would typically be used for maps and other things where the
        path is taken from the data.
        """
        if value.value:
            _assert_is_type('path.value', value.value, str)

    @grammar(grammar_type=ValueRef, grammar_name='innerRadius')
    def inner_radius(value):
        """ValueRef : number, inner radius of arc in pixels

        Only used if ``type`` is ``'arc'``."""

    @grammar(grammar_type=ValueRef, grammar_name='outerRadius')
    def outer_radius(value):
        """ValueRef : number, outer radius of the arc in pixels

        Only used if ``type`` is ``'arc'``."""

    @grammar(grammar_type=ValueRef, grammar_name='startAngle')
    def start_angle(value):
        """ValueRef : number, start angle of the arc in radians

        Only used if ``type`` is ``'arc'``."""

    @grammar(grammar_type=ValueRef, grammar_name='endAngle')
    def end_angle(value):
        """ValueRef : number, end angle of the arc in radians

        Only used if ``type`` is ``'arc'``."""

    @grammar(ValueRef)
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

    @grammar(ValueRef)
    def tension(value):
        """ValueRef : number, tension used for interpolation

        Only used if ``type`` is ``'area'`` or ``'line'``.
        """

    @grammar(ValueRef)
    def url(value):
        """ValueRef : string, url of image

        Only used if ``type`` is ``'image'``.
        """

    @grammar(ValueRef)
    def align(value):
        """ValueRef : string, horizontal alignment of mark

        Possible values are ``'left'``, ``'right'``, and ``'center'``. Only
        used if ``type`` is ``'image'`` or ``'text'``.
        """
        #TODO check values

    @grammar(ValueRef)
    def baseline(value):
        """ValueRef : string, vertical alignment of mark

        Possible values are ``'top'``, ``'middle'``, and ``'bottom'``. Only
        used if ``type`` is ``'image'`` or ``'text'``.
        """
        #TODO check values

    @grammar(ValueRef)
    def text(value):
        """ValueRef : string, text to display

        Only used if ``type`` is ``'text'``."""

    @grammar(ValueRef)
    def dx(value):
        """ValueRef : number, horizontal margin between text and anchor
        point in pixels

        Ignored if ``align`` is ``'center'``. Only used if ``type`` is
        ``'text'``.
        """

    @grammar(ValueRef)
    def dy(value):
        """ValueRef : number, vertical margin between text and anchor
        point in pixels

        Ignored if ``baseline`` is ``'middle'``. Only used if ``type`` is
        ``'text'``.
        """

    @grammar(ValueRef)
    def angle(value):
        """ValueRef : number, rotation of text in degrees

        Only used if ``type`` is ``'text'``.
        """

    @grammar(ValueRef)
    def font(value):
        """ValueRef : string, typeface for text

        Only used if ``type`` is ``'text'``.
        """

    @grammar(grammar_type=ValueRef, grammar_name='fontSize')
    def font_size(value):
        """ValueRef : number, font size in pixels

        Only used if ``type`` is ``'text'``.
        """

    @grammar(grammar_type=ValueRef, grammar_name='fontWeight')
    def font_weight(value):
        """ValueRef : string, font weight

        Should be a valid SVG font weight. Only used if ``type`` is
        ``'text'``.
        """

    @grammar(grammar_type=ValueRef, grammar_name='fontStyle')
    def font_style(value):
        """ValueRef : string, font style

        Should be a valid SVG font style. Only used if ``type`` is
        ``'text'``.
        """


class MarkProperties(GrammarClass):
    """Sets of all Mark properties

    Mark properties can change depending on user interaction or changing
    data. This class defines four events for which the properties may
    change.
    """
    @grammar(PropertySet)
    def enter(value):
        """PropertySet : properties applied when data is loaded
        """

    @grammar(PropertySet)
    def exit(value):
        """PropertySet : properties applied when data is removed
        """

    @grammar(PropertySet)
    def update(value):
        """PropertySet : properties applied for all non-exiting data

        (This is vague. Need better Vega docs.)
        """

    @grammar(PropertySet)
    def hover(value):
        """PropertySet, properties applied on mouse-over

        On mouse out, the ``update`` properties are applied.
        """


class MarkRef(GrammarClass):
    """Definitions for Mark source data
    """
    @grammar(str)
    def data(value):
        """string : Name of the source `Data`"""

    @grammar(list)
    def transform(value):
        """list : List of transforms to apply to the data"""


class Mark(GrammarClass):
    """Definitions for data marks

    Marks are the fundamental component that the viewer sees - such as a
    bar, line etc.. This class defines how the marks appear and what data
    the marks represent.
    """
    _valid_type_values = [
        'rect', 'symbol', 'path', 'arc', 'area', 'line', 'image', 'text']

    @grammar(str)
    def name(value):
        """string : Optional unique name for mark"""

    @grammar(str)
    def description(value):
        """string : Optional description for mark"""

    @grammar(str)
    def type(value):
        """string : Type of mark

        Valid types are ``'rect'``, ``'symbol'``, ``'path'``, ``'arc'``,
        ``'area'``, ``'line'``, ``'image'``, and ``'text'``.
        """
        if value not in Mark._valid_type_values:
            raise ValueError(
                'invalid mark type %s, valid types are %s' % (
                    value, Mark._valid_type_values))

    @grammar(grammar_type=MarkRef, grammar_name='from')
    def from_(value):
        """dict : Description of data to visualize

        Note that although the property has the name ``from_`` (using
        ``from`` is invalid Python syntax), the JSON will contain the
        correct property ``from``.
        """

    @grammar(MarkProperties)
    def properties(value):
        """MarkProperties : Mark property set definitions"""

    @grammar(str)
    def key(value):
        """string : Field to use for data binding

        When updating data dynamically, restrict dynamic transitions from
        affecting data with the given key. This can be useful for something
        like scrolling time series. See the Vega examples.
        """

    @grammar(ValueRef)
    def delay(value):
        """ValueRef, number : Transitional delay in milliseconds.
        """

    @grammar(str)
    def ease(value):
        """string : Type of transition easing

        Valid types are ``'linear'``, ``'quad'``, ``'cubic'``, ``'sin'``,
        ``'exp'``, ``'circle'``, and ``'bounce'``, which can be appended
        with the modifiers ``'in'``, ``'out'``, ``'in-out'``, and
        ``'out-in'``. The default is ``'cubic-in-out'``.

        See the documentation for the d3 ease function for more details.
        """


class DataRef(GrammarClass):
    """Definitions for how data is referenced by scales

    Data can be referenced in multiple ways, and sometimes it makes sense to
    reference multiple data fields at once.
    """
    @grammar(str)
    def data(value):
        """string : Name of data-set containing the domain values"""

    @grammar((list, str))
    def field(value):
        """string or list of strings : Reference to desired data field(s)

        If multiple fields are given, then the values of all fields are
        included in the domain.
        """


class Scale(GrammarClass):
    """Definitions for mapping from data space to visual space

    Scales determine the way in which data is mapped from a data space (such
    as numbers, time stamps, etc.) to a visual space (length of a line,
    height of a bar, etc.), for both independent and dependent variables.
    """
    @grammar(str)
    def name(value):
        """string : Unique name for the scale

        This is used for referencing by other components (mainly ``Mark``).
        """

    @grammar(str)
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

    @grammar((list, DataRef))
    def domain(value):
        """list or DataRef : Domain of the scale
        """

    @grammar(grammar_type=(float, int, DataRef), grammar_name='domainMin')
    def domain_min(value):
        """float, int, or DataRef : Minimum domain value

        Only used for quantitative/time scales. This takes precedence over
        the minimum of the ``domain`` property.
        """

    @grammar(grammar_type=(float, int, DataRef),
             grammar_name='domainMax')
    def domain_max(value):
        """float, int, or DataRef : Maximum domain value

        Only used for quantitative/time scales. This takes precedence over
        the maximum of the ``domain`` property.
        """

    @grammar((list, str))
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

    @grammar(grammar_type=(float, int, DataRef), grammar_name='rangeMin')
    def range_min(value):
        """float, int, or DataRef : Minimum range value

        Only used for quantitative/time scales. This takes precedence over
        the minimum of the ``range`` property.
        """

    @grammar(grammar_type=(float, int, DataRef), grammar_name='rangeMax')
    def range_max(value):
        """float, int, or DataRef : Maximum range value

        Only used for quantitative/time scales. This takes precedence over
        the maximum of the ``range`` property.
        """

    @grammar(bool)
    def reverse(value):
        """boolean : If True, flip the scale range"""

    @grammar(bool)
    def round(value):
        """boolean : If True, numeric output values are rounded to
        integers"""

    @grammar(bool)
    def points(value):
        """boolean : If True, distribute ordinal values over evenly spaced
        points between ``range_min`` and ``range_max``

        Ignored for non-ordinal scales.
        """

    @grammar(bool)
    def clamp(value):
        """boolean : If True, values that exceed the domain are clamped to
        within the domain

        Ignored for ordinal scales.
        """

    @grammar((bool, str))
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

    @grammar((float, int))
    def exponent(value):
        """float or int : Exponent for ``'pow'`` scale types

        Ignored for all scale types other than ``'pow'``.
        """

    @grammar(bool)
    def zero(value):
        """boolean : If True, include zero in the domain

        Only valid for quantitative scale types. This is useful if the
        domain is defined as a DataRef that may not include 0 exactly.
        """


class AxisProperties(GrammarClass):
    """Definitions for the rendering of axes

    Like Marks, axis properties can be broken into various subcomponents,
    but instead of events, the axes are divided into major ticks, minor
    ticks, labels, and the axis itself.
    """
    @grammar(grammar_type=PropertySet, grammar_name='majorTicks')
    def major_ticks(value):
        """PropertySet : Definition of major tick marks"""

    @grammar(grammar_type=PropertySet, grammar_name='minorTicks')
    def minor_ticks(value):
        """PropertySet : Definition of minor tick marks"""

    @grammar(PropertySet)
    def label(value):
        """PropertySet : Definition of marks for axis labels"""

    @grammar(PropertySet)
    def axis(value):
        """PropertySet : Definition of axis line style"""


class Axis(GrammarClass):
    """Definitions for axes

    Axes are visual cues that the viewer uses to interpret the marks
    representing the data itself.
    """
    @grammar(str)
    def type(value):
        """string : Type of axis - ``'x'`` or ``'y'``"""
        if value not in ('x', 'y'):
            raise ValueError('Axis.type must be "x" or "y"')

    @grammar(str)
    def scale(value):
        """string : Name of scale used for axis"""

    @grammar(str)
    def orient(value):
        """string : Orientation of the axis

        Should be one of ``'top'``, ``'bottom'``, ``'left'``, or ``'right'``.
        """

    @grammar(str)
    def format(value):
        """string : Formatting to use for axis labels

        See d3's formatting documentation for format pattern.
        """

    @grammar(int)
    def ticks(value):
        """int : Number of ticks to use"""

    @grammar(list)
    def values(value):
        """list of objects in scale's domain : Explicit definitions for
        values

        Values should be in the domain of the Axis's scale. Custom ticks can
        be used by setting ``properties``.
        """

    @grammar((int, float))
    def subdivide(value):
        """int or float : Number of minor ticks in between major ticks

        Only valid for quantitative scales.
        """

    @grammar(grammar_type=(int), grammar_name='tickPadding')
    def tick_padding(value):
        """int : Pixels between ticks and text labels"""

    @grammar(grammar_type=(int), grammar_name='tickSize')
    def tick_size(value):
        """int : Size in pixels of all ticks"""

    @grammar(grammar_type=(int), grammar_name='tickSizeMajor')
    def tick_size_major(value):
        """int : Size in pixels of major ticks"""

    @grammar(grammar_type=(int), grammar_name='tickSizeMinor')
    def tick_size_minor(value):
        """int : Size in pixels of minor ticks"""

    @grammar(grammar_type=(int), grammar_name='tickSizeEnd')
    def tick_size_end(value):
        """int : Size in pixels of end ticks"""

    @grammar(int)
    def offset(value):
        """int : Offset in pixels to displace the edge of the axis from the
        referenced area
        """

    @grammar(AxisProperties)
    def properties(value):
        """AxisProperties : Custom styling for ticks and tick labels
        """
