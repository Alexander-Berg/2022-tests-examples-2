# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import unittest

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone import (
    build_phones,
    SimplePhone,
    SimplePhones,
    sorted_phones,
)
from passport.backend.core.types.phone_number.phone_number import (
    InvalidPhoneNumber,
    PhoneNumber,
)
from passport.backend.utils.time import datetime_to_string


PHONE_NUMBER = '+79031234567'
PHONE_NUMBER_2 = '+79031234522'
PHONE_NUMBER_3 = '+79031114567'
PHONE_NUMBER_4 = '+78121234567'
PHONE_NUMBER_INVALID = '+380490000000'
SIMPLE_PHONE = PhoneNumber.parse(PHONE_NUMBER)
SIMPLE_PHONE_2 = PhoneNumber.parse(PHONE_NUMBER_2)
SIMPLE_PHONE_3 = PhoneNumber.parse(PHONE_NUMBER_3)
SIMPLE_PHONE_4 = PhoneNumber.parse(PHONE_NUMBER_4)
SIMPLE_PHONE_INVALID = PhoneNumber.parse(PHONE_NUMBER_INVALID, allow_impossible=True)
VALIDATION_DATETIME = datetime.now().replace(microsecond=0)
VALIDATION_DATETIME_STRING = datetime_to_string(VALIDATION_DATETIME)
VALIDATION_DATETIME_OLD_SCHEME = settings.PHONES_SECURE_SCHEME_ACTIVE_DATETIME - timedelta(days=1)


class TestSimplePhone(PassportTestCase):
    def setUp(self):
        self.phone = SimplePhone(
            id=1,
            number=SIMPLE_PHONE,
            is_confirmed=True,
            is_secure=True,
            validation_datetime=datetime.now(),
            pending_type=None,
            pending_phone_id=None,
        )

    def test_basic(self):
        eq_(self.phone.id, 1)
        eq_(self.phone.number, SIMPLE_PHONE)
        ok_(self.phone.is_confirmed)
        ok_(self.phone.is_secure)
        eq_(self.phone.validation_datetime, DatetimeNow())
        ok_(self.phone.is_suitable_for_restore)

    def test_eq(self):
        ok_(self.phone == self.phone)
        ok_(not self.phone == 123456)
        ok_(
            not self.phone == SimplePhone(
                id=1,
                number=SIMPLE_PHONE,
                is_confirmed=True,
                is_secure=False,
                validation_datetime=datetime.now(),
                pending_type=None,
                pending_phone_id=None,
            ),
        )
        ok_(
            not self.phone == SimplePhone(
                id=2,
                number=SIMPLE_PHONE,
                is_confirmed=True,
                is_secure=True,
                validation_datetime=datetime.now(),
                pending_type=None,
                pending_phone_id=None,
            ),
        )


class TestSimplePhones(unittest.TestCase):
    def test_empty_phones(self):
        phones = SimplePhones()
        assert_is_none(phones.secure)
        eq_(phones._by_number, dict())

    def test_add_and_find_phone(self):
        phones = SimplePhones()
        phone = SimplePhone(
            id=1,
            number=SIMPLE_PHONE,
            is_confirmed=True,
            is_secure=True,
            validation_datetime=VALIDATION_DATETIME,
            pending_type=None,
            pending_phone_id=None,
        )

        phones.add(phone)

        eq_(len(phones._by_number), 1)
        eq_(phones.secure, phone)
        eq_(phones.secure.id, phone.id)
        eq_(phones.find(SIMPLE_PHONE), phone)
        eq_(phones.find_confirmed(SIMPLE_PHONE), phone)

    def test_suitable_for_restore_phones(self):
        phones = SimplePhones()
        secure_phone = SimplePhone(
            id=1,
            number=SIMPLE_PHONE,
            is_confirmed=True,
            is_secure=True,
            validation_datetime=VALIDATION_DATETIME,
            pending_type=None,
            pending_phone_id=None,
        )
        confirmed_phone = SimplePhone(
            id=2,
            number=SIMPLE_PHONE_2,
            is_confirmed=True,
            is_secure=False,
            validation_datetime=VALIDATION_DATETIME,
            pending_type=None,
            pending_phone_id=None,
        )
        old_unconfirmed_phone = SimplePhone(
            id=3,
            number=SIMPLE_PHONE_3,
            is_confirmed=False,
            is_secure=False,
            validation_datetime=VALIDATION_DATETIME_OLD_SCHEME,
            pending_type=None,
            pending_phone_id=None,
        )
        old_confirmed_phone = SimplePhone(
            id=4,
            number=SIMPLE_PHONE_4,
            is_confirmed=True,
            is_secure=False,
            validation_datetime=VALIDATION_DATETIME_OLD_SCHEME,
            pending_type=None,
            pending_phone_id=None,
        )

        for phone in (
            secure_phone,
            confirmed_phone,
            old_unconfirmed_phone,
            old_confirmed_phone,
        ):
            phones.add(phone)

        eq_(
            phones.suitable_for_restore,
            sorted_phones([
                old_confirmed_phone,
                secure_phone,
            ]),
        )
        for phone in (
            old_confirmed_phone,
            secure_phone,
        ):
            ok_(phone.is_suitable_for_restore)
        for phone in (
            confirmed_phone,
            old_unconfirmed_phone,
        ):
            ok_(not phone.is_suitable_for_restore)

    def test_confirmed_phones(self):
        phones = SimplePhones()
        secure_phone = SimplePhone(
            id=1,
            number=SIMPLE_PHONE,
            is_confirmed=True,
            is_secure=True,
            validation_datetime=VALIDATION_DATETIME,
            pending_type=None,
            pending_phone_id=None,
        )
        confirmed_phone = SimplePhone(
            id=2,
            number=SIMPLE_PHONE_2,
            is_confirmed=True,
            is_secure=False,
            validation_datetime=VALIDATION_DATETIME,
            pending_type=None,
            pending_phone_id=None,
        )
        old_unconfirmed_phone = SimplePhone(
            id=3,
            number=SIMPLE_PHONE_3,
            is_confirmed=False,
            is_secure=False,
            validation_datetime=VALIDATION_DATETIME_OLD_SCHEME,
            pending_type=None,
            pending_phone_id=None,
        )
        old_confirmed_phone = SimplePhone(
            id=4,
            number=SIMPLE_PHONE_4,
            is_confirmed=True,
            is_secure=False,
            validation_datetime=VALIDATION_DATETIME_OLD_SCHEME,
            pending_type=None,
            pending_phone_id=None,
        )

        for phone in (
            secure_phone,
            confirmed_phone,
            old_unconfirmed_phone,
            old_confirmed_phone,
        ):
            phones.add(phone)

        eq_(
            phones.confirmed,
            sorted_phones([
                old_confirmed_phone,
                secure_phone,
                confirmed_phone,
            ]),
        )


