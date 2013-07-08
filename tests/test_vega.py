# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from itertools import product
import json

from vincent.vega import (KeyedList, ValidationError, GrammarDict, grammar,
                          GrammarClass, Visualization, Data, ValueRef, Mark,
                          PropertySet, Scale, Axis)
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


def test_keyed_list():
    """Test keyed list implementation"""

    class TestKey(object):
        """Test object for Keyed List"""
        def __init__(self, name=None):
            self.name = name

    key_list = KeyedList(attr_name='name')

    #Basic usage
    test_key = TestKey(name='test')
    key_list.append(test_key)
    nt.assert_equal(test_key, key_list['test'])

    #Bad key
    with nt.assert_raises(KeyError) as err:
        key_list['test_1']
    nt.assert_equal(err.exception.message, ' "test_1" is an invalid key')

    #Repeated keys
    test_key_1 = TestKey(name='test')
    key_list.append(test_key_1)
    with nt.assert_raises(ValidationError) as err:
        key_list['test']
    nt.assert_equal(err.expected, ValidationError)
    nt.assert_equal(err.exception.message, 'duplicate keys found')

    #Setting keys
    key_list.pop(-1)
    test_key_2 = TestKey(name='test_2')
    key_list['test_2'] = test_key_2
    nt.assert_equal(key_list['test_2'], test_key_2)

    mirror_key_2 = TestKey(name='test_2')
    key_list['test_2'] = mirror_key_2
    nt.assert_equal(key_list['test_2'], mirror_key_2)

    #Keysetting errors
    test_key_3 = TestKey(name='test_3')
    with nt.assert_raises(ValidationError) as err:
        key_list['test_4'] = test_key_3
    nt.assert_equal(err.expected, ValidationError)
    nt.assert_equal(err.exception.message,
                    "key must be equal to 'name' attribute")

    key_list = KeyedList(attr_name='type')
    test_key_4 = TestKey(name='test_key_4')
    with nt.assert_raises(ValidationError) as err:
        key_list['test_key_4'] = test_key_4
    nt.assert_equal(err.expected, ValidationError)
    nt.assert_equal(err.exception.message, 'object must have type attribute')


def test_grammar():
    """Grammar decorator behaves correctly."""
    validator_fail = False

    class DummyType(object):
        pass

    class TestGrammarClass(object):
        def __init__(self):
            self.grammar = GrammarDict()

        @grammar
        def test_grammar(value):
            if validator_fail:
                raise ValueError('validator failed')

        @grammar(grammar_type=DummyType)
        def test_grammar_with_type(value):
            if validator_fail:
                raise ValueError('validator failed')

        @grammar(grammar_name='a name')
        def test_grammar_with_name(value):
            if validator_fail:
                raise ValueError('validator failed')

    test = TestGrammarClass()
    nt.assert_is_none(test.test_grammar)
    nt.assert_dict_equal(test.grammar, {})

    test.test_grammar = 'testing'
    nt.assert_equal(test.test_grammar, 'testing')
    nt.assert_dict_equal(test.grammar, {'test_grammar': 'testing'})

    del test.test_grammar
    nt.assert_is_none(test.test_grammar)
    nt.assert_dict_equal(test.grammar, {})

    validator_fail = True
    nt.assert_raises_regexp(ValueError, 'validator failed', setattr, test,
                            'test_grammar', 'testing')

    # grammar with type checking
    test = TestGrammarClass()
    validator_fail = False
    dummy = DummyType()
    test.test_grammar_with_type = dummy
    nt.assert_equal(test.test_grammar_with_type, dummy)
    nt.assert_dict_equal(test.grammar, {'test_grammar_with_type': dummy})
    nt.assert_raises_regexp(ValueError, 'must be DummyType', setattr, test,
                            'test_grammar_with_type', 'testing')
    validator_fail = True
    nt.assert_raises_regexp(ValueError, 'validator failed', setattr, test,
                            'test_grammar_with_type', dummy)

    # grammar with field name
    test = TestGrammarClass()
    validator_fail = False
    test.test_grammar_with_name = 'testing'
    nt.assert_equal(test.test_grammar_with_name, 'testing')
    nt.assert_dict_equal(test.grammar, {'a name': 'testing'})
    validator_fail = True
    nt.assert_raises_regexp(ValueError, 'validator failed', setattr, test,
                            'test_grammar_with_name', 'testing')


def test_grammar_dict():
    """Test Vincent Grammar Dict"""

    g_dict = GrammarDict()
    test = Visualization()
    test_dict = {'axes': [], 'data': [], 'marks': [], 'scales': []}
    test_str = '{"marks": [], "axes": [], "data": [], "scales": []}'

    nt.assert_equal(test.grammar(), test_dict)
    nt.assert_equal(str(test.grammar), test_str)
    nt.assert_equal(g_dict.encoder(test), test.grammar)


def assert_grammar_typechecking(grammar_types, test_obj):
    """Assert that the grammar fields of a test object are correctly type-checked.

    `grammar_types` should be a list of (name, type) pairs, and `test_obj`
    should be an instance of the object to test.
    """
    class BadType(object):
        pass

    for name, objects in grammar_types:
        for obj in objects:
            tmp_obj = obj()
            setattr(test_obj, name, tmp_obj)
            nt.assert_equal(getattr(test_obj, name), tmp_obj)
            bad_obj = BadType()
            nt.assert_raises_regexp(ValueError, name + '.*' + obj.__name__,
                                    setattr, test_obj, name, bad_obj)
            nt.assert_equal(getattr(test_obj, name), tmp_obj)


