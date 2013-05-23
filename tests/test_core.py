# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from itertools import product

from vincent.core import field_property, Data
import nose.tools as nt

import pandas as pd
import numpy as np


sequences = {
    'int': range,
    'float': lambda l: map(float, range(l)),
    'char': lambda l: map(chr, range(97, 97 + l)),
    'datetime': lambda l: [datetime.now() + timedelta(days=i)
                           for i in xrange(l)],
    'Timestamp': lambda l: pd.date_range('1/2/2000', periods=l),
    'numpy float': lambda l: map(np.float32, range(l)),
    'numpy int': lambda l: map(np.int32, range(l))}


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

    def test_serialize(self):
        """Objects are serialized to JSON-compatible objects"""
        pass

    def test_pandas_series_loading(self):
        """Pandas Series objects are correctly loaded"""
        # Test valid series types
        name = ['_x', ' name']
        length = [0, 1, 2]
        index_key = [None, 'ix', 1]
        index_types = ['int', 'char', 'datetime', 'Timestamp']
        value_key = [None, 'x', 1]
        value_types = [
            'int', 'char', 'datetime', 'Timestamp', 'float',
            'numpy float', 'numpy int']

        series_info = product(
            name, length, index_key, index_types, value_key, value_types)
        for n, l, ikey, itype, vkey, vtype in series_info:
            index = sequences[itype](l)
            series = pd.Series(sequences[vtype](l), index=index, name=n,)

            ikey = ikey or Data._default_index_key
            vkey = vkey or series.name
            expected = [
                {ikey: Data.serialize(i), vkey: Data.serialize(v)}
                for i, v in zip(index, series)]

            data = Data.from_pandas(series, name=n, index_key=ikey,
                                    data_key=vkey)
            nt.assert_list_equal(expected, data.values)
            nt.assert_equal(n, data.name)
            data.to_json()

        # Missing a name
        series = pd.Series(np.random.randn(10))
        data = Data.from_pandas(series)
        nt.assert_equal(data.name, 'table')

    def test_pandas_dataframe_loading(self):
        """Pandas DataFrame objects are correctly loaded"""
        name = ['_x']
        length = [0, 1, 2]
        index_key = [None, 'ix', 1]
        index_types = ['int', 'char', 'datetime', 'Timestamp']
        column_types = ['int', 'char', 'datetime', 'Timestamp']

        # Leaving out some basic types here because we're not worried about
        # serialization.
        value_types = [
            'char', 'datetime', 'Timestamp', 'numpy float', 'numpy int']

        dataframe_info = product(
            name, length, length, index_key, index_types, column_types,
            value_types)
        for n, rows, cols, ikey, itype, ctype, vtype in dataframe_info:
            index = sequences[itype](rows)
            columns = sequences[ctype](cols)
            series = {
                c: pd.Series(sequences[vtype](rows), index=index, name=n)
                for c in columns}
            dataframe = pd.DataFrame(series)

            ikey = ikey or Data._default_index_key
            if cols == 0:
                expected = []
            else:
                expected = [
                    dict([(ikey, Data.serialize(index[i]))] +
                         [(str(c), Data.serialize(series[c][i]))
                          for c in columns])
                    for i in xrange(rows)]

            data = Data.from_pandas(dataframe, name=n, index_key=ikey)
            nt.assert_list_equal(expected, data.values)
            nt.assert_equal(n, data.name)
            data.to_json()

        # Missing a name
        dataframe = pd.DataFrame(np.random.randn(10, 3))
        data = Data.from_pandas(dataframe)
        nt.assert_equal(data.name, 'table')

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
