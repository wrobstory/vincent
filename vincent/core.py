# -*- coding: utf-8 -*-

import json

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


def _assert_is_type(name, value, type):
    """Assert that a value must be a given type."""
    if not isinstance(value, type):
        raise TypeError(name + ' must be a ' + str(type))


class Data(object):

    class LoadError(Exception):
        """Exception for errors on loading data from third-party objects."""
        pass

    def __init__(self, name):
        self._field = {}
        self.name = name

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

    def load_from(self, obj):
        """Load values from an external object."""
        if isinstance(obj, list):
            self.values = obj
        elif pd and isinstance(obj, (pd.Series, pd.DataFrame)):
            self.load_from_pandas(obj)
        elif np and isinstance(obj, np.ndarray):
            self.load_from_numpy(obj)
        else:
            raise ValueError('unknown data type ' + str(type(obj)))

    def load_from_pandas(self, pd_obj):
        if not pd:
            raise self.LoadError('pandas could not be imported')

    def load_from_numpy(self, np_obj):
        if not np:
            raise self.LoadError('numpy could not be imported')
