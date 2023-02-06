# -*- coding: utf-8 -*-
import binascii
import json
import re
import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.api.common.phone_karma.phone_karma import (
    extract_karma,
    get_phone_karma,
    load_phone_stats,
    PhoneKarma,
)
from passport.backend.core.builders.ufo_api import BaseUfoApiError
from passport.backend.core.builders.ufo_api.faker import (
    FakeUfoApi,
    ufo_api_phones_stats_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
import six


TEST_PHONE = PhoneNumber.parse('+79091234567')
TEST_WHITELIST_PHONE = PhoneNumber.parse('79097654321')
TEST_WHITELIST_PREFIX_PHONE_1 = PhoneNumber.parse('70007654321')
TEST_WHITELIST_PREFIX_PHONE_2 = PhoneNumber.parse('78147654321')
TEST_PHONE_FROM_FAKELIST = PhoneNumber.parse('79997654321')
TEST_PHONE_NUMBERS_FAKELIST = [
    [re.compile(r'^ \+7999 \d{7} $', re.VERBOSE), 'test_fakes'],
]


@with_settings_hosts(
    PHONE_KARMA_COUNTER_THRESHOLD=100,
)
class TestExtractKarma(unittest.TestCase):
    def test_black(self):
        for karma_value in [100, 101, 1000]:
            eq_(
                extract_karma({'phone_number_counter': karma_value}),
                PhoneKarma.black,
            )

    def test_white(self):
        for karma_value in [0, 1, 50]:
            eq_(
                extract_karma({'phone_number_counter': karma_value}),
                PhoneKarma.white,
            )

    def test_empty_stats(self):
        eq_(
            extract_karma({}),
            PhoneKarma.white,
        )


@with_settings_hosts()
class TestLoadPhoneStats(unittest.TestCase):
    def setUp(self):
        self.fake_ufo_api = FakeUfoApi()
        self.fake_ufo_api.start()

    def tearDown(self):
        self.fake_ufo_api.stop()
        del self.fake_ufo_api

    def test_ok(self):
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_PHONE),
        )
        status, phone_stats = load_phone_stats(TEST_PHONE)
        eq_(status, True)
        eq_(
            phone_stats,
            ufo_api_phones_stats_response(TEST_PHONE),
        )

    def test_error(self):
        self.fake_ufo_api.set_response_side_effect(
            'phones_stats',
            BaseUfoApiError,
        )
        with assert_raises(BaseUfoApiError):
            load_phone_stats(TEST_PHONE, safe=False)

    def test_safe(self):
        self.fake_ufo_api.set_response_side_effect(
            'phones_stats',
            BaseUfoApiError,
        )
        status, phones_stats = load_phone_stats(TEST_PHONE)
        eq_(status, False)
        eq_(
            phones_stats,
            {},
        )


@with_settings_hosts(
    PHONE_KARMA_WHITELIST=[TEST_WHITELIST_PHONE.digital],
    PHONE_KARMA_WHITELIST_PREFIXES=['7000', '7814'],
    PHONE_KARMA_COUNTER_THRESHOLD=100,
    PHONE_NUMBERS_FAKELIST=TEST_PHONE_NUMBERS_FAKELIST,
)
class TestGetPhoneKarma(unittest.TestCase):
    def setUp(self):
        self.fake_ufo_api = FakeUfoApi()
        self.fake_ufo_api.start()

    def tearDown(self):
        self.fake_ufo_api.stop()
        del self.fake_ufo_api

    def test_white_karma_ok(self):
        data = {'phone_number_counter': 1}
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_PHONE, data),
        )
        eq_(
            get_phone_karma(TEST_PHONE),
            PhoneKarma.white,
        )

    def test_black_karma_ok(self):
        data = {'phone_number_counter': 100}
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_PHONE, data),
        )
        eq_(
            get_phone_karma(TEST_PHONE),
            PhoneKarma.black,
        )

    def test_whitelist(self):
        self.fake_ufo_api.set_response_side_effect(
            'phones_stats',
            ValueError,
        )
        eq_(
            get_phone_karma(TEST_WHITELIST_PHONE),
            PhoneKarma.white,
        )
        eq_(self.fake_ufo_api.request.call_count, 0)

    def test_whitelist_prefix(self):
        self.fake_ufo_api.set_response_side_effect(
            'phones_stats',
            ValueError,
        )
        for phone in [TEST_WHITELIST_PREFIX_PHONE_1, TEST_WHITELIST_PREFIX_PHONE_2]:
            eq_(
                get_phone_karma(phone),
                PhoneKarma.white,
            )
        eq_(self.fake_ufo_api.request.call_count, 0)

    def test_fakelist(self):
        self.fake_ufo_api.set_response_side_effect(
            'phones_stats',
            ValueError,
        )
        eq_(
            get_phone_karma(TEST_PHONE_FROM_FAKELIST),
            PhoneKarma.white,
        )
        eq_(self.fake_ufo_api.request.call_count, 0)

    def test_ufo_error(self):
        self.fake_ufo_api.set_response_side_effect(
            'phones_stats',
            BaseUfoApiError,
        )
        eq_(
            get_phone_karma(TEST_PHONE),
            PhoneKarma.unknown,
        )

    def test_ufo_empty_data(self):
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            json.dumps({'other-key': '123'}),
        )
        eq_(
            get_phone_karma(TEST_PHONE),
            PhoneKarma.white,
        )

    def test_invalid_ufo_response(self):
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            json.dumps({'data': '123'}),
        )
        eq_(
            get_phone_karma(TEST_PHONE),
            PhoneKarma.unknown,
        )

    def test_invalid_ufo_response_unsafe(self):
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            json.dumps({'data': '123'}),
        )
        with assert_raises(TypeError if six.PY2 else binascii.Error):
            get_phone_karma(TEST_PHONE, safe=False),

    def test_ufo_error_unsafe(self):
        self.fake_ufo_api.set_response_side_effect(
            'phones_stats',
            BaseUfoApiError,
        )
        with assert_raises(BaseUfoApiError):
            get_phone_karma(TEST_PHONE, safe=False)
