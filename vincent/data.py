# -*- coding: utf-8 -*-
"""

Data: Vincent Data Class for data importing and Vega Data type

"""
from __future__ import (print_function, division)
import time
import json
from .core import (
    _assert_is_type,
    ValidationError,
    grammar,
    GrammarClass,
    LoadError
)
from ._compat import str_types

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

    @grammar(str_types)
    def name(value):
        """string : Name of the data

        This is used by other components (``Mark``, etc.) for reference.
        """

    @grammar(str_types)
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

    @grammar(str_types)
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
        if isinstance(obj, str_types):
            return obj
        elif hasattr(obj, 'timetuple'):
            return int(time.mktime(obj.timetuple())) * 1000
        elif hasattr(obj, 'item'):
            return obj.item()
        elif hasattr(obj, '__float__'):
            if isinstance(obj, int):
                return int(obj)
            else:
                return float(obj)
        elif hasattr(obj, '__int__'):
            return int(obj)
        else:
            raise LoadError('cannot serialize index of type '
                            + type(obj).__name__)

    @classmethod
    def from_pandas(cls, data, columns=None, key_on='idx', name=None,
                    series_key='data', grouped=False, records=False, **kwargs):
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
        series_key : string, default 'data'
            Applies only to ``Series``. If ``None`` (default), then defaults to
            data.name. For example, if ``series_key`` is ``'x'``, then the
            entries of the ``values`` list
            will be ``{'idx': ..., 'col': 'x', 'val': ...}``.
        grouped: boolean, default False
            Pass true for an extra grouping parameter
        records: boolean, defaule False
            Requires Pandas 0.12 or greater. Writes the Pandas DataFrame
            using the df.to_json(orient='records') formatting.
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
        else:
            vega_data = cls(name='table', **kwargs)

        pd_obj = data.copy()
        if columns:
            pd_obj = data[columns]
        if key_on != 'idx':
            pd_obj.index = data[key_on]
        if records:
            # The worst
            vega_data.values = json.loads(pd_obj.to_json(orient='records'))
            return vega_data

        vega_data.values = []

        if isinstance(pd_obj, pd.Series):
            data_key = data.name or series_key
            for i, v in pd_obj.iteritems():
                value = {}
                value['idx'] = cls.serialize(i)
                value['col'] = data_key
                value['val'] = cls.serialize(v)
                vega_data.values.append(value)

        elif isinstance(pd_obj, pd.DataFrame):
            # We have to explicitly convert the column names to strings
            # because the json serializer doesn't allow for integer keys.
            for i, row in pd_obj.iterrows():
                for num, (k, v) in enumerate(row.iteritems()):
                    value = {}
                    value['idx'] = cls.serialize(i)
                    value['col'] = cls.serialize(k)
                    value['val'] = cls.serialize(v)
                    if grouped:
                        value['group'] = num
                    vega_data.values.append(value)
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
        columns = list(map(str, columns))

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
    def from_mult_iters(cls, name=None, idx=None, **kwargs):
        """Load values from multiple iters

        Parameters
        ----------
        name : string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.
        idx: string, default None
            Iterable to use for the data index
        **kwargs : dict of iterables
            The ``values`` field will contain dictionaries with keys for
            each of the iterables provided. For example,

                d = Data.from_iters(idx='x', x=[0, 1, 5], y=(10, 20, 30))

            would result in ``d`` having a ``values`` field with

                [{'idx': 0, 'col': 'y', 'val': 10},
                 {'idx': 1, 'col': 'y', 'val': 20}

            If the iterables are not the same length, then ValueError is
            raised.
        """
        if not name:
            name = 'table'

        lengths = [len(v) for v in kwargs.values()]

        if len(set(lengths)) != 1:
            raise ValueError('Iterables must all be same length')

        if not idx:
            raise ValueError('Must provide iter name index reference')

        index = kwargs.pop(idx)
        vega_vals = []
        for k, v in sorted(kwargs.items()):
            for idx, val in zip(index, v):
                value = {}
                value['idx'] = idx
                value['col'] = k
                value['val'] = val
                vega_vals.append(value)

        return cls(name, values=vega_vals)

    @classmethod
    def from_iter(cls, data, name=None):
        """Convenience method for loading data from an iterable.

        Defaults to numerical indexing for x-axis.

        Parameters
        ----------
        data: iterable
            An iterable of data (list, tuple, dict of key/val pairs)
        name: string, default None
            Name of the data set. If None (default), the name will be set to
            ``'table'``.

        """

        if not name:
            name = 'table'
        if isinstance(data, (list, tuple)):
            data = {x: y for x, y in enumerate(data)}

        values = [{'idx': k, 'col': 'data', 'val': v}
                  for k, v in sorted(data.items())]
        return cls(name, values=values)

    @classmethod
    def keypairs(cls, data, columns=None, use_index=False, name=None):
        """This will format the data as Key: Value pairs, rather than the
        idx/col/val style. This is useful for some transforms, and to
        key choropleth map data

        Standard Data Types:
            List: [0, 10, 20, 30, 40]
            Paired Tuples: ((0, 1), (0, 2), (0, 3))
            Dict: {'A': 10, 'B': 20, 'C': 30, 'D': 40, 'E': 50}

        Plus Pandas DataFrame and Series, and Numpy ndarray

        Parameters
        ----------
        data:
            List, Tuple, Dict, Pandas Series/DataFrame, Numpy ndarray
        columns: list, default None
            If passing Pandas DataFrame, you must pass at least one column
            name.If one column is passed, x-values will default to the index
            values.If two column names are passed, x-values are columns[0],
            y-values columns[1].
        use_index: boolean, default False
            Use the DataFrame index for your x-values

        """
        if not name:
            name = 'table'
        cls.raw_data = data

        # Tuples
        if isinstance(data, tuple):
            values = [{"x": x[0], "y": x[1]} for x in data]

        # Lists
        elif isinstance(data, list):
            values = [{"x": x, "y": y}
                      for x, y in zip(range(len(data) + 1), data)]

        # Dicts
        elif isinstance(data, dict) or isinstance(data, pd.Series):
            values = [{"x": x, "y": y} for x, y in sorted(data.items())]

        # Dataframes
        elif isinstance(data, pd.DataFrame):
            if len(columns) > 1 and use_index:
                raise ValueError('If using index as x-axis, len(columns)'
                                 'cannot be > 1')
            if use_index or len(columns) == 1:
                values = [{"x": cls.serialize(x[0]),
                           "y": cls.serialize(x[1][columns[0]])}
                          for x in data.iterrows()]
            else:

                values = [{"x": cls.serialize(x[1][columns[0]]),
                           "y": cls.serialize(x[1][columns[1]])}
                          for x in data.iterrows()]

        # NumPy arrays
        elif isinstance(data, np.ndarray):
            values = cls._numpy_to_values(data)
        else:
            raise TypeError('unknown data type %s' % type(data))

        return cls(name, values=values)

    @staticmethod
    def _numpy_to_values(data):
        '''Convert a NumPy array to values attribute'''
        def to_list_no_index(xvals, yvals):
            return [{"x": x, "y": np.asscalar(y)}
                    for x, y in zip(xvals, yvals)]

        if len(data.shape) == 1 or data.shape[1] == 1:
            xvals = range(data.shape[0] + 1)
            values = to_list_no_index(xvals, data)
        elif len(data.shape) == 2:
            if data.shape[1] == 2:
                # NumPy arrays and matrices have different iteration rules.
                if isinstance(data, np.matrix):
                    xidx = (0, 0)
                    yidx = (0, 1)
                else:
                    xidx = 0
                    yidx = 1

                xvals = [np.asscalar(row[xidx]) for row in data]
                yvals = [np.asscalar(row[yidx]) for row in data]
                values = [{"x": x, "y": y} for x, y in zip(xvals, yvals)]
            else:
                raise ValueError('arrays with > 2 columns not supported')
        else:
            raise ValueError('invalid dimensions for ndarray')

        return values

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
        # TODO: support writing to separate file
        return super(self.__class__, self).to_json(validate=validate,
                                                   pretty_print=pretty_print)
