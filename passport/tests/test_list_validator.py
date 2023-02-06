# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from passport.backend.core import validators
import six


class TestListValidator(unittest.TestCase):
    def setUp(self):
        self.v = validators.ListValidator(validators.Int(), not_in=[1, 2, 3])

    @raises(validators.Invalid)
    def test_invalid_items(self):
        self.v.to_python('10,b,c')

    @raises(validators.Invalid)
    def test_not_in(self):
        self.v.to_python('1,5,6')

    def test_default_empty_value(self):
        eq_(self.v.to_python(''), None)

    def test_empty_value(self):
        v = validators.ListValidator(validators.Int(),
                                     not_in=[1, 2, 3],
                                     if_empty=[])
        eq_(v.to_python(''), [])

    def test_unicode_values(self):
        v = validators.ListValidator(validators.UnicodeString())
        eq_(v.to_python(u'абв,где,жз'), [u'абв', u'где', u'жз'])

    def test_unquote(self):
        v = validators.ListValidator(validators.UnicodeString(), unquote=True)
        eq_(v.to_python('a%2Cb,%20,c%2B%2Cd'), ['a,b', ' ', 'c+,d'])

    def test_unquote_unicode(self):
        v = validators.ListValidator(validators.UnicodeString(), unquote=True)
        eq_(v.to_python(u'%D1%84%D1%8B%D0%B2%D0%B0%2Cb,%20,c%2B%2Cd'), [u'фыва,b', ' ', 'c+,d'])

    def test_unquote_non_ascii(self):
        if six.PY3:
            return
        # одна из строк из формы декодировалась в юникод
        v = validators.ListValidator(validators.UnicodeString(), unquote=True)
        with assert_raises(validators.Invalid):
            v.to_python(u'фыва%2Cb,%20,c%2B%2Cd')

    def test_unquote_bad_utf8(self):
        if six.PY3:
            return
        # одну из строк после декодирования из URL encoding не удалось декодировать из UTF-8
        v = validators.ListValidator(validators.UnicodeString(), unquote=True)
        with assert_raises(validators.Invalid):
            v.to_python(u'%D1%D1%D1%8B%D0%B2%D0%B0%2Cb,%20,c%2B%2Cd')

    def test_valid(self):
        eq_(self.v.to_python('4,5,6'), [4, 5, 6])

    def test_empty_not_in(self):
        v = validators.ListValidator(validators.Int())
        eq_(v.to_python('1,2,3'), [1, 2, 3])

    def test_custom_delimiter(self):
        v = validators.ListValidator(validators.Int(), delimiter='--')
        eq_(v.to_python('1--2--3'), [1, 2, 3])

    def test_repeated_items(self):
        eq_(self.v.to_python('5,5,5'), [5, 5, 5])

    def test_max_items(self):
        v = validators.ListValidator(validators.Int(), max=2)
        eq_(v.to_python('1,1'), [1, 1])

    @raises(validators.Invalid)
    def test_max_items_overflow(self):
        v = validators.ListValidator(validators.Int(), max=2, unique=True)
        v.to_python('1,1,1')  # unique выполняется после проверки числа элементов

    def test_min_items(self):
        v = validators.ListValidator(validators.Int(), min=4)
        eq_(v.to_python('1,1,2,2'), [1, 1, 2, 2])

    def test_min_items_zero_ok(self):
        v = validators.ListValidator(validators.Int(), min=0)
        eq_(v.to_python('1'), [1])

    @raises(validators.Invalid)
    def test_min_items_underflow(self):
        v = validators.ListValidator(validators.Int(), min=2)
        v.to_python('1')

    def test_unique(self):
        v = validators.ListValidator(validators.Int(), unique=True)
        eq_(v.to_python('1,1,1'), [1])
