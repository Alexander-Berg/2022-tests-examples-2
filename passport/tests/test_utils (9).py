# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.core.validators import Invalid
from passport.backend.core.validators.utils import (
    convert_formencode_invalid_to_error_list,
    fold_whitespace,
    is_printable_ascii,
)


class ConvertFormencodeInvalidTestCase(unittest.TestCase):

    def test_ok_with_error_dict(self):
        leaf_invalid = Invalid(('foundInHistory', u'some message'), 'bad value', None)
        root_invalid = Invalid('root message', 'root value', None, error_dict=dict(leaf_value=leaf_invalid))
        eq_(
            convert_formencode_invalid_to_error_list(root_invalid),
            ['leaf_value.found_in_history'],
        )

    def test_ok_with_error_list(self):
        leaf_invalid = Invalid(('listTooLong', u'some message'), 'bad value', None)
        list_invalid = Invalid('list message', 'list value', None, error_list=[leaf_invalid])
        root_invalid = Invalid('root message', 'root value', None, error_dict=dict(list_value=list_invalid))
        eq_(
            convert_formencode_invalid_to_error_list(root_invalid),
            ['list_value.list_too_long'],
        )

    def test_ok_with_unknown_code_and_field(self):
        invalid = Invalid(('unknown_code', u'some message'), 'bad value', None)
        eq_(
            convert_formencode_invalid_to_error_list(invalid),
            ['None.invalid'],
        )


class IsPrintableAsciiTestCase(unittest.TestCase):
    def test_ok(self):
        for good in (
            'abc0',
            '~!@#$%^&*()_+',
        ):
            ok_(is_printable_ascii(good))

        for bad in (
            '\t',
            '\n',
            '\0',
            '\x19',
            '\x7F',
        ):
            ok_(not is_printable_ascii(bad))


class FoldWhitespaceTestCase(unittest.TestCase):
    @parameterized.expand((
        ('aaa', 'aaa'),
        ('  ', ' '),
        ('   aa    a  ', ' aa a '),
        (u'  ', u' '),
        (u'  \u2005', u' '),
    ))
    def test_ok(self, arg, res):
        eq_(fold_whitespace(arg), res)
