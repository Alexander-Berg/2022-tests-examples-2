# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from nose_parameterized import (
    param,
    parameterized,
)


def name_parameterized_func(func, num, p):
    base_name = func.__name__
    formatted_args = list()
    for value in p.args:
        formatted_args.append(repr(value))
    for name, value in p.kwargs.iteritems():
        formatted_args.append('%s=%r' % (name, value))
    name_suffix = '(%s)' % ', '.join(formatted_args)
    return str(base_name + name_suffix)


def parameterized_expand(params):
    return parameterized.expand(params, name_parameterized_func)


__all__ = [
    'param',
    'parameterized',
]
