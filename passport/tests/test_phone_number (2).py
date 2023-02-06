# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core import validators
from passport.backend.core.types.phone_number import phone_number
from six import iteritems


class TestPhoneNumber(unittest.TestCase):
    def test_parse_ok(self):
        mapping = {
            ('+74951234567', None): '+7 495 123-45-67',
            ('+90 538 377 3877', None): '+90 538 377 3877',
            ('+380 44 279 1967', None): '+380 44 279 1967',
            ('84951234567', 'RU'): '+7 495 123-45-67',
            ('+1 650 253 0000', None): '+1 650-253-0000',
            ('(650) 253 0000', 'US'): '+1 650-253-0000',
            ('(650) 253 0000', 'us'): '+1 650-253-0000',
        }
        for (actual, country), expected in iteritems(mapping):
            v = validators.PhoneNumber()
            data = {'phone_number': actual}
            if country:
                country = country.upper()
            expected_data = {'phone_number': phone_number.PhoneNumber.parse(actual, country)}
            if country:
                data['country'] = country
                expected_data['country'] = country
            eq_(v.to_python(data), expected_data)

    def test_parse_fail(self):
        invalid_phone_numbers = [
            ('+749599999999', None),
            ('+70109999999', None),
            ('9999999', None),
            ('84951234567', None),
            ('84951234567', 'bla'),
            ('aaaa777aaaa2008', 'ru'),
            ('AAAA777AAAA2008', 'ru'),
        ]
        for number, country in invalid_phone_numbers:
            v = validators.PhoneNumber()
            data = {'phone_number': number}
            if country:
                data['country'] = country
            assert_raises(validators.Invalid, v.to_python, data)

    def test_parse_ignores_check(self):
        """PASSP-4199"""
        v = validators.PhoneNumber(allow_impossible=True)
        _phone_number = phone_number.PhoneNumber.parse('+791234567802', 'RU', allow_impossible=True)
        expected_data = {'phone_number': _phone_number}
        eq_(v.to_python({'phone_number': '+791234567802'}), expected_data)

    def test_parse_ignores_check_fail(self):
        invalid_phone_numbers = ['AAAA777AAAA2008', 'aaaa777aaaa2008']
        v = validators.PhoneNumber(allow_impossible=True)
        for number in invalid_phone_numbers:
            assert_raises(validators.Invalid, v.to_python, {'phone_number': number})

    def test_empty_phone_number(self):
        v = validators.PhoneNumber()
        eq_(v.to_python({'phone_number': None}), {'phone_number': None})
