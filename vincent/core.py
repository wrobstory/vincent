# -*- coding: utf-8 -*-
"""

Core: The core functionality for Vincent to map to Vega grammar

"""
from __future__ import (print_function, division)
import json
from string import Template
from pkg_resources import resource_string

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None

from ._compat import str_types


def initialize_notebook():
    """Initialize the IPython notebook display elements"""
    try:
        from IPython.core.display import display, HTML
    except ImportError:
        print("IPython Notebook could not be loaded.")

    # Thanks to @jakevdp:
    # https://github.com/jakevdp/mpld3/blob/master/mpld3/_display.py#L85
    load_lib = """
                function vct_load_lib(url, callback){
                      if(typeof d3 !== 'undefined' &&
                         url === 'http://d3js.org/d3.v3.min.js'){
                        callback()
                      }
                      var s = document.createElement('script');
                      s.src = url;
                      s.async = true;
                      s.onreadystatechange = s.onload = callback;
                      s.onerror = function(){
                        console.warn("failed to load library " + url);
                        };
                      document.getElementsByTagName("head")[0].appendChild(s);
                };
                var vincent_event = new CustomEvent(
                  "vincent_libs_loaded",
                  {bubbles: true, cancelable: true}
                );
                """
    lib_urls = [
        "'http://d3js.org/d3.v3.min.js'",
        "'http://d3js.org/d3.geo.projection.v0.min.js'",
        "'http://wrobstory.github.io/d3-cloud/d3.layout.cloud.js'",
        "'http://wrobstory.github.io/vega/vega.v1.3.3.js'"
    ]
    get_lib = """vct_load_lib(%s, function(){
                  %s
                  });"""
    load_js = get_lib
    ipy_trigger = "window.dispatchEvent(vincent_event);"
    for elem in lib_urls[:-1]:
        load_js = load_js % (elem, get_lib)
    load_js = load_js % (lib_urls[-1], ipy_trigger)
    html = """
           <script>
               %s
               function load_all_libs(){
                  console.log('Loading Vincent libs...')
                  %s
               };
               if(typeof define === "function" && define.amd){
                    if (window['d3'] === undefined ||
                        window['topojson'] === undefined){
                        require.config(
                            {paths: {
                              d3: 'http://d3js.org/d3.v3.min',
                              topojson: 'http://d3js.org/topojson.v1.min'
                              }
                            }
                          );
                        require(["d3"], function(d3){
                            console.log('Loading Vincent from require.js...')
                            window.d3 = d3;
                            require(["topojson"], function(topojson){
                                window.topojson = topojson;
                                load_all_libs();
                            });
                        });
                    } else {
                        load_all_libs();
                    };
               }else{
                    console.log('Require.js not found, loading manually...')
                    load_all_libs();
               };

           </script>""" % (load_lib, load_js,)
    return display(HTML(html))


def _assert_is_type(name, value, value_type):
    """Assert that a value must be a given type."""
    if not isinstance(value, value_type):
        if type(value_type) is tuple:
            types = ', '.join(t.__name__ for t in value_type)
            raise ValueError('{0} must be one of ({1})'.format(name, types))
        else:
            raise ValueError('{0} must be {1}'
                             .format(name, value_type.__name__))


class ValidationError(Exception):
    """Exception raised with validation fails

    This exception is raised only when the ``validate`` functions of classes
    that inherit from ``FieldClass`` are called. It implies that the classes
    do not contain valid Vega JSON."""
    pass


class KeyedList(list):
    """A list that can optionally be indexed by the ``name`` attribute of
    its elements"""
    def __init__(self, attr_name='name', *args, **kwargs):
        self.attr_name = attr_name
        list.__init__(self, *args, **kwargs)

    def get_keys(self):
        keys = [getattr(x, self.attr_name) for x in self]
        if len(keys) != len(set(keys)):
            raise ValidationError('duplicate keys found')
        return keys

    def __getitem__(self, key):
        if isinstance(key, str_types):
            keys = self.get_keys()
            if key not in keys:
                raise KeyError(' "{0}" is an invalid key'.format(key))
            else:
                return self[keys.index(key)]
        else:
            return list.__getitem__(self, key)

    def __delitem__(self, key):
        if isinstance(key, str_types):
            keys = self.get_keys()
            if key not in keys:
                raise KeyError(' "{0}" is an invalid key'.format(key))
            else:
                list.__delitem__(self, keys.index(key))
        else:
            return list.__delitem__(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, str_types):
            if not hasattr(value, self.attr_name):
                raise ValidationError(
                    'object must have ' + self.attr_name + ' attribute')
            elif getattr(value, self.attr_name) != key:
                raise ValidationError(
                    "key must be equal to '" + self.attr_name +
                    "' attribute")

            keys = self.get_keys()
            if key not in keys:
                self.append(value)
            else:
                list.__setitem__(self, keys.index(key), value)
        else:
            list.__setitem__(self, key, value)


