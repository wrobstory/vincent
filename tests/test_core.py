# -*- coding: utf-8 -*-

from vincent.core import field_property, Data
import nose.tools as nt

import pandas as pd
import numpy as np


def test_field_property():
    """Field property decorator behaves correctly."""
    validator_fail = False

    class TestFieldClass(object):
        def __init__(self):
            self._field = {}

        @field_property
        def test_field(value):
            if validator_fail:
                raise ValueError('validator failed')

    test = TestFieldClass()
    nt.assert_is_none(test.test_field)
    nt.assert_dict_equal(test._field, {})

    test.test_field = 'testing'
    nt.assert_equal(test.test_field, 'testing')
    nt.assert_dict_equal(test._field, {'test_field': 'testing'})

    del test.test_field
    nt.assert_is_none(test.test_field)
    nt.assert_dict_equal(test._field, {})

    validator_fail = True
    nt.assert_raises_regexp(ValueError, 'validator failed', setattr, test,
                            'test_field', 'testing')


def assert_field_typechecking(field_types, test_obj):
    """Assert that the fields of a test object are correctly type-checked.

    `field_types` should be a list of (name, type) pairs, and `test_obj`
    should be an instance of the object to test.
    """
    class BadType(object):
        pass

    for name, obj in field_types:
        tmp_obj = obj()
        setattr(test_obj, name, tmp_obj)
        nt.assert_equal(getattr(test_obj, name), tmp_obj)
        bad_obj = BadType()
        nt.assert_raises_regexp(TypeError, name + '.*' + obj.__name__,
                                setattr, test_obj, name, bad_obj)
        nt.assert_equal(getattr(test_obj, name), tmp_obj)


class TestData(object):
    def test_field_typechecking(self):
        """Data fields are correctly type-checked"""
        field_types = [
            ('name', str),
            ('url', str),
            ('values', list),
            ('source', str),
            ('transform', list)]

        assert_field_typechecking(field_types, Data('name'))

    def test_pandas_series_loading(self):
        """Pandas Series objects are correctly loaded"""
        test_s = pd.Series(np.random.randn(10))
        test_s.name = 'myname'
        data = Data.from_pandas(test_s)
        expected_values = [
            {Data._default_index_key: x, test_s.name: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, test_s.name)

        new_name = 'diffname'
        data = Data.from_pandas(test_s, name=new_name)
        expected_values = [
            {Data._default_index_key: x, new_name: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, new_name)

        key = 'akey'
        data = Data.from_pandas(test_s, key=key)
        expected_values = [
            {Data._default_index_key: x, key: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, test_s.name)
