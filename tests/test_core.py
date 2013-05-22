# -*- coding: utf-8 -*-
from time import mktime

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
        # Integer-indexed, named series
        test_s = pd.Series(np.random.randn(10))
        test_s.name = 'myname'
        data = Data.from_pandas(test_s)
        expected_values = [
            {Data._default_index_key: x, test_s.name: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, test_s.name)
        data.to_json()

        # Integer-indexed series with new name
        new_name = 'diffname'
        data = Data.from_pandas(test_s, name=new_name)
        expected_values = [
            {Data._default_index_key: x, new_name: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, new_name)
        data.to_json()

        # Integer-indexed series with new data key
        key = 'akey'
        data = Data.from_pandas(test_s, data_key=key)
        expected_values = [
            {Data._default_index_key: x, key: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, test_s.name)
        data.to_json()

        # Integer-indexed series with new index key
        key = 'ikey'
        data = Data.from_pandas(test_s, index_key=key)
        expected_values = [
            {key: x, test_s.name: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, test_s.name)
        data.to_json()

        # Missing a name
        test_s = pd.Series(np.random.randn(10))
        nt.assert_raises_regexp(
            Data.LoadError, 'name', Data.from_pandas, test_s)

        # String-indexed series
        test_s = pd.Series(5., index=['a', 'b', 'c', 'd'], name=new_name)
        data = Data.from_pandas(test_s)
        expected_values = [
            {Data._default_index_key: x, test_s.name: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        data.to_json()

        # Timestamp-indexed series
        test_s = pd.Series(5., index=pd.date_range('1/1/2000', periods=4),
                           name=new_name)
        data = Data.from_pandas(test_s)
        to_js_time = lambda t: int(mktime(t.timetuple()) * 1000)
        expected_values = [
            {Data._default_index_key: to_js_time(x), test_s.name: y}
            for x, y in test_s.iterkv()]
        nt.assert_list_equal(expected_values, data.values)
        data.to_json()

    def test_pandas_dataframe_loading(self):
        """Pandas DataFrame objects are correctly loaded"""
        # Integer-indexed columns and indices
        test_df = pd.DataFrame(np.random.randn(10, 3))
        data = Data.from_pandas(test_df, name='myname')
        idx = lambda i: [(Data._default_index_key, i)]
        expected_values = [
            dict(idx(i) + [(str(k), v) for k, v in row.iterkv()])
            for i, row in test_df.iterrows()]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal(data.name, 'myname')
        data.to_json()

        # Integer-indexed columns and indices with new index key
        test_df = pd.DataFrame(np.random.randn(10, 3))
        key = 'ikey'
        data = Data.from_pandas(test_df, name='myname', index_key=key)
        idx = lambda i: [(key, i)]
        expected_values = [
            dict(idx(i) + [(str(k), v) for k, v in row.iterkv()])
            for i, row in test_df.iterrows()]
        nt.assert_list_equal(expected_values, data.values)
        data.to_json()

        # String-indexed columns and indices
        test_df = pd.DataFrame({
            'x': pd.Series(1., index=['a', 'b', 'c']),
            'y': pd.Series(2., index=['a', 'b', 'c'])})
        data = Data.from_pandas(test_df, name='myname')
        expected_values = [
            {Data._default_index_key: i, 'x': 1., 'y': 2.}
            for i in ['a', 'b', 'c']]
        nt.assert_list_equal(expected_values, data.values)
        data.to_json()

        # Timestamp-indexed dataframe
        idx = pd.date_range('1/1/2000', periods=4)
        test_df = pd.DataFrame({
            'x': pd.Series(1., index=idx),
            'y': pd.Series(2., index=idx)})
        data = Data.from_pandas(test_df, name='myname')
        to_js_time = lambda t: int(mktime(t.timetuple()) * 1000)
        expected_values = [
            {Data._default_index_key: to_js_time(i), 'x': 1., 'y': 2.}
            for i in idx]
        nt.assert_list_equal(expected_values, data.values)
        data.to_json()

        # Missing a name
        test_df = pd.DataFrame(np.random.randn(10, 3))
        nt.assert_raises_regexp(
            Data.LoadError, 'name', Data.from_pandas, test_df)

    def test_numpy_loading(self):
        """Numpy ndarray objects are correctly loaded"""
        test_data = np.random.randn(6, 3)
        index = xrange(test_data.shape[0])
        columns = ['a', 'b', 'c']

        data = Data.from_numpy(test_data, name='name', columns=columns)
        ikey = Data._default_index_key
        expected_values = [
            {ikey: i, 'a': row[0], 'b': row[1], 'c': row[2]}
            for i, row in zip(index, test_data.tolist())]
        nt.assert_list_equal(expected_values, data.values)
        nt.assert_equal('name', data.name)

        index_key = 'akey'
        data = Data.from_numpy(test_data, name='name', columns=columns,
                               index_key=index_key)
        expected_values = [
            {index_key: i, 'a': row[0], 'b': row[1], 'c': row[2]}
            for i, row in zip(index, test_data.tolist())]
        nt.assert_list_equal(expected_values, data.values)

        index = ['a', 'b', 'c', 'd', 'e', 'f']
        data = Data.from_numpy(test_data, name='name', index=index,
                               columns=columns)
        expected_values = [
            {ikey: i, 'a': row[0], 'b': row[1], 'c': row[2]}
            for i, row in zip(index, test_data.tolist())]
        nt.assert_list_equal(expected_values, data.values)
