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


class Data(object):

    _default_index_key = '_index'

    class LoadError(Exception):
        """Exception for errors on loading data from third-party objects"""
        pass

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
        _assert_is_type('name', value, str)

    @field_property
    def url(value):
        _assert_is_type('url', value, str)

    @field_property
    def values(value):
        _assert_is_type('values', value, list)

    @field_property
    def source(value):
        _assert_is_type('source', value, str)

    @field_property
    def transform(value):
        _assert_is_type('transform', value, list)

    @classmethod
    def _create_index(cls, key, idx):
        """Convert an index into a JSON-serializable value"""
        if isinstance(idx, str):
            return [(key, idx)]
        elif hasattr(idx, 'timetuple'):
            return [(key, int(time.mktime(idx.timetuple())) * 1000)]
        elif hasattr(idx, '__float__'):
            return [(key, float(idx))]
        elif hasattr(idx, '__int__'):
            return [(key, int(idx))]
        else:
            raise cls.LoadError('cannot serialize index of type '
                                + type(idx).__name__)

    @classmethod
    def _create_value(cls, idx):
        """Convert a value data type into a JSON-serializable value"""
        if isinstance(idx, str):
            return idx
        elif hasattr(idx, '__float__'):
            return float(idx)
        elif hasattr(idx, '__int__'):
            return int(idx)
        else:
            raise cls.LoadError('cannot serialize value of type '
                                + type(idx).__name__)

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
        """
        # Note: There's an experimental JSON encoder floating around in
        # pandas land that hasn't made it into the main branch. This
        # function should be revisited if it ever does.
        if not pd:
            raise cls.LoadError('pandas could not be imported')

        if name:
            data = cls(name=name, **kwargs)
        elif hasattr(pd_obj, 'name') and pd_obj.name:
            data = cls(name=pd_obj.name, **kwargs)
        else:
            raise cls.LoadError(
                'name must be provided as argument or be attribute of '
                'object')

        index_key = index_key or cls._default_index_key

        if isinstance(pd_obj, pd.Series):
            data_key = data_key or data.name
            data.values = [
                dict(cls._create_index(index_key, i) +
                     [(data_key, cls._create_value(v))])
                for i, v in pd_obj.iterkv()]
        elif isinstance(pd_obj, pd.DataFrame):
            # We have to explicitly convert the column names to strings
            # because the json serializer doesn't allow for integer keys.
            data.values = [
                dict(cls._create_index(index_key, i) +
                     [(str(k), v) for k, v in row.iterkv()])
                for i, row in pd_obj.iterrows()]
        else:
            raise ValueError('cannot load from data type '
                             + type(pd_obj).__name__)
        return data

    @classmethod
    def from_numpy(cls, np_obj, name, columns, index=None, index_key=None,
                   **kwargs):
        """Load values from a NumPy array
        """
        if not np:
            raise cls.LoadError('numpy could not be imported')
        _assert_is_type('numpy object', np_obj, np.ndarray)

        # Integer index if none is provided
        index = index or range(np_obj.shape[0])
        # Explicitly map dict-keys to strings for JSON serializer.
        columns = map(str, columns)

        index_key = index_key or cls._default_index_key

        if len(index) != np_obj.shape[0]:
            raise cls.LoadError(
                'length of index must be equal to number of rows of array')
        elif len(columns) != np_obj.shape[1]:
            raise cls.LoadError(
                'length of columns must be equal to number of columns of '
                'array')

        data = cls(name=name, **kwargs)
        data.values = [
            dict(cls._create_index(index_key, idx) +
                 [(col, x) for col, x in zip(columns, row)])
            for idx, row in zip(index, np_obj.tolist())]

        return data

    def to_json(self, overwrite_url=False):
        """Convert data to JSON

        Parameters
        ----------
        overwrite_url : boolean
            If False (default) and a file already exists at the `url`, it
            will not be overwritten and an exception will be raised. If
            True, the file is overwritten. If `url` is None, then this has
            no effect.
        """
        #TODO: support writing to separate file
        return json.dumps(self._field)
