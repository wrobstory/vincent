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


def field_property(validator):
    """Decorator to define properties that map to the internal `_field`
    dict.

    The argument is a "validator" function that should return no value but
    raise an exception if the provided value is not valid Vega. If the
    validator throws no exception, then the value is assigned to the
    `_field` dict using the validator function name as the key.

    The validator function should take only one argument, so that no `self`
    argument is included - the validator should not modify the class.

    The docstring for the property is taken from the validator's docstring.
    """
    name = validator.__name__

    def setter(self, value):
        validator(value)
        self._field[name] = value

    def getter(self):
        return self._field.get(name, None)

    def deleter(self):
        if name in self._field:
            del self._field[name]

    return property(getter, setter, deleter, validator.__doc__)


def _assert_is_type(name, value, value_type):
    """Assert that a value must be a given type."""
    if not isinstance(value, value_type):
        if type(value_type) is tuple:
            raise TypeError(name + ' must be one of (' +
                            ', '.join(t.__name__ for t in value_type) + ')')
        else:
            raise TypeError(name + ' must be a ' + value_type.__name__)


class LoadError(Exception):
    """Exception for errors on loading data from third-party objects"""
    pass


class Data(object):

    _default_index_key = '_index'

    def __init__(self, name, **kwargs):
        self._field = {}
        self.name = name

        for attr, value in kwargs.iteritems():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise ValueError('unknown keyword argument ' + attr)

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
        a dict. The keys of the dict are columns and the values are
        individual data points. The keys of the dicts must be strings for
        the data to correctly serialize to JSON.

        The data will often have an `index` column representing the
        independent variable, with the remaining columns representing the
        dependent variables, though this is not required. The `Data` class
        itself, however, is agnostic to which columns are dependent and
        independent.

        For example, the values attribute

            [{'x': 0, 'y': 3.2}, {'x': 1, 'y': 1.3}]

        could represent two rows of two variables - possibly an independent
        variable 'x' and a dependent variable 'y'.

        It may be more convenient to load data from pandas or NumPy objects.
        See the functions `Data.from_pandas` and `Data.from_numpy`.
        """
        _assert_is_type('values', value, list)
        for row in value:
            _assert_is_type('values row', row, dict)

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
            (default), then `pd_obj` must have a `name` attribute or a
            `LoadError` is raised.
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
            raise LoadError(
                'name must be provided as argument or be attribute of '
                'object')

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