class TestBuildPhones(unittest.TestCase):
    def test_build_empty_list(self):
        phones = build_phones([])
        eq_(len(phones._by_number), 0)

    def test_build_all_fields(self):
        phones = build_phones([{
            'id': '1',
            'number': PHONE_NUMBER,
            'valid': 'valid',
            'secure': '1',
            'validation_date': VALIDATION_DATETIME_STRING,
        }])

        eq_(len(phones._by_number), 1)

        phone = phones.find(SIMPLE_PHONE)

        eq_(phone.id, 1)
        ok_(phone.is_confirmed)
        ok_(phone.is_secure)
        eq_(phone.validation_datetime, VALIDATION_DATETIME)

    def test_build_all_fields_invalid_phone__allow_impossible(self):
        phones = build_phones(
            [{
                'id': '1',
                'number': PHONE_NUMBER_INVALID,
                'valid': 'valid',
                'secure': '1',
                'validation_date': VALIDATION_DATETIME_STRING,
            }],
            allow_impossible=True,
        )

        eq_(len(phones._by_number), 1)

        phone = phones.find(SIMPLE_PHONE_INVALID)

        eq_(phone.id, 1)
        ok_(phone.is_confirmed)
        ok_(phone.is_secure)
        eq_(phone.validation_datetime, VALIDATION_DATETIME)

    def test_build_all_fields_invalid_phone__allow_impossible_false(self):
        self.assertRaises(
            InvalidPhoneNumber,
            build_phones,
            [{
                'id': '1',
                'number': PHONE_NUMBER_INVALID,
                'valid': 'valid',
                'secure': '1',
                'validation_date': VALIDATION_DATETIME_STRING,
            }],
            allow_impossible=False,
        )

    def test_unconfirmed_not_secure_phone(self):
        phones = build_phones([{
            'id': '1',
            'number': PHONE_NUMBER,
            'valid': 'invalid',
            'secure': '0',
            'validation_date': VALIDATION_DATETIME_STRING,
        }])

        eq_(len(phones._by_number), 1)

        phone = phones.find(SIMPLE_PHONE)

        eq_(phone.id, 1)
        assert_is_none(phones.secure)
        ok_(not phone.is_confirmed)
        ok_(not phone.is_secure)

    def test_validation_datetime(self):
        phones = build_phones([{
            'id': '1',
            'number': PHONE_NUMBER,
            'valid': 'valid',
            'secure': '1',
            'validation_date': VALIDATION_DATETIME_STRING,
        }])

        eq_(len(phones._by_number), 1)

        phone = phones.find(SIMPLE_PHONE)

        eq_(phone.id, 1)
        ok_(phone.is_confirmed)
        ok_(phone.is_secure)
        eq_(phone.validation_datetime, VALIDATION_DATETIME)

    def test_pending_phone_id(self):
        phones = build_phones([{
            'id': '1',
            'number': PHONE_NUMBER,
            'valid': 'valid',
            'secure': '1',
            'pending_phoneid': 123,
            'validation_date': VALIDATION_DATETIME,
        }])

        eq_(len(phones._by_number), 1)

        phone = phones.find(SIMPLE_PHONE)

        eq_(phone.id, 1)
        ok_(phone.is_confirmed)
        eq_(phone.pending_phone_id, 123)

        phones = build_phones([{
            'id': '1',
            'number': PHONE_NUMBER,
            'valid': 'valid',
            'secure': '1',
            'validation_date': VALIDATION_DATETIME,
        }])
        phone = phones.find(SIMPLE_PHONE)
        eq_(phone.pending_phone_id, None)

    def test_secure_phone_being_bound(self):
        phones = build_phones([{
            'id': '1',
            'number': PHONE_NUMBER,
            'valid': 'msgsent',
            'secure': '1',
            'validation_date': None,
        }])

        assert_is_none(phones.secure)

        phone = phones.find(SIMPLE_PHONE)
        ok_(not phone.is_confirmed)
        ok_(not phone.is_secure)
