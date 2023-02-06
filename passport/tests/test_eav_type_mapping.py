# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.eav_type_mapping import (
    get_attr_name,
    get_attr_type,
)
import six


if six.PY2:
    import mock
elif six.PY3:
    from unittest import mock


class TestEavTypeMapping(unittest.TestCase):
    def test_get_attr_type__ok(self):
        with mock.patch.dict('passport.backend.core.eav_type_mapping.ATTRIBUTE_NAME_TO_TYPE', values={'x': 1}):
            eq_(get_attr_type('x'), 1)
            eq_(get_attr_type(1), 1)

    def test_invalid_attr_type__error(self):
        with assert_raises(KeyError):
            invalid_attr_type = -1
            get_attr_type(invalid_attr_type)

    def test_invalid_attr_name__error(self):
        with assert_raises(KeyError):
            invalid_attr_name = 'some_attribute.invalid_name'
            get_attr_type(invalid_attr_name)

    def test_get_attr_name__ok(self):
        with mock.patch.dict('passport.backend.core.eav_type_mapping.ATTRIBUTE_TYPE_TO_NAME', values={1: 'x'}):
            eq_(get_attr_name('1'), 'x')

    def test_get_attr_name__fail(self):
        with assert_raises(KeyError):
            with mock.patch.dict('passport.backend.core.eav_type_mapping.ATTRIBUTE_TYPE_TO_NAME', clear=True):
                eq_(get_attr_name(1), 'x')
