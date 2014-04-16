# -*- coding: utf-8 -*-
'''
Test Vincent.vega
-----------------

'''
from datetime import datetime, timedelta
from itertools import product
import time
import json

from vincent.charts import Line
from vincent.core import (grammar, GrammarClass, GrammarDict, KeyedList,
                          LoadError, ValidationError)
from vincent.visualization import Visualization
from vincent.data import Data
from vincent.transforms import Transform
from vincent.properties import PropertySet
from vincent.scales import DataRef, Scale
from vincent.marks import ValueRef, MarkProperties, MarkRef, Mark
from vincent.axes import AxisProperties, Axis
from vincent.legends import LegendProperties, Legend

import nose.tools as nt

import pandas as pd
import numpy as np


sequences = {
    'int': range,
    'float': lambda l: list(map(float, list(range(l)))),
    'char': lambda l: list(map(chr, list(range(97, 97 + l)))),
    'datetime': lambda l: [datetime.now() + timedelta(days=i)
                           for i in range(l)],
    'Timestamp': lambda l: pd.date_range('1/2/2000', periods=l),
    'numpy float': lambda l: list(map(np.float32, list(range(l)))),
    'numpy int': lambda l: list(map(np.int32, list(range(l))))}


def test_keyed_list():
    """Test keyed list implementation"""

    class TestKey(object):
        """Test object for Keyed List"""
        def __init__(self, name=None):
            self.name = name

    key_list = KeyedList(attr_name='name')

    # Basic usage
    test_key = TestKey(name='test')
    key_list.append(test_key)
    nt.assert_equal(test_key, key_list['test'])

    # Bad key
    with nt.assert_raises(KeyError) as err:
        key_list['test_1']
    nt.assert_equal(err.exception.args[0], ' "test_1" is an invalid key')

    # Repeated keys
    test_key_1 = TestKey(name='test')
    key_list.append(test_key_1)
    with nt.assert_raises(ValidationError) as err:
        key_list['test']
    nt.assert_equal(err.expected, ValidationError)
    nt.assert_equal(err.exception.args[0], 'duplicate keys found')

    # Setting keys
    key_list.pop(-1)
    test_key_2 = TestKey(name='test_2')
    key_list['test_2'] = test_key_2
    nt.assert_equal(key_list['test_2'], test_key_2)

    mirror_key_2 = TestKey(name='test_2')
    key_list['test_2'] = mirror_key_2
    nt.assert_equal(key_list['test_2'], mirror_key_2)

    key_list[0] = mirror_key_2
    nt.assert_equal(key_list[0], mirror_key_2)

    # Keysetting errors
    test_key_3 = TestKey(name='test_3')
    with nt.assert_raises(ValidationError) as err:
        key_list['test_4'] = test_key_3
    nt.assert_equal(err.expected, ValidationError)
    nt.assert_equal(err.exception.args[0],
                    "key must be equal to 'name' attribute")

    key_list = KeyedList(attr_name='type')
    test_key_4 = TestKey(name='test_key_4')
    with nt.assert_raises(ValidationError) as err:
        key_list['test_key_4'] = test_key_4
    nt.assert_equal(err.expected, ValidationError)
    nt.assert_equal(err.exception.args[0], 'object must have type attribute')


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
    test_dict = {'axes': [], 'data': [], 'marks': [],
                 'scales': [], 'legends': []}
    test_str = ('{"axes": [], "data": [], "legends": [], '
                '"marks": [], "scales": []}')

    nt.assert_equal(test.grammar(), test_dict)
    print(json.dumps(test.grammar, sort_keys=True))
    nt.assert_equal(json.dumps(test.grammar, sort_keys=True),
                    test_str)
    nt.assert_equal(g_dict.encoder(test), test.grammar)


