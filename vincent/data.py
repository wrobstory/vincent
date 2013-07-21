# -*- coding: utf-8 -*-
"""

Data: Vincent Data Class for data importing and Vega Data type

"""
from __future__ import (print_function, division)
import time
import copy
from core import _assert_is_type, ValidationError, grammar, GrammarClass, LoadError

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None


class Data(GrammarClass):
    """Data container for visualization

    The Vega document may contain the data itself or a reference to a URL
    containing the data and formatting instructions. Additionally, new data
    can be created from old data via the transform fields.
    """
    _default_index_key = 'idx'

    def __init__(self, name=None, **kwargs):
        """Initialize a Data object

        Parameters
        ----------
        name : string, default None
            Name of the data set. If None (default), then the name will be
            set to ``'table'``.
        **kwargs : dict
            Attributes to set on initialization.
        """
        super(self.__class__, self).__init__(**kwargs)
        self.name = name if name else 'table'

    @grammar(str)
    def name(value):
        """string : Name of the data

        This is used by other components (``Mark``, etc.) for reference.
        """

    @grammar(str)
    def url(value):
        """string : URL from which to load the data

            This can be used as an alternative to defining the data in the
            ``values`` attribute.
        """

    @grammar(list)
    def values(value):
        """list : Data contents

        Data is represented in tabular form, where each element of
        ``values`` corresponds to a row of data.  Each row of data is
        represented by a dict or a raw number. The keys of the dict are
        columns and the values are individual data points. The keys of the
        dicts must be strings for the data to correctly serialize to JSON.

        The data will often have an "index" column representing the
        independent variable, with the remaining columns representing the
        dependent variables, though this is not required. The ``Data`` class
        itself, however, is agnostic to which columns are dependent and
        independent.

        For example, the values attribute
        ``[{'x': 0, 'y': 3.2}, {'x': 1, 'y': 1.3}]``
        could represent two rows of two variables - possibly an independent
        variable ``'x'`` and a dependent variable ``'y'``.
        For simple data sets, an alternative values attribute could be a
        simple list of numbers such as
        ``[2, 12, 3, 5]``.

        It may be more convenient to load data from pandas or NumPy objects.
        See the methods :func:`Data.from_pandas` and
        :func:`Data.from_numpy`.
        """
        for row in value:
            _assert_is_type('values row', row, (float, int, dict))

    @grammar(str)
    def source(value):
        """string : ``name`` field of another data set

        This is typically used with data transforms to create new data
        values.
        """

    @grammar(list)
    def transform(value):
        """list : transforms to apply to the data

        Note: Transform-relational classes are not yet implemented.
        """

    @grammar(dict)
    def format(value):
        """dict : information about the data format

        This is only used when loading data from the ``url`` attribute.
        Format-relational classes are not yet implemented.
        """

    def validate(self, *args):
        """Validate contents of class
        """
        super(self.__class__, self).validate(*args)
        if not self.name:
            raise ValidationError('name is required for Data')

    @staticmethod
    def serialize(obj):
        """Convert an object into a JSON-serializable value

        This is used by the ``from_pandas`` and ``from_numpy`` functions to
        convert data to JSON-serializable types when loading.
        """
        if isinstance(obj, str):
            return obj
        elif hasattr(obj, 'timetuple'):
            return int(time.mktime(obj.timetuple())) * 1000
        elif hasattr(obj, 'item'):
            return obj.item()
        elif hasattr(obj, '__float__'):
            return float(obj)
        elif hasattr(obj, '__int__'):
            return int(obj)
        else:
            raise LoadError('cannot serialize index of type '
                            + type(obj).__name__)

    @classmethod
    def from_pandas(cls, data, columns=None, key_on='idx', name=None,
                    index_key=None, series_key=None, **kwargs):
        """Load values from a pandas ``Series`` or ``DataFrame`` object

        Parameters
        ----------
        data : pandas ``Series`` or ``DataFrame``
            Pandas object to import data from.
        columns: list, default None
            DataFrame columns to convert to Data. Keys default to col names.
            If columns are given and on_index is False, x-axis data will
            default to the first column.
        key_on: string, default 'index'
            Value to key on for x-axis data. Defaults to index.
        name : string, default None
            Applies to the ``name`` attribute of the generated class. If
            ``None`` (default), then the ``name`` attribute of ``pd_obj`` is
            used if it exists, or ``'table'`` if it doesn't.
        index_key : string, default None
            If keying by index, custom key name for the index. Defaults to
            index.name, then finally 'idx'
        series_key : string, default None
            Applies only to ``Series``. If ``None`` (default), then defaults to
            'y'. Otherwise, the data will be indexed by this key. For example, if
            ``series_key`` is ``'x'``, then the entries of the ``values`` list
            will be ``{'idx': ..., 'x': ...}``.
        **kwargs : dict
            Additional arguments passed to the :class:`Data` constructor.
        """
        # Note: There's an experimental JSON encoder floating around in
        # pandas land that hasn't made it into the main branch. This
        # function should be revisited if it ever does.
        if not pd:
            raise LoadError('pandas could not be imported')
        if not hasattr(data, 'index'):
            raise ValueError('Please load a Pandas object.')

        if name:
            vega_data = cls(name=name, **kwargs)
        elif hasattr(data, 'name') and data.name:
            vega_data = cls(name=data.name, **kwargs)
        else:
            vega_data = cls(name='table', **kwargs)

        pd_obj = data.copy()
        if columns:
            pd_obj = data[columns]
        if key_on != 'idx':
            pd_obj.index = data[key_on]

        index_key = index_key or pd_obj.index.name or cls._default_index_key

        if isinstance(pd_obj, pd.Series):
            data_key = series_key or data.name
            vega_data.values = [
                dict([(index_key, cls.serialize(i))] +
                     [(data_key, cls.serialize(v))])
                for i, v in pd_obj.iterkv()]
        elif isinstance(pd_obj, pd.DataFrame):
            # We have to explicitly convert the column names to strings
            # because the json serializer doesn't allow for integer keys.
            vega_data.values = [
                dict([(index_key, cls.serialize(i))] +
                     [(str(k), cls.serialize(v)) for k, v in row.iterkv()])
                for i, row in pd_obj.iterrows()]
        else:
            raise ValueError('cannot load from data type '
                             + type(pd_obj).__name__)
        return vega_data

    @classmethod
    def from_numpy(cls, np_obj, name, columns, index=None, index_key=None,
                   **kwargs):
        """Load values from a numpy array

        Parameters
        ----------
        np_obj : numpy.ndarray
            numpy array to load data from
        name : string
            ``name`` field for the data
        columns : iterable
            Sequence of column names, from left to right. Must have same
            length as the number of columns of ``np_obj``.
        index : iterable, default None
            Sequence of indices from top to bottom. If ``None`` (default),
            then the indices are integers starting at 0. Must have same
            length as the number of rows of ``np_obj``.
        index_key : string, default None
            Key to use for the index. If ``None`` (default), ``idx`` is
            used.
        **kwargs : dict
            Additional arguments passed to the :class:`Data` constructor

        Notes
        -----
        The individual elements of ``np_obj``, ``columns``, and ``index``
        must return valid values from :func:`Data.serialize`.
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

    @classmethod
    def from_mult_iters(cls, name=None, stacked=False, **kwargs):
        """Load values from multiple iters

        Parameters
        ----------
        name : string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.
        stacked: bool, default False
            Pass true to stack all passed iters on the common axis of the
            first iter.
        **kwargs : dict of iterables
            The ``values`` field will contain dictionaries with keys for
            each of the iterables provided. For example,

                d = Data.from_iters(x=[0, 1, 5], y=(10, 20, 30))

            would result in ``d`` having a ``values`` field with

                [{'x': 0, 'y': 10}, {'x': 1, 'y': 20}, {'x': 5, 'y': 30}]

            If the iterables are not the same length, then ValueError is
            raised.
        """
        if not name:
            name = 'table'

        lengths = [len(v) for v in kwargs.values()]

        if len(set(lengths)) != 1:
            raise ValueError('iterables must all be same length')
        else:
            values = [{} for i in xrange(lengths[0])]

        for k, v in kwargs.iteritems():
            for i, x in enumerate(v):
                values[i][k] = x

        return cls(name, values=values)

    @classmethod
    def stacked(cls, data=None, name=None, stack_on=None, on_index=True, **kwargs):
        """"Load values from a Pandas DataFrame, a dict of iters, or multiple
        iters into stacked values for stacked area/bar charts

        Parameters
        ----------
        data: Pandas DataFrame or dict of iters, default None
            Pandas DataFrame or dict of iterables
        name: string, default None
            Name of the dataset. If None, the name will be set to ``'table'``.
        stack_on: string, default None
            Key to identify x-axis on which to stack other values. Can pass
            dict key or Pandas DataFrame column name.
        on_index: boolean, default True
            Pass True to stack Pandas DataFrames on index as common x-axis
        kwargs: dict of iterables
            The ``values`` field will contain dictionaries with keys for
            each of the iterables provided. For example,

                d = Data.from_iters(x=[0, 1, 5], y=(10, 20, 30))

            would result in ``d`` having a ``values`` field with

                [{'x': 0, 'y': 10}, {'x': 1, 'y': 20}, {'x': 5, 'y': 30}]

            If the iterables are not the same length, then ValueError is
            raised.

        Example
        -------
        >>>data = Data.stacked({'x': [0, 1, 2], 'y': [3, 4, 5],
                               'y2': [7, 8, 9]}, stack_on='x')
        >>>data = Data.stacked(df, stack_on='Column1')
        >>>data = Data.stacked(stack_on='x', x=[1,2,3], y=[4,5,6], y2=[7,8,9])

        """

        if hasattr(data, 'name'):
            name = data

        if kwargs:
            if len(set([len(v) for v in kwargs.values()])) != 1:
                raise ValueError('iterables must all be same length')
            data = kwargs

        values = []

        if data is not None:
            if isinstance(data, pd.DataFrame):
                if stack_on and on_index:
                    raise ValueError('Cannot stack on both column and index')
                if hasattr(data, 'name'):
                    name = data.name
                for i, row in data.iterrows():
                    if on_index:
                        key = cls.serialize(i)
                        stack_on = data.index.name or cls._default_index_key
                    else:
                        key = cls.serialize(row[stack_on])
                        row = row.drop(stack_on)
                    for cnt, (idx, val) in enumerate(row.iteritems()):
                        values.append({stack_on: key, idx: cls.serialize(val), 'c': cnt})

            elif isinstance(data, dict):
                copydat = copy.copy(data)
                if not stack_on:
                    raise ValueError('Data passed as a dict must include a key'
                                     ' for `stack_on` on which to stack')
                key = copydat.pop(stack_on)
                for cnt, (k, v) in enumerate(copydat.iteritems()):
                    for idx, val in zip(key, v):
                        values.append({stack_on: idx, k: val, 'c': cnt})

        return cls(name, values=sorted(values, key=lambda x: x['c']))

    @classmethod
    def from_iter(cls, data, name=None):
        """Convenience method for loading data from an iterable.

        Defaults to numerical indexing for x-axis.

        Parameters
        ----------
        data: iterable
            An iterable of data
        name: string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.

        """
        if not name:
            name = 'table'
        values = [{"x": x, "y": y} for x, y in enumerate(data)]
        return cls(name, values=values)

    @classmethod
    def from_iter_pairs(cls, data, name=None):
        """Convenience method for loading data from a tuple of tuples or list of lists.
        Defaults to numerical indexing for x-axis.

        Parameters
        ----------
        data: tuple
            Tuple of paired tuples
        name: string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.

        Example:
        >>>data = Data.from_tuples([(1,2), (3,4), (5,6)])

        """
        if not name:
            name = 'table'
        values = [{"x": x[0], "y": x[1]} for x in data]
        return cls(name, values=values)

    @classmethod
    def from_dict(cls, data, name=None):
        """Convenience method for loading data from dict

        Parameters
        ----------
        data: dict
            Dict of data
        name: string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.

        Example
        -------
        >>>data = Data.from_dict({'apples': 10, 'oranges': 2, 'pears': 3})

        """
        if not name:
            name = 'table'
        values = [{"x": x, "y": y} for x, y in data.iteritems()]
        return cls(name, values=values)

    def to_json(self, validate=False, pretty_print=True, data_path=None):
        """Convert data to JSON

        Parameters
        ----------
        data_path : string
            If not None, then data is written to a separate file at the
            specified path. Note that the ``url`` attribute if the data must
            be set independently for the data to load correctly.

        Returns
        -------
        string
            Valid Vega JSON.
        """
        #TODO: support writing to separate file
        return super(self.__class__, self).to_json(validate, pretty_print)