def assert_manual_typechecking(bad_grammar, test_obj):
    """Some attrs use the _assert_is_type func for typechecking"""

    for attr, value, datatype in bad_grammar:
        with nt.assert_raises(ValueError) as err:
            setattr(test_obj, attr, value)

        nt.assert_equal(err.exception.message,
                        '{0}[0] must be {1}'.format(attr, datatype.__name__))


def assert_grammar_validation(grammar_errors, test_obj):
    """Check grammar methods for validation errors"""

    for attr, value, error, message in grammar_errors:
        with nt.assert_raises(error) as err:
            setattr(test_obj, attr, value)

        nt.assert_equal(err.exception.message, message)


class TestGrammarClass(object):
    """Test GrammarClass's built-in methods that aren't tested elsewhere"""

    def test_bad_init(self):
        """Test bad initialization"""
        nt.assert_raises(ValueError, GrammarClass, width=50)

    def test_validation(self):
        """Test validation of grammar"""
        test = Visualization()
        test.axes.append({'bad axes': 'ShouldRaiseError'})
        with nt.assert_raises(ValidationError) as err:
            test.validate()
        nt.assert_equal(err.exception.message,
                        'invalid contents: axes[0] must be Axis')


class TestVisualization(object):
    """Test the Visualization Class"""

    def test_grammar_typechecking(self):
        """Visualization fields are correctly type checked"""

        grammar_types = [('name', [str]),
                         ('width', [int]),
                         ('height', [int]),
                         ('data', [list, KeyedList]),
                         ('scales', [list, KeyedList]),
                         ('axes', [list, KeyedList]),
                         ('marks', [list, KeyedList])]

        assert_grammar_typechecking(grammar_types, Visualization())

    def test_validation_checking(self):
        """Visualization fields are grammar-checked"""

        grammar_errors = [('width', -1, ValueError,
                           'width cannot be negative'),
                          ('height', -1, ValueError,
                           'height cannot be negative'),
                          ('viewport', [1], ValueError,
                           'viewport must have 2 dimensions'),
                          ('viewport', [-1, -1], ValueError,
                           'viewport dimensions cannot be negative'),
                          ('padding', {'top': 2}, ValueError,
                           ('Padding must have keys "top", "left", "right",'
                            ' "bottom".')),
                          ('padding',
                           {'top': 1, 'left': 1, 'right': 1, 'bottom': -1},
                           ValueError, 'Padding cannot be negative.'),
                          ('padding', -1, ValueError,
                           'Padding cannot be negative.')]

        assert_grammar_validation(grammar_errors, Visualization())

    def test_manual_typecheck(self):
        """Test manual typechecking for elements like marks"""

        test_attr = [('data', [1], Data), ('scales', [1], Scale),
                     ('axes', [1], Axis), ('marks', [1], Mark)]

        assert_manual_typechecking(test_attr, Visualization())

    def test_validation(self):
        """Test Visualization validation"""

        test_obj = Visualization()
        with nt.assert_raises(ValidationError) as err:
            test_obj.validate()
        nt.assert_equal(err.exception.message,
                        'data must be defined for valid visualization')

        test_obj.data = [Data(name='test'), Data(name='test')]
        with nt.assert_raises(ValidationError) as err:
            test_obj.validate()
        nt.assert_equal(err.exception.message,
                        'data has duplicate names')


class TestData(object):
    def test_grammar_typechecking(self):
        """Data fields are correctly type-checked"""
        grammar_types = [
            ('name', [str]),
            ('url', [str]),
            ('values', [list]),
            ('source', [str]),
            ('transform', [list])]

        assert_grammar_typechecking(grammar_types, Data('name'))

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

    def test_iter_loading(self):
        pass


class TestValueRef(object):
    def test_grammar_typechecking(self):
        """ValueRef fields are correctly type-checked"""
        grammar_types = [
            ('value', [str]),
            ('value', [int]),
            ('value', [float]),
            ('field', [str]),
            ('scale', [str]),
            ('mult', [int]),
            ('mult', [float]),
            ('offset', [int]),
            ('offset', [float]),
            ('band', [bool])]
        assert_grammar_typechecking(grammar_types, ValueRef())

    def test_json_serialization(self):
        """ValueRef JSON is correctly serialized"""
        vref = ValueRef()
        nt.assert_equal(json.dumps({}), vref.to_json(pretty_print=False))

        props = {
            'value': 'test-value',
            'band': True}
        vref = ValueRef(**props)
        nt.assert_equal(json.dumps(props), vref.to_json(pretty_print=False))

        props = {
            'value': 'test-value',
            'field': 'test-field',
            'scale': 'test-scale',
            'mult': 1.2,
            'offset': 4,
            'band': True}
        vref = ValueRef(**props)
        nt.assert_equal(json.dumps(props), vref.to_json(pretty_print=False))


class TestPropertySet(object):
    def test_grammar_typechecking(self):
        """PropertySet fields are correctly type-checked"""
        # All fields must be ValueRef for Mark properties
        fields = [
            'x', 'x2', 'width', 'y', 'y2', 'height', 'opacity', 'fill',
            'fill_opacity', 'stroke', 'stroke_width', 'stroke_opacity',
            'size', 'shape', 'path', 'inner_radius', 'outer_radius',
            'start_angle', 'end_angle', 'interpolate', 'tension', 'url',
            'align', 'baseline', 'text', 'dx', 'dy', 'angle', 'font',
            'font_size', 'font_weight', 'font_style']
        grammar_types = [(f, [ValueRef]) for f in fields]
        assert_grammar_typechecking(grammar_types, PropertySet())
