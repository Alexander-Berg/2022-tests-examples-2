# -*- coding: utf-8 -*-

import hashlib
from unittest import TestCase

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.frodo.utils import (
    frodo_bool,
    get_hint_metadata,
    get_password_metadata,
    get_phone_number_hash,
    get_string_metadata,
)
from passport.backend.core.test.test_utils import with_settings


@with_settings(FRODO_SECRET_SALT='test-salt')
class FrodoUtilsTestCase(TestCase):
    def test_get_string_metadata(self):
        text = u'abcABCD..-  1;73509АЯфбзжшц'
        expected_metadata = {
            'lat_lower_case_count': 3,
            'lat_upper_case_count': 4,
            'digits_count': 6,
            'lat_vowel_count': 2,
            'lat_consonant_count': 5,
            'vowel_count': 4,
            'consonant_count': 11,
            'space_count': 2,
            'hyphen_count': 1,
            'other_count': 3,
            'length': len(text),
            'ru_upper_case_count': 2,
            'ru_lower_case_count': 6,
            'lat_other_count': 13,
        }

        metadata = get_string_metadata('')
        eq_(len(expected_metadata), len(metadata))
        for key in metadata:
            eq_(metadata[key], 0)

        eq_(expected_metadata, get_string_metadata(text))

    def test_get_password_metadata(self):
        result, resultex = get_password_metadata(None)
        eq_(result, '0.0.0.0.0.0.0.0')
        eq_(resultex, '0.0.0.0.0.0.0.0')

        result, resultex = get_password_metadata('')
        eq_(result, '0.0.0.0')
        eq_(resultex, '0.0.0.0')

        result, resultex = get_password_metadata('ABabc9001')
        eq_(result, '9.2.3.4')
        eq_(resultex, '2.3.0.0')

    def test_get_hint_metadata(self):
        result, resultex = get_hint_metadata('')
        eq_(result, '0.0.0.0.0.0')
        eq_(resultex, '0.0.0.0.0.0')

        result, resultex = get_hint_metadata(u'эюяЭЦaB-.45')
        eq_(result, '11.1.1.2.2.3')
        eq_(resultex, '5.2.1.0.1')

    def test_get_phonenumber_hash(self):
        phone_number = "+79991234567"
        md5 = hashlib.md5(b'test-salt')
        md5.update(phone_number.encode('utf8'))
        eq_(get_phone_number_hash(phone_number), md5.hexdigest())

    def test_frodo_bool(self):
        ok_(frodo_bool(None) is None)
        eq_(frodo_bool(True), '1')
        eq_(frodo_bool(False), '0')