def assert_grammar_typechecking(grammar_types, test_obj):
    """Assert that the grammar fields of a test object are correctly
    type-checked.

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

    for attr, value in bad_grammar:
        with nt.assert_raises(ValueError) as err:
            setattr(test_obj, attr, value)

        nt.assert_equal(err.expected, ValueError)


def assert_grammar_validation(grammar_errors, test_obj):
    """Check grammar methods for validation errors"""

    for attr, value, error, message in grammar_errors:
        with nt.assert_raises(error) as err:
            setattr(test_obj, attr, value)

        nt.assert_equal(err.exception.args[0], message)


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
        nt.assert_equal(err.exception.args[0],
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

        test_attr = [('data', [1]), ('scales', [1]),
                     ('axes', [1]), ('marks', [1]),
                     ('legends', [1])]

        assert_manual_typechecking(test_attr, Visualization())

    def test_validation(self):
        """Test Visualization validation"""

        test_obj = Visualization()
        with nt.assert_raises(ValidationError) as err:
            test_obj.validate()
        nt.assert_equal(err.exception.args[0],
                        'data must be defined for valid visualization')

        test_obj.data = [Data(name='test'), Data(name='test')]
        with nt.assert_raises(ValidationError) as err:
            test_obj.validate()
        nt.assert_equal(err.exception.args[0],
                        'data has duplicate names')

    def test_axis_labeling(self):
        """Test convenience method for axis label setting"""

        # With Axes already in place
        test_obj = Visualization()
        test_obj.axes.extend([Axis(type='x'), Axis(type='y')])
        test_obj.axis_titles(x="test1", y="test2")
        nt.assert_equals(test_obj.axes['x'].title, 'test1')
        nt.assert_equals(test_obj.axes['y'].title, 'test2')

        # With no Axes already defined
        del test_obj.axes[0]
        del test_obj.axes[0]
        test_obj.axis_titles(x="test1", y="test2")
        nt.assert_equals(test_obj.axes['x'].title, 'test1')
        nt.assert_equals(test_obj.axes['y'].title, 'test2')

    def test_axis_properties(self):

        test_vis = Visualization()
        with nt.assert_raises(ValueError) as err:
            test_vis.x_axis_properties(title_size=20, label_angle=30)
        nt.assert_equals(err.exception.args[0],
                         'This Visualization has no axes!')
        test_vis.axes = [Axis(scale='x'), Axis(scale='y')]
        test_vis.x_axis_properties(title_size=20, title_offset=10,
                                   label_angle=30, color='#000')
        test_vis.y_axis_properties(title_size=20, title_offset=10,
                                   label_angle=30, color='#000')

        def check_axis_colors():
            for axis in test_vis.axes:
                props = axis.properties
                for prop in [props.title.fill, props.labels.fill]:
                    nt.assert_equals(getattr(prop, 'value'), '#000')
                for prop in [props.axis.stroke, props.major_ticks.stroke,
                             props.minor_ticks.stroke, props.ticks.stroke]:
                    nt.assert_equals(getattr(prop, 'value'), '#000')

        for axis in test_vis.axes:
            props = axis.properties
            nt.assert_equals(props.labels.angle.value, 30)
            nt.assert_equals(props.title.font_size.value, 20)
            nt.assert_equals(props.title.dy.value, 10)
        check_axis_colors()

        test_vis.axes = [Axis(scale='x'), Axis(scale='y')]
        test_vis.common_axis_properties(color='#000')
        for axis in test_vis.axes:
            check_axis_colors()

    def test_legends(self):
        test_vis = Visualization()
        test_vis.legend(title='Test', text_color='#000')
        nt.assert_equals(test_vis.legends[0].title, 'Test')
        nt.assert_equals(test_vis.legends[0].properties.labels.fill.value,
                         '#000')
        nt.assert_equals(test_vis.legends[0].properties.title.fill.value,
                         '#000')

    def test_colors(self):
        test_vis = Line([1, 2, 3])
        rng = ['foo', 'bar']
        test_vis.colors(range_=rng)
        nt.assert_equals(test_vis.scales['color'].range, rng)

    def test_to_json(self):
        """Test JSON to string"""

        pretty = '''{
          "marks": [],
          "axes": [],
          "data": [],
          "scales": [],
          "legends": []
        }'''

        test = Visualization()
        actual, tested = json.loads(pretty), json.loads(test.to_json())
        nt.assert_dict_equal(actual, tested)


class TestData(object):
    """Test the Data class"""

    def test_grammar_typechecking(self):
        """Data fields are correctly type-checked"""
        grammar_types = [
            ('name', [str]),
            ('url', [str]),
            ('values', [list]),
            ('source', [str]),
            ('transform', [list])]

        assert_grammar_typechecking(grammar_types, Data('name'))

    def test_validate(self):
        """Test Data name validation"""
        test_obj = Data()
        del test_obj.name
        nt.assert_raises(ValidationError, test_obj.validate)

    def test_serialize(self):
        """Objects are serialized to JSON-compatible objects"""

        def epoch(obj):
            """Convert to JS Epoch time"""
            return int(time.mktime(obj.timetuple())) * 1000

        types = [('test', str, 'test'),
                 (pd.Timestamp('2013-06-08'), int,
                  epoch(pd.Timestamp('2013-06-08'))),
                 (datetime.utcnow(), int, epoch(datetime.utcnow())),
                 (1, int, 1),
                 (1.0, float, 1.0),
                 (np.float32(1), float, 1.0),
                 (np.int32(1), int, 1),
                 (np.float64(1), float, 1.0),
                 (np.int64(1), int, 1)]

        for puts, pytype, gets in types:
            nt.assert_equal(Data.serialize(puts), gets)

        class BadType(object):
            """Bad object for type warning"""

        test_obj = BadType()
        with nt.assert_raises(LoadError) as err:
            Data.serialize(test_obj)
        nt.assert_equals(err.exception.args[0],
                         'cannot serialize index of type BadType')

    def test_pandas_series_loading(self):
        """Pandas Series objects are correctly loaded"""
        # Test valid series types
        name = ['_x', ' name']
        length = [0, 1, 2]
        index_key = [None, 'ix', 1]
        index_types = ['int', 'char', 'datetime', 'Timestamp']
        value_key = [None, 'x', 1]
        value_types = ['int', 'char', 'datetime', 'Timestamp', 'float',
                       'numpy float', 'numpy int']

        series_info = product(name, length, index_key, index_types,
                              value_key, value_types)

        for n, l, ikey, itype, vkey, vtype in series_info:
            index = sequences[itype](l)
            series = pd.Series(sequences[vtype](l), index=index, name=n,)

            vkey = series.name or vkey
            expected = [{'idx': Data.serialize(i), 'col': vkey,
                         'val': Data.serialize(v)}
                        for i, v in zip(index, series)]

            data = Data.from_pandas(series, name=n, series_key=vkey)
            nt.assert_list_equal(expected, data.values)
            nt.assert_equal(n, data.name)
            data.to_json()

        # Missing a name
        series = pd.Series(np.random.randn(10))
        data = Data.from_pandas(series)
        nt.assert_equal(data.name, 'table')

    def test_pandas_dataframe_loading(self):

        # Simple columns/key_on tests
        df = pd.DataFrame({'one': [1, 2, 3], 'two': [6, 7, 8],
                           'three': [11, 12, 13], 'four': [17, 18, 19]})
        get_all = [{'col': 'four', 'idx': 0, 'val': 17},
                   {'col': 'one', 'idx': 0, 'val': 1},
                   {'col': 'three', 'idx': 0, 'val': 11},
                   {'col': 'two', 'idx': 0, 'val': 6},
                   {'col': 'four', 'idx': 1, 'val': 18},
                   {'col': 'one', 'idx': 1, 'val': 2},
                   {'col': 'three', 'idx': 1, 'val': 12},
                   {'col': 'two', 'idx': 1, 'val': 7},
                   {'col': 'four', 'idx': 2, 'val': 19},
                   {'col': 'one', 'idx': 2, 'val': 3},
                   {'col': 'three', 'idx': 2, 'val': 13},
                   {'col': 'two', 'idx': 2, 'val': 8}]
        get1 = [{'col': 'one', 'idx': 0, 'val': 1},
                {'col': 'one', 'idx': 1, 'val': 2},
                {'col': 'one', 'idx': 2, 'val': 3}]
        get2 = [{'col': 'one', 'idx': 0, 'val': 1},
                {'col': 'two', 'idx': 0, 'val': 6},
                {'col': 'one', 'idx': 1, 'val': 2},
                {'col': 'two', 'idx': 1, 'val': 7},
                {'col': 'one', 'idx': 2, 'val': 3},
                {'col': 'two', 'idx': 2, 'val': 8}]
        getkey2 = [{'col': 'one', 'idx': 6, 'val': 1},
                   {'col': 'one', 'idx': 7, 'val': 2},
                   {'col': 'one', 'idx': 8, 'val': 3}]
        getkey3 = [{'col': 'one', 'idx': 11, 'val': 1},
                   {'col': 'two', 'idx': 11, 'val': 6},
                   {'col': 'one', 'idx': 12, 'val': 2},
                   {'col': 'two', 'idx': 12, 'val': 7},
                   {'col': 'one', 'idx': 13, 'val': 3},
                   {'col': 'two', 'idx': 13, 'val': 8}]
        val_all = Data.from_pandas(df)
        val1 = Data.from_pandas(df, columns=['one'])
        val2 = Data.from_pandas(df, columns=['one', 'two'])
        key2 = Data.from_pandas(df, columns=['one'], key_on='two')
        key3 = Data.from_pandas(df, columns=['one', 'two'], key_on='three')

        nt.assert_list_equal(val_all.values, get_all)
        nt.assert_list_equal(val1.values, get1)
        nt.assert_list_equal(val2.values, get2)
        nt.assert_list_equal(key2.values, getkey2)
        nt.assert_list_equal(key3.values, getkey3)

        # Missing a name
        dataframe = pd.DataFrame(np.random.randn(10, 3))
        data = Data.from_pandas(dataframe)
        nt.assert_equal(data.name, 'table')

        # Bad obj
        nt.assert_raises(ValueError, Data.from_pandas, {})

    def test_numpy_loading(self):
        """Numpy ndarray objects are correctly loaded"""
        test_data = np.random.randn(6, 3)
        index = range(test_data.shape[0])
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

        # Bad loads
        with nt.assert_raises(LoadError) as err:
            Data.from_numpy(test_data, 'test', columns, index=range(4))
        nt.assert_equal(err.expected, LoadError)

        columns = ['a', 'b']
        with nt.assert_raises(LoadError) as err:
            Data.from_numpy(test_data, 'test', columns, index)
        nt.assert_equal(err.expected, LoadError)

    def test_from_mult_iters(self):
        """Test set of iterables"""
        test1 = Data.from_mult_iters(x=[0, 1, 2], y=[3, 4, 5], z=[7, 8, 9],
                                     idx='x')
        test2 = Data.from_mult_iters(fruit=['apples', 'oranges', 'grapes'],
                                     count=[12, 16, 54], idx='fruit')
        values1 = [{'col': 'y', 'idx': 0, 'val': 3},
                   {'col': 'y', 'idx': 1, 'val': 4},
                   {'col': 'y', 'idx': 2, 'val': 5},
                   {'col': 'z', 'idx': 0, 'val': 7},
                   {'col': 'z', 'idx': 1, 'val': 8},
                   {'col': 'z', 'idx': 2, 'val': 9}]
        values2 = [{'col': 'count', 'idx': 'apples', 'val': 12},
                   {'col': 'count', 'idx': 'oranges', 'val': 16},
                   {'col': 'count', 'idx': 'grapes', 'val': 54}]

        nt.assert_list_equal(test1.values, values1)
        nt.assert_list_equal(test2.values, values2)

        # Iter errors
        nt.assert_raises(ValueError, Data.from_mult_iters, x=[0], y=[1, 2])

    def test_from_iter(self):
        """Test data from single iterable"""
        test_list = Data.from_iter([10, 20, 30])
        test_dict = Data.from_iter({
            'apples': 10, 'bananas': 20, 'oranges': 30})
        get1 = [{'col': 'data', 'idx': 0, 'val': 10},
                {'col': 'data', 'idx': 1, 'val': 20},
                {'col': 'data', 'idx': 2, 'val': 30}]
        get2 = [{'col': 'data', 'idx': 'apples', 'val': 10},
                {'col': 'data', 'idx': 'bananas', 'val': 20},
                {'col': 'data', 'idx': 'oranges', 'val': 30}]
        nt.assert_list_equal(test_list.values, get1)
        nt.assert_list_equal(test_dict.values, get2)

    def test_serialize_error(self):
        """Test serialization error"""

        class badType(object):
            """I am a bad actor"""

        broken = badType()

        nt.assert_raises(LoadError, Data.serialize, broken)

    def test_keypairs(self):
        Data.keypairs([0, 10, 20, 30, 40])
        Data.keypairs(((0, 1), (0, 2), (0, 3)))
        Data.keypairs({'A': 10, 'B': 20, 'C': 30, 'D': 40, 'E': 50})


class TestTransform(object):
    """Test the Transform class"""

    def test_grammar_typechecking(self):
        """Transform field typechecking"""
        grammar_types = [
            ('fields', [list]), ('from_', [str]),
            ('as_', [list]), ('keys', [list]), ('sort', [str]),
            ('test', [str]), ('field', [str]), ('expr', [str]),
            ('by', [str, list]), ('value', [str]), ('median', [bool]),
            ('with_', [str]), ('key', [str]), ('with_key', [str]),
            ('links', [str]), ('size', [list]), ('iterations', [int]),
            ('charge', [int, str]), ('link_distance', [int, str]),
            ('link_strength', [int, str]), ('friction', [int, float]),
            ('theta', [int, float]), ('gravity', [int, float]),
            ('alpha', [int, float]), ('point', [str]),
            ('height', [str])]

        assert_grammar_typechecking(grammar_types, Transform())


class TestValueRef(object):
    """Test the ValueRef class"""

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
        nt.assert_equal(json.dumps(props, sort_keys=True),
                        vref.to_json(pretty_print=False))

        props = {
            'value': 'test-value',
            'field': 'test-field',
            'scale': 'test-scale',
            'mult': 1.2,
            'offset': 4,
            'band': True}
        vref = ValueRef(**props)
        nt.assert_equal(json.dumps(props, sort_keys=True),
                        vref.to_json(pretty_print=False))


class TestPropertySet(object):
    """Test the PropertySet Class"""

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

    def test_validation_checking(self):
        """ValueRef fields are grammar-checked"""

        grammar_errors = [('fill_opacity', ValueRef(value=-1), ValueError,
                           'fill_opacity must be between 0 and 1'),
                          ('fill_opacity', ValueRef(value=2), ValueError,
                           'fill_opacity must be between 0 and 1'),
                          ('stroke_width', ValueRef(value=-1), ValueError,
                           'stroke width cannot be negative'),
                          ('stroke_opacity', ValueRef(value=-1), ValueError,
                           'stroke_opacity must be between 0 and 1'),
                          ('stroke_opacity', ValueRef(value=2), ValueError,
                           'stroke_opacity must be between 0 and 1'),
                          ('size', ValueRef(value=-1), ValueError,
                           'size cannot be negative')]

        assert_grammar_validation(grammar_errors, PropertySet())

        bad_shape = ValueRef(value="BadShape")
        nt.assert_raises(ValueError, PropertySet, shape=bad_shape)

    def test_manual_typecheck(self):
        """Test manual typechecking for elements like marks"""

        test_attr = [('fill', ValueRef(value=1)),
                     ('fill_opacity', ValueRef(value='str')),
                     ('stroke', ValueRef(value=1)),
                     ('stroke_width', ValueRef(value='str')),
                     ('stroke_opacity', ValueRef(value='str')),
                     ('size', ValueRef(value='str')),
                     ('shape', ValueRef(value=1)),
                     ('path', ValueRef(value=1))]

        assert_manual_typechecking(test_attr, PropertySet())


class TestMarkProperties(object):
    """Test the MarkProperty Class"""

    def test_grammar_typechecking(self):
        """Test grammar of MarkProperty"""

        fields = ['enter', 'exit', 'update', 'hover']
        grammar_types = [(f, [PropertySet]) for f in fields]
        assert_grammar_typechecking(grammar_types, MarkProperties())


class TestMarkRef(object):
    """Test the MarkRef Class"""

    def test_grammar_typechecking(self):
        """Test grammar of MarkRef"""

        grammar_types = [('data', [str]), ('transform', [list])]
        assert_grammar_typechecking(grammar_types, MarkRef())


class TestMark(object):
    """Test Mark Class"""

    def test_grammar_typechecking(self):
        """Test grammar of Mark"""

        grammar_types = [('name', [str]), ('description', [str]),
                         ('from_', [MarkRef]),
                         ('properties', [MarkProperties]), ('key', [str]),
                         ('key', [str]), ('delay', [ValueRef]),
                         ('ease', [str]), ('marks', [list]),
                         ('scales', [list, KeyedList])]
        assert_grammar_typechecking(grammar_types, Mark())

    def test_validation_checking(self):
        """Mark fields are grammar checked"""

        nt.assert_raises(ValueError, Mark, type='panda')


class TestDataRef(object):
    """Test DataRef class"""

    def test_grammar_typechecking(self):
        """Test grammar of DataRef"""

        grammar_types = [('data', [str]), ('field', [str])]
        assert_grammar_typechecking(grammar_types, DataRef())


class TestScale(object):
    """Test Scale class"""

    def test_grammar_typechecking(self):
        """Test grammar of Scale"""

        grammar_types = [('name', [str]), ('type', [str]),
                         ('domain', [list, DataRef]),
                         ('domain_min', [float, int, DataRef]),
                         ('domain_max', [float, int, DataRef]),
                         ('range', [list, str]),
                         ('range_min', [float, int, DataRef]),
                         ('range_max', [float, int, DataRef]),
                         ('reverse', [bool]), ('round', [bool]),
                         ('points', [bool]), ('clamp', [bool]),
                         ('nice', [bool, str]),
                         ('exponent', [float, int]),
                         ('zero', [bool])]

        assert_grammar_typechecking(grammar_types, Scale())


class TestAxisProperties(object):
    """Test AxisProperties Class"""

    def test_grammar_typechecking(self):
        """Test grammar of AxisProperties"""

        grammar_types = [('major_ticks', [PropertySet]),
                         ('minor_ticks', [PropertySet]),
                         ('labels', [PropertySet]),
                         ('axis', [PropertySet])]

        assert_grammar_typechecking(grammar_types, AxisProperties())


class TestAxis(object):
    """Test Axis Class"""

    def test_grammar_typechecking(self):
        """Test grammar of Axis"""

        grammar_types = [('title', [str]),
                         ('title_offset', [int]),
                         ('grid', [bool]),
                         ('scale', [str]),
                         ('orient', [str]), ('format', [str]),
                         ('ticks', [int]), ('values', [list]),
                         ('subdivide', [int, float]),
                         ('tick_padding', [int]), ('tick_size', [int]),
                         ('tick_size_major', [int]),
                         ('tick_size_minor', [int]),
                         ('tick_size_end', [int]),
                         ('offset', [int]),
                         ('properties', [AxisProperties])]

        assert_grammar_typechecking(grammar_types, Axis())

    def test_validation_checking(self):
        """Axis fields are grammar checked"""

        nt.assert_raises(ValueError, Axis, type='panda')


class TestLegendProperties(object):
    """Test LegendProperties class"""

    def test_grammar_typechecking(self):
        """Test grammar of LegendProperties"""

        grammar_types = [('title', [PropertySet]),
                         ('labels', [PropertySet]),
                         ('symbols', [PropertySet]),
                         ('gradient', [PropertySet]),
                         ('legend', [PropertySet])]

        assert_grammar_typechecking(grammar_types, LegendProperties())


class TestLegend(object):
    """Test Legend Class"""

    def test_grammar_typechecking(self):
        """Test grammar of Legend"""

        grammar_types = [('size', [str]),
                         ('shape', [str]),
                         ('fill', [str]),
                         ('stroke', [str]),
                         ('title', [str]),
                         ('format', [str]),
                         ('values', [list]),
                         ('properties', [LegendProperties])]

        assert_grammar_typechecking(grammar_types, Legend())

    def test_validation_checking(self):
        """Legend fields are grammar checked"""

        nt.assert_raises(ValueError, Legend, orient='center')