def grammar(grammar_type=None, grammar_name=None):
    """Decorator to define properties that map to the ``grammar``
    dict. This dict is the canonical representation of the Vega grammar
    within Vincent.

    This decorator is intended for classes that map to some pre-defined JSON
    structure, such as axes, data, marks, scales, etc. It is assumed that this
    decorates functions with an instance of ``self.grammar``.

    Parameters
    ----------
    grammar_type : type or tuple of types, default None
        If the argument to the decorated function is not of the given types,
        then a ValueError is raised. No type checking is done if the type is
        None (default).
    grammar_name : string, default None
        An optional name to map to the internal ``grammar`` dict. If None
        (default), then the key for the dict is the name of the function
        being decorated. If not None, then it will be the name specified
        here. This is useful if the expected JSON field name is a Python
        keyword or has an un-Pythonic name.

    This should decorate a "validator" function that should return no value
    but raise an exception if the provided value is not valid Vega grammar. If
    the validator throws no exception, then the value is assigned to the
    ``grammar`` dict.

    The validator function should take only one argument - the value to be
    validated - so that no ``self`` argument is included; the validator
    should not modify the class.

    If no arguments are given, then no type-checking is done the property
    will be mapped to a field with the name of the decorated function.

    The doc string for the property is taken from the validator functions's
    doc string.
    """
    def grammar_creator(validator, name):
        def setter(self, value):
            if isinstance(grammar_type, (type, tuple)):
                _assert_is_type(validator.__name__, value, grammar_type)
            validator(value)
            self.grammar[name] = value

        def getter(self):
            return self.grammar.get(name, None)

        def deleter(self):
            if name in self.grammar:
                del self.grammar[name]

        return property(getter, setter, deleter, validator.__doc__)

    if isinstance(grammar_type, (type, tuple)):
        # If grammar_type is a type, return another decorator.
        def grammar_dec(validator):
            # Make sure to use the grammar name if it's there.
            if grammar_name:
                return grammar_creator(validator, grammar_name)
            else:
                return grammar_creator(validator, validator.__name__)
        return grammar_dec
    elif isinstance(grammar_name, str_types):
        # If grammar_name is a string, use that name and return another
        # decorator.
        def grammar_dec(validator):
            return grammar_creator(validator, grammar_name)
        return grammar_dec
    else:
        # Otherwise we assume that grammar_type is actually the function being
        # decorated.
        return grammar_creator(grammar_type, grammar_type.__name__)


class GrammarDict(dict):
    """The Vega Grammar. When called, obj.grammar returns a Python data
    structure for the Vega Grammar. When printed, obj.grammar returns a
    string representation."""

    def __init__(self, *args, **kwargs):
        """Standard Dict init"""
        dict.__init__(self, *args, **kwargs)

    def encoder(self, obj):
        """Encode grammar objects for each level of hierarchy"""
        if hasattr(obj, 'grammar'):
            return obj.grammar

    def __call__(self):
        """When called, return the Vega grammar as a Python data structure."""

        return json.loads(json.dumps(self, default=self.encoder))

    def __str__(self):
        """String representation of Vega Grammar"""

        return json.dumps(self, default=self.encoder)


class GrammarClass(object):
    """Base class for objects that rely on an internal ``grammar`` dict. This
    dict contains the complete Vega grammar.

    This should be used as a superclass for classes that map to some JSON
    structure. The JSON content is stored in an internal dict named
    ``grammar``.
    """
    def __init__(self, **kwargs):
        """Initialize a GrammarClass

        **kwargs are attribute-value pairs that are set on initialization.
        These will generally be keys for the ``grammar`` dict. If the
        attribute does not already exist as a property, then a
        ``ValueError`` is raised.
        """
        self.grammar = GrammarDict()

        for attr, value in sorted(kwargs.items()):
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise ValueError('unknown keyword argument ' + attr)

    def validate(self):
        """Validate the contents of the object.

        This calls ``setattr`` for each of the class's grammar properties. It
        will catch ``ValueError``s raised by the grammar property's setters
        and re-raise them as :class:`ValidationError`.
        """
        for key, val in self.grammar.items():
            try:
                setattr(self, key, val)
            except ValueError as e:
                raise ValidationError('invalid contents: ' + e.args[0])

    def to_json(self, path=None, html_out=False,
                html_path='vega_template.html', validate=False,
                pretty_print=True):
        """Convert object to JSON

        Parameters
        ----------
        path: string, default None
            Path to write JSON out. If there is no path provided, JSON
            will be returned as a string to the console.
        html_out: boolean, default False
            If True, vincent will output an simple HTML scaffold to
            visualize the vega json output.
        html_path: string, default 'vega_template.html'
            Path for the html file (if html_out=True)
        validate : boolean
            If True, call the object's `validate` method before
            serializing. Default is False.
        pretty_print : boolean
            If True (default), JSON is printed in more-readable form with
            indentation and spaces.

        Returns
        -------
        string
            JSON serialization of the class's grammar properties.
        """
        if validate:
            self.validate()

        if pretty_print:
            dumps_args = {'indent': 2, 'separators': (',', ': ')}
        else:
            dumps_args = {}

        def encoder(obj):
            if hasattr(obj, 'grammar'):
                return obj.grammar

        if html_out:
            template = Template(
                str(resource_string('vincent', 'vega_template.html')))
            with open(html_path, 'w') as f:
                f.write(template.substitute(path=path))

        if path:
            with open(path, 'w') as f:
                json.dump(self.grammar, f, default=encoder, sort_keys=True,
                          **dumps_args)
        else:
            return json.dumps(self.grammar, default=encoder, sort_keys=True,
                              **dumps_args)

    def from_json(self):
        """Load object from JSON

        Not yet implemented.
        """
        raise NotImplementedError()


class LoadError(Exception):
    """Exception for errors on loading data from third-party objects"""
    pass
