# -*- coding: utf-8 -*-

from numbers import Number

import six


def _bool_to_str(val, true_value, false_value):
    if val is None:
        return u''
    if val is True:
        return true_value
    if val is False:
        return false_value
    raise TypeError(u'%r is not boolean' % val)


def bool_to_yesno(val):
    return _bool_to_str(val, u'yes', u'no')


def bool_to_onezero(val):
    return _bool_to_str(val, u'1', u'0')


def number_to_str(val):
    if val is None:
        return u''
    if isinstance(val, Number):
        return six.text_type(val)
    raise TypeError(u'%r is not number' % val)


def datetime_to_str(val, str_format=u'%Y-%m-%d %H:%M:%S'):
    if val is None:
        return u''
    try:
        return val.strftime(str_format)
    except AttributeError:
        raise TypeError(u'%r is not datetime' % val)
