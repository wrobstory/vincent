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
    def _create_index(cls, idx):
        """Convert an index into a JSON-serializable value"""
        if isinstance(idx, str):
            return [(cls._default_index_key, idx)]
        elif hasattr(idx, 'timetuple'):
            return [(cls._default_index_key,
                     int(time.mktime(idx.timetuple())) * 1000)]
        elif hasattr(idx, '__float__'):
            return [(cls._default_index_key, float(idx))]
        elif hasattr(idx, '__int__'):
            return [(cls._default_index_key, int(idx))]
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
    def from_pandas(cls, pd_obj, name=None, key=None, **kwargs):
        """Load values from a pandas Series or DataFrame
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

        if isinstance(pd_obj, pd.Series):
            key = key or data.name
            data.values = [
                dict(cls._create_index(i) + [(key, cls._create_value(v))])
                for i, v in pd_obj.iterkv()]
        elif isinstance(pd_obj, pd.DataFrame):
            data.values = [
                dict(cls._create_index(i) +
                     [(str(k), v) for k, v in row.iterkv()])
                for i, row in pd_obj.iterrows()]
        else:
            raise ValueError('cannot load from data type '
                             + type(pd_obj).__name__)
        return data

    @classmethod
    def from_numpy(cls, np_obj, index=None):
        """Load values from a NumPy array
        """
        if not np:
            raise cls.LoadError('numpy could not be imported')
        _assert_is_type('numpy object', np_obj, np.ndarray)

    def to_json(self):
        return json.dumps(self._field)
