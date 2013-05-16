# -*- coding: utf-8 -*-

import json


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


class Scale(object):
    def __init__(self, name):
        self._field = {}
        self.name = name

    @field_property
    def name(value):
        """Name of the scale."""
        if not isinstance(value, str):
            raise TypeError('name must be string')

    @field_property
    def reverse(value):
        """If `True`, flip the range of the scale."""
        if not isinstance(value, bool):
            raise TypeError('reverse must be bool')

    def to_json(self):
        return json.dumps(self._field)
