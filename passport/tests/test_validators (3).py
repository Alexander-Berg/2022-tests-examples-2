# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json
import re
import time
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core import validators
from passport.backend.core.models.person import DisplayName
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_error_codes,
    check_raise_error,
)
from passport.backend.core.types.birthday import Birthday
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.validators import YandexTeamLogin
from passport.backend.core.validators.validators import (
    MAX_DOMAIN_ID,
    MAX_UID,
)
from passport.backend.utils.common import bytes_to_hex
import pytest


MAX_LONG_VALUE = 2147483647
TEST_MAGIC_LINK_RANDOM_BYTES = b'1' * 10
TEST_MAGIC_LINK_SECRET_KEY = bytes_to_hex(TEST_MAGIC_LINK_RANDOM_BYTES)


class TestRequireSome(unittest.TestCase):
    def test_validation_passes_with_either_item(self):
        v = validators.RequireSome(['a', 'b'])

        data = {'a': 5}
        eq_(v.to_python(data), data)

        data = {'b': 10}
        eq_(v.to_python(data), data)

    def test_none_values_are_considered_missing(self):
        v = validators.RequireSome(['a', 'b'])

        data = {'a': 5, 'b': None}
        eq_(v.to_python(data), data)

    def test_custom_empty_values_are_considered_missing(self):
        v = validators.RequireSome(['a', 'b'], empty_values=[False])

        data = {'a': 5, 'b': False}
        eq_(v.to_python(data), data)

    def test_false_values_are_ok(self):
        v = validators.RequireSome(['a', 'b'])

        data = {'a': False}
        eq_(v.to_python(data), data)

    @raises(validators.Invalid)
    def test_missing_items_raise_validation_error(self):
        v = validators.RequireSome(['a', 'b'])

        v.to_python({})

    @raises(validators.Invalid)
    def test_multiple_items_raise_validation_error(self):
        v = validators.RequireSome(['a', 'b'])

        v.to_python({'a': 5, 'b': 7})

    def test_not_reuired_fields(self):
        v = validators.RequireSome(['a', 'b'], min_=0)

        v.to_python({})


class TestRequireSet(unittest.TestCase):

    def setUp(self):
        self.v = validators.RequireSet(allowed_sets=[
            ['login'],
            ['firstname', 'lastname'],
        ])

    @raises(validators.Invalid)
    def test_both(self):
        data = {'login': 'a', 'firstname': 'b', 'lastname': 'c'}
        eq_(self.v.to_python(data), data)

    def test_login(self):
        data = {'login': 'a', 'firstname': None, 'lastname': None}
        eq_(self.v.to_python(data), data)

    def test_firstlastname(self):
        data = {'firstname': 'b', 'lastname': 'c', 'login': None}
        eq_(self.v.to_python(data), data)

    @raises(validators.Invalid)
    def test_firstname(self):
        self.v.to_python({'firstname': 'a', 'lastname': None, 'login': None})

    @raises(validators.Invalid)
    def test_lastname(self):
        self.v.to_python({'lastname': 'a', 'firstname': None, 'login': None})

    @raises(validators.Invalid)
    def test_nothing(self):
        self.v.to_python({'lastname': None, 'firstname': None, 'login': None})

    @raises(ValueError)
    def test_not_allow_empty_allowed_sets(self):
        validators.RequireSet(allowed_sets=[])

    def test_partial(self):
        data = {'lastname': 'a', 'firstname': None, 'login': 'aa'}
        eq_(self.v.to_python(data), data)

    def test_subsets(self):
        v = validators.RequireSet(allowed_sets=[
            ['a'],
            ['a', 'b'],
            ['a', 'b', 'c'],
        ])
        eq_(v.to_python({'a': 1, 'b': 2, 'c': 3}), {'a': 1, 'b': 2, 'c': 3})

    def test_allow_empty(self):
        v = validators.RequireSet(allowed_sets=[['a'], ['a', 'b', 'c']],
                                  allow_empty=True)
        data = {'a': None, 'b': None, 'c': None, 'd': None}
        eq_(v.to_python(data), data)

    @raises(validators.Invalid)
    def test_allow_empty_not_all_missing(self):
        v = validators.RequireSet(allowed_sets=[['a', 'b', 'c']],
                                  allow_empty=True)
        data = {'a': None, 'b': None, 'c': 'bla'}
        eq_(v.to_python(data), data)

    def test_expected_parameters(self):
        eq_(self.v.expected_parameters(), '<"firstname", "lastname"> | <"login">')

    def test_expected_parameters_and_allow_empty(self):
        v = validators.RequireSet(
            allowed_sets=[
                ['login'],
                ['firstname', 'lastname'],
            ],
            allow_empty=True,
        )
        eq_(v.expected_parameters(), '<"firstname", "lastname"> | <"login"> | all values are missing')

    def test_ignore_additional_fields(self):
        v = validators.RequireSet(
            allowed_sets=[
                ['a', 'b'],
                ['b', 'c'],
            ],
        )
        data = {
            'a': None,
            'b': 'b_value',
            'c': 'c_value',
            'field': 'field_value',
        }
        eq_(v.to_python(data), data)

    def test_empty_ignore_additional_fields(self):
        v = validators.RequireSet(
            allowed_sets=[
                ['a', 'b'],
                ['b', 'c'],
            ],
            allow_empty=True,
        )
        data = {
            'a': None,
            'b': None,
            'c': None,
            'd': None,
            'field': 'field_value',
        }
        eq_(v.to_python(data), data)


class TestAliasFields(unittest.TestCase):
    def test_primary_keys_pass(self):
        v = validators.AliasFields({'a': ['b', 'c'], 'q': ['w', 'e']})

        data = {'a': 10}
        eq_(v.to_python(data), data)

        data = {'q': 20}
        eq_(v.to_python(data), data)

        data = {'a': False, 'q': None}
        eq_(v.to_python(data), data)

    def test_primary_key_takes_priority(self):
        v = validators.AliasFields({'a': ['b', 'c'], 'q': ['w', 'e']})

        data = {'a': 10, 'b': 20, 'c': 30, 'q': 40}
        eq_(v.to_python(data), data)

        data = {'w': 10, 'q': 20, 'e': 30, 'a': 40}
        eq_(v.to_python(data), data)

    def test_aliases(self):
        v = validators.AliasFields({'a': ['b', 'c'], 'q': ['w', 'e']})

        data = {'b': 20, 'e': 40}
        eq_(v.to_python(data), {'a': 20, 'q': 40})

        data = {'b': 20, 'c': 30, 'w': 40}
        eq_(v.to_python(data), {'a': 20, 'c': 30, 'q': 40})

        data = {'b': 20, 'c': 30, 'w': 40, 'e': 50}
        eq_(v.to_python(data), {'a': 20, 'c': 30, 'q': 40, 'e': 50})

    def test_none_is_ignored(self):
        v = validators.AliasFields({'a': ['b', 'c'], 'q': ['w', 'e']})

        data = {'b': None, 'c': 0, 'w': None, 'e': False}
        eq_(v.to_python(data), {'a': 0, 'q': False, 'b': None, 'w': None})

    def test_missing_aliases(self):
        v = validators.AliasFields({'a': ['b', 'c'], 'q': ['w', 'e']})

        data = {}
        eq_(v.to_python(data), {})


class TestFieldsMatch(unittest.TestCase):
    @raises(TypeError)
    def test_empty_field_names(self):
        validators.FieldsMatch()

    @raises(TypeError)
    def test_one_field_name_args(self):
        validators.FieldsMatch('name')

    @raises(TypeError)
    def test_one_field_name_kwargs(self):
        validators.FieldsMatch(fields_names=['name'])

    def test_unpackargs(self):
        v = validators.FieldsMatch('a', 'b', 'c')
        eq_(v.field_names, ('a', 'b', 'c'))

    def test_validate_partial_all_fields(self):
        with mock.patch('passport.backend.core.validators.FieldsMatch.validate_python') as validate_python:
            v = validators.FieldsMatch('a', 'b', 'c')
            data = {'a': 'value', 'b': 'value', 'c': 'value'}
            v.validate_partial(data, None)
            eq_(validate_python.call_count, 1)
            eq_(validate_python.call_args[0][0], data)

    def test_validate_partial_not_all_fields(self):
        v = validators.FieldsMatch('a', 'b', 'c')

        data = {'a': 'value', 'b': 'value'}
        state = None
        eq_(v.validate_partial(data, state), None)

    def test_validation_passes(self):
        v = validators.FieldsMatch('a', 'b', 'c')

        data = {'a': 'value', 'b': 'value', 'c': 'value'}
        eq_(v.to_python(data), data)

    @raises(validators.Invalid)
    def test_not_matched(self):
        v = validators.FieldsMatch('a', 'b', 'c')

        data = {'a': 'valueA', 'b': 'valueB', 'c': 'valueC'}
        try:
            eq_(v.to_python(data), data)
        except validators.Invalid as e:
            eq_(len(e.error_dict), 1)
            ok_('form' in e.error_dict)
            form_error = e.error_dict['form']
            eq_(form_error.code, 'invalidNoMatch')
            eq_(form_error.msg, 'Fields do not match: a != b, c')
            raise
        ok_(False)


class TestDisplayName(unittest.TestCase):
    def test_validation_passes_with_all_fields(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'name',
            'provider': 'fb',
            'profile_id': 123,
            'is_from_variants': False,
        }
        eq_(v.to_python(data), DisplayName('name', 'fb', 123))

    def test_validation_passes_from_variants(self):
        v = validators.DisplayName()

        data = {
            'display_name': 's:123:fb:name',
            'is_from_variants': 1,
        }
        eq_(v.to_python(data), DisplayName('name', 'fb', 123))

    def test_validation_passes_only_display_name(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'name',
        }
        eq_(v.to_python(data), DisplayName('name'))

    def test_validation_passes_with_strip(self):
        v = validators.DisplayName()

        data = {
            'display_name': u'\u2000  name  ',
        }
        eq_(v.to_python(data), DisplayName('name'))

    def test_validation_missing_display_name(self):
        v = validators.DisplayName()

        data = {}
        eq_(v.to_python(data), None)

    def test_validation_missing_display_name_with_other_fields(self):
        v = validators.DisplayName()

        data = {
            'provider': 'fb',
            'profile_id': 123,
        }
        eq_(v.to_python(data), None)

    @raises(validators.Invalid)
    def test_validation_missing_profile_id(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'name',
            'provider': 'fb',
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_unallowed_symbol(self):
        v = validators.DisplayName()

        data = {
            'display_name': u'\u200c  name  ',
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_missing_provider(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'name',
            'profile_id': 123,
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_missing_is_from_variants(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'p:name',
            'is_from_variants': '',
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_not_bool_is_from_variants(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'p:name',
            'is_from_variants': 'book',
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_not_integer_profile_id(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'name',
            'provider': 'fb',
            'profile_id': 'one',
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_invalid_provider(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'name',
            'provider': 'facebook',
            'profile_id': 123,
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_invalid_string_from_variants(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'llama:name',
            'is_from_variants': True,
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_all_fields_error(self):
        v = validators.DisplayName()
        data = {
            'display_name': 'name',
            'provider': 'fb',
            'profile_id': 123,
            'is_from_variants': True,
        }
        v.to_python(data)

    def test_validation_passes_max_possible_display_name_length(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'n' * 40,
        }
        eq_(v.to_python(data), DisplayName('n' * 40))

    @raises(validators.Invalid)
    def test_validation_too_long_display_name(self):
        v = validators.DisplayName()

        data = {
            'display_name': 'n' * 41,
            'profile_id': 123,
        }
        v.to_python(data)


class TestSocialDisplayName(unittest.TestCase):
    def test_validation_passes_with_all_fields(self):
        v = validators.SocialDisplayName()

        data = {
            'display_name': 'name',
            'provider': 'fb',
            'profile_id': 123,
        }
        eq_(v.to_python(data), DisplayName('name', 'fb', 123))

    def test_validation_passes_with_strip(self):
        v = validators.SocialDisplayName()

        data = {
            'display_name': '  name  ',
            'provider': 'fb',
            'profile_id': 123,
        }
        eq_(v.to_python(data), DisplayName('name', 'fb', 123))

    def test_validation_missing_display_name(self):
        v = validators.SocialDisplayName()

        data = {}
        eq_(v.to_python(data), None)

    @raises(validators.Invalid)
    def test_validation_missing_display_name_with_other_fields(self):
        v = validators.SocialDisplayName()

        data = {
            'provider': 'fb',
            'profile_id': 123,
        }
        eq_(v.to_python(data), None)

    @raises(validators.Invalid)
    def test_validation_passes_only_display_name(self):
        v = validators.SocialDisplayName()

        data = {
            'display_name': 'name',
        }
        eq_(v.to_python(data), DisplayName('name'))

    @raises(validators.Invalid)
    def test_validation_missing_profile_id(self):
        v = validators.SocialDisplayName()

        data = {
            'display_name': 'name',
            'provider': 'fb',
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_missing_provider(self):
        v = validators.SocialDisplayName()

        data = {
            'display_name': 'name',
            'profile_id': 123,
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_not_integer_profile_id(self):
        v = validators.SocialDisplayName()

        data = {
            'display_name': 'name',
            'provider': 'fb',
            'profile_id': 'one',
        }
        v.to_python(data)

    @raises(validators.Invalid)
    def test_validation_invalid_provider(self):
        v = validators.SocialDisplayName()

        data = {
            'display_name': 'name',
            'provider': 'facebook',
            'profile_id': 123,
        }
        v.to_python(data)


class TestRequireIfEquals(unittest.TestCase):

    def test_passed(self):
        v = validators.RequireIfEquals(['req', 'more'], 'check', 'hit')
        v.to_python({'check': None, 'req': None})
        v.to_python({'check': 'hit', 'req': 'a_val', 'more': 'b_val'})
        # эти два значения `req` допускаются, поскольку это ответственность валидатора
        # конкретного поля - допускать такие значения или нет
        v.to_python({'check': 'hit', 'req': '0', 'more': ''})

        v = validators.RequireIfEquals(['req'], 'check', None)
        v.to_python({'check': 'miss', 'req': None})
        v.to_python({'check': 'miss', 'req': 'some'})

    def test_failed(self):
        v = validators.RequireIfEquals(['a', 'b'], 'c', 'hit')
        with assert_raises(validators.Invalid):
            v.to_python({'a': None, 'b': None, 'c': 'hit'})
        with assert_raises(validators.Invalid):
            v.to_python({'a': 'None', 'b': None, 'c': 'hit'})
        with assert_raises(validators.Invalid):
            v.to_python({'a': None, 'b': 'None', 'c': 'hit'})

        v = validators.RequireIfEquals(['a'], 'b', None)
        with assert_raises(validators.Invalid):
            v.to_python({'a': None, 'b': None})


class TestLooseDate(unittest.TestCase):
    def setUp(self):
        self.validator = validators.LooseDateValidator()

    def test_passed(self):
        valid_data = {
            '1900-01-01': datetime(1900, 1, 1),
            '1900-10-10': datetime(1900, 10, 10),
            '2000-02-00': datetime(2000, 2, 1),
            '1998-00-00': datetime(1998, 1, 1),
            '2004-02-29': datetime(2004, 2, 29),
            '9999-12-31': datetime(9999, 12, 31),
            '': None,
            None: None,
        }
        for string, date in valid_data.items():
            eq_(self.validator.to_python(string), date)

    def test_failed(self):
        values_codes = (
            ('1234-11-100', 'invalid'),
            ('01234-11-10', 'invalid'),
            ('abcd', 'invalid'),
            ('2000-00-11', 'invalid'),
            ('2001-02-29', 'invalid'),
            ('0000-10-10', 'invalid'),
            ('1899-02-29', 'invalid'),  # Сначала проверяем валидность даты, потом смотрим на год
            ('1899-12-30', 'tooearly'),
            ({}, 'badType'),
            (object(), 'badType'),
            ([], 'badType'),
            ({1: 2}, 'badType'),
            (0, 'badType'),
        )
        for value, error_code in values_codes:
            with assert_raises(validators.Invalid) as exception_context:
                self.validator.to_python(value)
            eq_(exception_context.exception.code, error_code)

    def test_with_non_default_earliest_year(self):
        validator = validators.LooseDateValidator(earliest_year=2000)

        eq_(validator.to_python('2000-00-00'), datetime(2000, 1, 1))

        with assert_raises(validators.Invalid) as exception_context:
            validator.to_python('1999-12-00')
        eq_(exception_context.exception.code, 'tooearly')

    def test_with_max_days_in_future_eq_zero(self):
        validator = validators.LooseDateValidator(max_days_in_future=0)

        now = datetime.now()
        for date in (now + timedelta(days=-1), now):
            eq_(validator.to_python(date.strftime('%Y-%m-%d')), datetime(date.year, date.month, date.day))

        for date in (now + timedelta(days=1), now + timedelta(days=1000), datetime(9999, 12, 31)):
            with assert_raises(validators.Invalid) as exception_context:
                validator.to_python(date.strftime('%Y-%m-%d'))
            eq_(exception_context.exception.code, 'toolate')

    def test_with_max_days_in_future_not_zero(self):
        validator = validators.LooseDateValidator(max_days_in_future=2)

        now = datetime.now()
        for date in (now + timedelta(days=-1), now, now + timedelta(days=1), now + timedelta(days=2)):
            eq_(validator.to_python(date.strftime('%Y-%m-%d')), datetime(date.year, date.month, date.day))

        for date in (now + timedelta(days=3), now + timedelta(days=1000), datetime(9999, 12, 31)):
            with assert_raises(validators.Invalid) as exception_context:
                validator.to_python(date.strftime('%Y-%m-%d'))
            eq_(exception_context.exception.code, 'toolate')


class TestHexString(unittest.TestCase):
    def test_passed(self):
        v = validators.HexString()
        v.to_python('abcdef0123456789')
        v.to_python('a')
        v.to_python('a' * 100)

    def test_failed(self):
        for value in ['abcdefg', 'a-b', 'abc.']:
            with assert_raises(validators.Invalid):
                v = validators.HexString()
                v.to_python(value)


class TestGpsPackageName(unittest.TestCase):
    def test_passed(self):
        for value in ('com.yandex.foo', 'c123.y123', 'a.b'):
            v = validators.GpsPackageName()
            eq_(v.to_python(value), value)

    def test_failed(self):
        for value in (
            u'ru.yandex.кириллица'  # # имя пакета должно содержать _только_ a-zA-Z0-9_\.
            'ru',  # сегментов должно быть > 1
            'ru.yandex.',  # кончается точкой - непорядок
            '123ru.123yandex',  # сегмент имени пакета должен начинаться с буквы
        ):
            v = validators.GpsPackageName()
            with assert_raises(validators.Invalid):
                v.to_python(value)


@pytest.mark.parametrize('valid_uid', ['0', 0, '1', 100, 12345, MAX_UID])
def test_uid(valid_uid):
    check_equality(validators.Uid(), (valid_uid, int(valid_uid)))


@pytest.mark.parametrize('invalid_uid', [
    '',
    'a',
    '-1',
    -1,
    '    ',
    MAX_UID + 1,
    2 ** 128,
    ])
def test_uid_invalid(invalid_uid):
    check_raise_error(validators.Uid(), invalid_uid)


class TestDomainId(unittest.TestCase):
    def test_passed(self):
        v = validators.DomainId()
        for value in (
            '1',
            100,
            12345,
            MAX_DOMAIN_ID,
        ):
            eq_(v.to_python(value), int(value))

    def test_failed(self):
        v = validators.DomainId()
        for value in (
            '',
            'a',
            '0',
            0,
            '-1',
            -1,
            '    ',
            MAX_UID + 1,
            2 ** 128,
        ):
            with assert_raises(validators.Invalid):
                v.to_python(value)


class TestBase64String(unittest.TestCase):
    good_values = [
        ('sasd', b'\xb1\xab\x1d'),
        ('jsla6hg=', b'\x8e\xc9Z\xea\x18'),
        ('jsla6hg', b'\x8e\xc9Z\xea\x18'),
        ('klN+NPRj6jGZvA==', b'\x92S~4\xf4c\xea1\x99\xbc'),
    ]
    bad_values = [
        '@',
        '%^',
        'привет',
        u'абв',
    ]

    def test_ok(self):
        v = validators.Base64String()
        for value, decoded in self.good_values:
            eq_(v.to_python(value), decoded)

    def test_error(self):
        v = validators.Base64String()
        for value in self.bad_values:
            with assert_raises(validators.Invalid):
                v.to_python(value)

    def test_no_decode_ok(self):
        v = validators.Base64String(decode=False)
        for value, _ in self.good_values:
            eq_(v.to_python(value), value)

    def test_no_decode_error(self):
        v = validators.Base64String(decode=False)
        for value in self.bad_values:
            with assert_raises(validators.Invalid):
                v.to_python(value)


class TestTotpPinValidator(unittest.TestCase):
    def test_ok(self):
        v = validators.TotpPinValidator(
            phone_number=PhoneNumber.parse('+79261234567'),
            country='RU',
            birthday=Birthday(year=2016, month=1, day=1),
        )
        for value, decoded in [
            ('0102', '0102'),
            ('8429', '8429'),
            ('3331', '3331'),
            ('0012', '0012'),
            ('1800', '1800'),
            ('2100', '2100'),
            ('1235', '1235'),
            ('7890', '7890'),
            ('9875', '9875'),
            ('2343', '2343'),
            ('6545', '6545'),
            ('01010', '01010'),
            ('1234567890', '1234567890'),
            ('123456787654321', '123456787654321'),
            ('0' * 15 + '1', '0' * 15 + '1'),
            ('79261234566', '79261234566'),
            ('89261234566', '89261234566'),
            ('1234123412341238', '1234123412341238'),
            ('0000000000000901', '0000000000000901'),
            ('020116', '020116'),
            ('02012016', '02012016'),
            ('20001', '20001'),
        ]:
            eq_(v.to_python(value), decoded)

    def test_ok_without_phone_number_and_birthday_check(self):
        v = validators.TotpPinValidator()
        for value, decoded in [
            ('79261234567', '79261234567'),
            ('89261234567', '89261234567'),
            ('010116', '010116'),
            ('01012016', '01012016'),
        ]:
            eq_(v.to_python(value), decoded)

    def test_ok_for_birthday_without_year(self):
        v = validators.TotpPinValidator(
            birthday=Birthday(month=1, day=1),
        )
        for value, decoded in [
            ('010104', '010104'),
            ('01010004', '01010004'),
            ('010100', '010100'),
            ('01011900', '01011900'),
        ]:
            eq_(v.to_python(value), decoded)

        with assert_raises(validators.Invalid):
            v.to_python('0101')

    def test_ok_for_invalid_birthday(self):
        v = validators.TotpPinValidator(
            birthday=Birthday(year=1899, month=1, day=1),
        )
        for value, decoded in [
            ('010104', '010104'),
            ('01010004', '01010004'),
            ('010100', '010100'),
            ('01011900', '01011900'),
        ]:
            eq_(v.to_python(value), decoded)

        with assert_raises(validators.Invalid):
            v.to_python('0101')

    def test_error(self):
        bad_values = [
            'abc',  # короткий
            'abcd',  # не число
            u'абвг',  # не число
            '+1221',  # посторонние символы
            '-1221',  # посторонние символы
            '0' * 16 + '1',  # длинный
            # Одинаковые цифры
            '0000',
            '3333',
            '9999',
            # Последовательные цифры
            '0123',
            '1234',
            '2345',
            '3456',
            '4567',
            '5678',
            '6789',
            '4321',
            '5432',
            '6543',
            '7654',
            '8765',
            '9876',
            '3210',
            '0123456789',
            # Похожи на год
            '1999',
            '2099',
            # Похожи на номер телефона
            '89261234567',
            '79261234567',
            # Похожи на день рождения
            '01012016',
            '010116',
            '0101',
        ]
        for value in bad_values:
            with assert_raises(validators.Invalid):
                v = validators.TotpPinValidator(
                    phone_number=PhoneNumber.parse('+79261234567'),
                    country='RU',
                    birthday=Birthday(year=2016, month=1, day=1),
                )
                v.to_python(value)


class TestStrictStringValidator(unittest.TestCase):
    def test_not_strict_ok(self):
        v = validators.String()
        for value, expected in [
            # корректно работаем со строками и None
            (None, u''),
            ('', u''),
            ('string', u'string'),
            (u'вася', u'вася'),
            # пустые значения также преобразуются в пустую строку
            ({}, u''),
            ([], u''),
            (0, u''),  # сомнительное поведение formencode
            # если на входе не строка, валидатор пытается его преобразовать к строке
            ({'x': 'y'}, u"{'x': 'y'}"),
        ]:
            decoded = v.to_python(value)
            eq_(type(decoded), type(expected))
            eq_(decoded, expected)

    def test_strict_ok(self):
        v = validators.String(strict=True)
        for value, expected in [
            # корректно работаем со строками
            ('string', u'string'),
            (u'вася', u'вася'),
            # пустые значения также преобразуются в пустую строку
            (None, u''),
            ('', u''),
        ]:
            decoded = v.to_python(value)
            eq_(type(decoded), type(expected))
            eq_(decoded, expected)

    def test_strict_error(self):
        # не проходит проверка типа
        bad_values = [
            0,
            {1: 2},
            ['value'],
            object(),
            {},
            [],
        ]
        for value in bad_values:
            with assert_raises(validators.Invalid):
                v = validators.String(strict=True)
                v.to_python(value)


class TestRegexValidatorEmptyHandling(unittest.TestCase):
    def test_valid_empty(self):
        v = validators.Regex(r'\d+')
        for value, expected in [
            (None, None),
            (u'', None),
        ]:
            decoded = v.to_python(value)
            eq_(type(decoded), type(expected))
            eq_(decoded, expected)

    def test_invalid_empty(self):
        bad_values = [
            0,
            {},
            [],
        ]
        for value in bad_values:
            with assert_raises(validators.Invalid):
                v = validators.Regex(r'.*')
                v.to_python(value)


@with_settings(
    ALT_DOMAINS={
        'galatasaray.net': 2,
        'auto.ru': 1120001,
    },
)
class TestAltDomainAliasValidator(unittest.TestCase):

    def setUp(self):
        self.patch = mock.patch(
            'passport.backend.core.validators.validators.ALT_DOMAIN_LOGIN_VALIDATORS',
            {'auto.ru': YandexTeamLogin},
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    @raises(ValueError)
    def test_error_invalid_allowed_domains(self):
        validators.AltDomainAliasValidator(allowed_domains=['unknown_domain.ru'])

    def test_ok_all_domains_allowed(self):
        v = validators.AltDomainAliasValidator()
        for value, decoded in [
            ('alias@Galatasaray.NET', 'alias@galatasaray.net'),
            ('Alias@Auto.ru', 'alias@auto.ru'),
        ]:
            eq_(v.to_python(value), decoded)

    def test_ok_some_domains_allowed(self):
        v = validators.AltDomainAliasValidator(allowed_domains=['galatasaray.net'])
        for value, decoded in [
            ('alias.with.dots@Galatasaray.NET', 'alias-with-dots@galatasaray.net'),
        ]:
            eq_(v.to_python(value), decoded)

    def test_error_domain_not_allowed(self):
        v = validators.AltDomainAliasValidator(allowed_domains=['galatasaray.net'])
        bad_values = [
            'Alias@Auto.ru',
            'alias@kinopoisk.ru',
        ]
        for value in bad_values:
            assert_raises(validators.Invalid, v.to_python, value)

    def test_error(self):
        v = validators.AltDomainAliasValidator()
        bad_values = [
            u'что-то',
            'abc@unknown_domain.ru',
            '-bad-login-for-auto-ru-@auto.ru',
            'too.bad@auto.ru',
        ]
        for value in bad_values:
            assert_raises(validators.Invalid, v.to_python, value)


def test_TimestampInPast__ok():
    v = validators.TimestampInPast()
    now = int(time.time())
    valid = [
        ('0', 0),
        ('-100', -100),
        (str(now), now),
    ]
    for value, expected in valid:
        eq_(v.to_python(value), expected)


def test_TimestampInPast__error():
    v = validators.TimestampInPast()
    now = int(time.time())
    invalid = [
        2 ** 64 + 1,  # Слишком большое число!
        now + 100,  # Определенно будущее
        -2208997800 - (24 * 60 * 60),  # (01-01-1900 - 1d) Далекое прошлое
    ]
    for value in invalid:
        assert_raises(validators.Invalid, v.to_python, value)


class TransformingRegexValidatorTestCase(unittest.TestCase):

    def setUp(self):
        self.validator = validators.TransformingRegex(regex=re.compile(r'^(?P<value>\d*)$'))

    def test_valid(self):
        valid = [
            ('1234', {'value': '1234'}),
            ('', ''),  # Пустое значение не валидируется регулярным выражением
        ]
        for value, expected in valid:
            eq_(self.validator.to_python(value), expected)

    def test_valid_with_strip_enabled(self):
        self.validator.strip = True
        eq_(self.validator.to_python('  1  '), {'value': '1'})

    def test_invalid(self):
        invalid = (
            'w',
            ' ',
            '12345[',
        )
        for value in invalid:
            assert_raises(validators.Invalid, self.validator.to_python, value)

    def test_invalid_empty(self):
        self.validator.not_empty = True
        assert_raises(validators.Invalid, self.validator.to_python, '')

    def test_with_no_named_groups(self):
        self.validator = validators.TransformingRegex(regex=re.compile(r'^\d{2}\.\d{2}$'))

        eq_(self.validator.to_python('10.20'), {})


class PersistentTrackKeyValidatorTestCase(unittest.TestCase):
    def test_valid(self):
        v = validators.PersistentTrackKey()
        for uid in 0, 1, MAX_UID:
            track_key = '52bf429537106213b295c3efa00ce2c1%x' % uid
            parsed_track_key = {
                'track_key': track_key,
                'uid': uid,
                'track_id': '52bf429537106213b295c3efa00ce2c1',
            }
            eq_(
                v.to_python(track_key),
                parsed_track_key,
            )
            eq_(
                v.to_python('    %s   ' % track_key),
                parsed_track_key,
            )

    def test_invalid(self):
        v = validators.PersistentTrackKey()
        bad_values = [
            'not_a_track_key',
            '52bf429537106213b295c3efa00ce',
            '52bf429537106213b295c3efa00ce2c1',
            '52bf429537106213b295c3efa00ce2c1abcdefg',
            '_2bf429537106213b295c3efa00ce2c1abcdef',
            '52bf429537106213b295c3efa00ce2c1%x' % (MAX_UID + 1),
            '52bf429537106213b295c3efa00ce2c1%x' % 2 ** 128,
        ]
        for value in bad_values:
            with assert_raises(validators.Invalid):
                v.to_python(value)


class TestMagicLinkSecretKeyTestCase(unittest.TestCase):

    def test_valid(self):
        v = validators.MagicLinkSecretKey()
        for uid in 0, 1, MAX_UID:
            secret = '%s%x' % (TEST_MAGIC_LINK_SECRET_KEY, uid)
            parsed_secret = {
                'secret': secret,
                'uid': uid,
                'key': TEST_MAGIC_LINK_SECRET_KEY,
            }
            eq_(
                v.to_python(secret),
                parsed_secret,
            )
            eq_(
                v.to_python('    %s   ' % secret),
                parsed_secret,
            )

    def test_invalid(self):
        v = validators.MagicLinkSecretKey()
        bad_values = [
            'not_a_track_key',
            '52bf4295',
            '52bf429537106213b295c3efa00ce2c1abcdefg',
            '_2bf429537106213b295c3efa00ce2c1abcdef',
            '%s%x' % (TEST_MAGIC_LINK_SECRET_KEY, MAX_UID + 1),
        ]
        for value in bad_values:
            with assert_raises(validators.Invalid):
                v.to_python(value)


class TestPhoneId(unittest.TestCase):
    def test_ok(self):
        v = validators.PhoneId()
        valid = [
            (123, 123),
            ('123', 123),
            ('-123', -123),
            (123.999, 123),
            (' 123 ', 123),
        ]
        for value, expected in valid:
            eq_(v.to_python(value), expected)

    def test_no_strip_ok(self):
        v = validators.PhoneId(strip=False)
        valid = [
            (' 123 ', 123),
            (' 123\t ', 123),
        ]
        for value, expected in valid:
            eq_(v.to_python(value), expected)

    def test_empty_error(self):
        v = validators.PhoneId()
        invalid = [
            '',
            ' ',
            None,
        ]
        for value in invalid:
            assert_raises(validators.Invalid, v.to_python, value)

    def test_error(self):
        v = validators.PhoneId(strip=False)
        invalid = [
            '123.3',
            'seven-eleven',
            '12 3',
            ' ',
        ]
        for value in invalid:
            assert_raises(validators.Invalid, v.to_python, value)

    def test_missing_ok(self):
        v = validators.PhoneId(if_missing=None, not_empty=False)
        valid = [
            ('', None),
            (' ', None),
            (None, None),
        ]
        for value, expected in valid:
            eq_(v.to_python(value), expected)


@with_settings()
class TestCityId(unittest.TestCase):
    def test_ok(self):
        v = validators.CityId()
        valid = [
            (213, 213),
            (' 214', 214),
            ('213', 213),
            (None, None),
            ('', None),
        ]
        for value, expected in valid:
            eq_(v.to_python(value), expected)

    def test_error(self):
        v = validators.CityId()
        invalid = [
            MAX_LONG_VALUE + 1,
            MAX_LONG_VALUE,
            -10,
            0,
            'twelve',
            225,    # Russia
        ]
        for value in invalid:
            assert_raises(validators.Invalid, v.to_python, value)

    def test_empty_error(self):
        v = validators.CityId(not_empty=True)
        invalid = ['', ' ']
        for value in invalid:
            assert_raises(validators.Invalid, v.to_python, value)


class TestUnixtime(unittest.TestCase):
    MAX_INT32 = 2 ** 31 - 1
    MIN_INT32 = -2 ** 31

    def test_valid_values(self):
        v = validators.Unixtime()
        valid = [
            ('0', datetime.fromtimestamp(0)),
            (str(self.MAX_INT32), datetime.fromtimestamp(self.MAX_INT32)),
            (str(self.MIN_INT32), datetime.fromtimestamp(self.MIN_INT32)),
            (' 0 ', datetime.fromtimestamp(0)),
        ]
        for value, expected in valid:
            eq_(v.to_python(value), expected)

    def test_invalid_values(self):
        v = validators.Unixtime()
        invalid = [
            str(self.MAX_INT32 + 1),
            str(self.MIN_INT32 - 1),
            '111111111111111111111111',
            '-111111111111111111111111',
            '',
            '0.5',
            'one',
        ]
        for value in invalid:
            assert_raises(validators.Invalid, v.to_python, value)

    def test_with_milliseconds(self):
        v = validators.Unixtime(allow_milliseconds=True)
        eq_(
            v.to_python('0.5'),
            datetime.fromtimestamp(0.5),
        )


@pytest.mark.parametrize('value', ['foo', 'FOO', 'a' * 40])
def test_uber_id(value):
    check_equality(validators.UberId(), (value, value.lower()))


def test_uber_id_period():
    check_equality(validators.UberId(), ('aa..bb', 'aa--bb'))


@pytest.mark.parametrize('value', ['', 'a' * 41, u'ф' * 10])
def test_uber_id_invalid(value):
    check_raise_error(validators.UberId(), value)


@pytest.mark.parametrize('value', ['a' * 6, 'a' * 50])
def test_device_id(value):
    check_equality(validators.DeviceId(), (value, value))


@pytest.mark.parametrize('value', ['', 'a' * 5, 'a' * 51])
def test_device_id_invalid(value):
    check_raise_error(validators.DeviceId(), value)


@pytest.mark.parametrize('value', ['', 'a', 'a' * 100])
def test_device_name(value):
    check_equality(validators.DeviceName(), (value, value or None))


@pytest.mark.parametrize('value', ['a' * 101])
def test_device_name_invalid(value):
    check_raise_error(validators.DeviceName(), value)


@pytest.mark.parametrize('value', ['a', 'a' * 100])
def test_music_promo_code(value):
    check_equality(validators.MusicPromoCode(), (value, value or None))


@pytest.mark.parametrize('value', [None, '', 'a' * 256])
def test_music_promo_code_invalid(value):
    check_raise_error(validators.MusicPromoCode(), value)


class TestMailishId(unittest.TestCase):
    def test_ok(self):
        v = validators.MailishId()
        for value, result in [
            ('', None),
            ('WGVR2===', 'wgvr2'),
            ('WGVR2', 'wgvr2'),
            ('ORSXG5BNORSXG5BNORSXG5BNORSXG5BNOQ', 'orsxg5bnorsxg5bnorsxg5bnorsxg5bnoq'),
            ('r3evv2qy', 'r3evv2qy'),
            ('SJJx4NhumPVDdGN4', 'sjjx4nhumpvddgn4'),
            ('r3EvV2qy' * 31, 'r3evv2qy' * 31),
        ]:
            eq_(v.to_python(value), result)

    def test_error(self):
        bad_values = [
            # 'a',
            # 'ab',
            'abc@',
            'a%^',
            'привет',
            u'абв',
            'Ym FzZTY 0IH ZhbHVl',
            'r3evv2qy' * 32,
            # Base64
            'YmFzZTY0IHZhbHVl',
            'MTIzNA==',
        ]
        for value in bad_values:
            with assert_raises(validators.Invalid):
                v = validators.MailishId()
                v.to_python(value)


class TestBillingFeatures(unittest.TestCase):
    def test_ok(self):
        validator = validators.BillingFeatures()
        value = {
            'cashback_100': {
                'in_trial': True,
                'paid_trial': False,
                'region_id': 0,
                'trial_duration': 0,
                'brand': 'some_brand',
            },
            'music_premium': {
                'region_id': 9999
            },
            'passport': {},
        }
        eq_(
            validator.to_python(json.dumps(value)),
            value,
        )

    def test_invalid_json_error(self):
        validator = validators.BillingFeatures()
        value = u'''{
            "feature_name": {
                "region_id": 9999,
                "value"
            }
        }'''
        with assert_raises(validators.Invalid) as e:
            validator.to_python(value)
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Expecting \':\' delimiter: line 5 column 13 (char 103)',
        )

    def test_long_feature_name_error(self):
        validator = validators.BillingFeatures()
        value = {
            'very_long_feature_name_1234567890': {
                'region_id': 9999,
            },
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: The name of the feature (very_long_feature_name_1234567890) doesn\'t match the pattern ^[abcdefghijklmnopqrstuvwxyz0123456789_-]{1,20}$',
        )

    def test_deprecated_feature_name_error(self):
        validator = validators.BillingFeatures()
        value = {
            'feature_name': {
                'region_id': 9999,
                'name': 'Feature',
            },
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: "name" is a deprecated attribute name',
        )

    def test_not_a_dictionary_value_error(self):
        validator = validators.BillingFeatures()
        value = [
            {
                'region_id': 9999,
            },
        ]
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: A field value is not a dictionary',
        )

    def test_feature_is_not_a_dictionary_error(self):
        validator = validators.BillingFeatures()
        value = {
            'cashback_100': [
                9999,
                1234,
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: A feature (cashback_100) value is not a dictionary',
        )

    def test_invalid_feature_name_error(self):
        validator = validators.BillingFeatures()
        value = {
            '100% Cashback': {
                'region_id': 9999,
            },
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: The name of the feature (100% Cashback) doesn\'t match the pattern ^[abcdefghijklmnopqrstuvwxyz0123456789_-]{1,20}$',
        )

    def test_invalid_string_attribute_error(self):
        validator = validators.BillingFeatures()
        value = {
            'cashback_100': {
                'brand': '100% Cashback',
            },
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: The value (100% Cashback) of attribute (brand) of the feature (cashback_100) doesn\'t match the pattern ^[abcdefghijklmnopqrstuvwxyz0123456789_-]{1,20}$',
        )

    def test_unknown_feature_attribute_error(self):
        validator = validators.BillingFeatures()
        value = {
            'cashback_100': {
                'in_trial': True,
                'paid_trial': False,
                'region_id': 0,
                'trial_duration': 0,
                'unknown_attribute': 'value',
            },
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            "Cannot parse/validate JSON: 'FeatureAttributes' object has no attribute 'UnknownAttribute'"
        )

    def test_invalid_feature_attribute_type(self):
        validator = validators.BillingFeatures()
        value = {
            'cashback_100': {
                'in_trial': True,
                'paid_trial': False,
                'region_id': 0,
                'trial_duration': 0.4,
            },
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: 0.4 has type float, but expected one of: int, long',
        )

    def test_a_lot_of_features_error(self):
        validator = validators.BillingFeatures()
        value = dict([
            ('feature_{}'.format(i), dict()) for i in range(0, validators.BillingFeatures.MAX_FEATURES_COUNT + 1)
        ])
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Max features count is 20',
        )


class TestPlusSubscriberStateValidator(unittest.TestCase):
    def test_empty_ok(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {}
        eq_(
            validator.to_python(json.dumps(value)),
            '',
        )

    def test_available_and_frozen_features_sorted_as_proto_ok(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 111,
                    'Value': 'foo',
                    'End': 1234567890,
                },
                {
                    'Id': 222,
                },
            ],
            'AvailableFeaturesEnd': 1234567899,
            'FrozenFeatures': [
                {
                    'Id': 333,
                    'Value': 'bar',
                },
            ],
        }
        eq_(
            validator.to_python(json.dumps(value)),
            '{"AvailableFeatures":[{"End":1234567890,"Id":111,"Value":"foo"},{"Id":222}],"AvailableFeaturesEnd":1234567899,"FrozenFeatures":[{"Id":333,"Value":"bar"}]}',
        )

    def test_available_and_frozen_features_unsorted_to_sorted_ok(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                {
                    'Id': 333,
                    'Value': 'bar',
                },
            ],
            'AvailableFeaturesEnd': 1234567899,
            'AvailableFeatures': [
                {
                    'Value': 'foo',
                    'Id': 111,
                    'End': 1234567890,
                },
                {
                    'Id': 222,
                },
            ],
        }
        eq_(
            validator.to_python(json.dumps(value)),
            '{"AvailableFeatures":[{"End":1234567890,"Id":111,"Value":"foo"},{"Id":222}],"AvailableFeaturesEnd":1234567899,"FrozenFeatures":[{"Id":333,"Value":"bar"}]}',
        )

    def test_available_features_ok(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 111,
                    'End': 1234567890,
                    'Value': 'foo',
                },
                {
                    'Id': 222,
                },
            ],
            'AvailableFeaturesEnd': 1234567899,
        }
        eq_(
            validator.to_python(json.dumps(value)),
            '{"AvailableFeatures":[{"End":1234567890,"Id":111,"Value":"foo"},{"Id":222}],"AvailableFeaturesEnd":1234567899}',
        )

    def test_available_features_with_max_instant_value_ok(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 111,
                    'End': 31556889864403199,
                },
            ],
            'AvailableFeaturesEnd': 31556889864403199,
        }
        eq_(
            validator.to_python(json.dumps(value)),
            '{"AvailableFeatures":[{"End":31556889864403199,"Id":111}],"AvailableFeaturesEnd":31556889864403199}',
        )

    def test_frozen_features_ok(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                {
                    'Id': 333,
                    'Value': 'bar',
                },
            ],
        }
        eq_(
            validator.to_python(json.dumps(value)),
            '{"FrozenFeatures":[{"Id":333,"Value":"bar"}]}',
        )

    def test_invalid_json_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = u'''{
            "AvailableFeatures": [
                {
                    "Id": 111,
                    "End"
                }
            ]
        }'''
        with assert_raises(validators.Invalid) as e:
            validator.to_python(value)
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Expecting \':\' delimiter: line 6 column 17 (char 128)',
        )

    def test_not_a_dictionary_value_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = [
            {
                'Id': 111,
            },
        ]
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: A field value is not a dictionary',
        )

    def test_available_features_empty_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: At least AvailableFeatures or FrozenFeatures must be in the state',
        )

    def test_frozen_features_empty_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: At least AvailableFeatures or FrozenFeatures must be in the state',
        )

    def test_available_and_frozen_features_empty_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [],
            'FrozenFeatures': [],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: At least AvailableFeatures or FrozenFeatures must be in the state',
        )

    def test_available_feature_is_not_a_dictionary_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                [
                    111,
                ],
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        ok_(
            e.exception.msg.startswith('Cannot parse/validate JSON: Failed to parse AvailableFeatures field: Failed to parse 111 field: expected string or ')
        )

    def test_available_feature_id_empty_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {},
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature must contain an Id',
        )

    def test_available_feature_value_long_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 111,
                    'Value': 'q' * 41,
                },
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature value must match the pattern ^[\\x20-\\x7E]{1,40}$',
        )

    def test_available_feature_value_invalid_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 111,
                    'Value': '\x09',
                },
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature value must match the pattern ^[\\x20-\\x7E]{1,40}$',
        )

    def test_available_features_too_much_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [{'Id': i} for i in range(0, 51)],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature list size must be less than 50',
        )

    def test_available_features_end_empty_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 111,
                },
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: AvailableFeaturesEnd must be in a state if AvailableFeatures list is not empty',
        )

    def test_available_feature_id_type_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 0.4,
                },
            ],
            'AvailableFeaturesEnd': 1234567899,
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Failed to parse AvailableFeatures field: Failed to parse Id field: Couldn\'t parse integer: 0.4...',
        )

    def test_available_feature_id_negative_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': -111,
                },
            ],
            'AvailableFeaturesEnd': 1234567899,
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Failed to parse AvailableFeatures field: Failed to parse Id field: Value out of range: -111..',
        )

    def test_frozen_feature_is_not_a_dictionary_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                [
                    333,
                ],
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        ok_(
            e.exception.msg.startswith('Cannot parse/validate JSON: Failed to parse FrozenFeatures field: Failed to parse 333 field: expected string or ')
        )

    def test_frozen_feature_id_empty_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                {},
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature must contain an Id',
        )

    def test_frozen_feature_value_long_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                {
                    'Id': 111,
                    'Value': 'q' * 41,
                },
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature value must match the pattern ^[\\x20-\\x7E]{1,40}$',
        )

    def test_frozen_feature_value_invalid_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                {
                    'Id': 111,
                    'Value': '\x09',
                },
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature value must match the pattern ^[\\x20-\\x7E]{1,40}$',
        )

    def test_frozen_feature_id_type_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                {
                    'Id': 0.4,
                },
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Failed to parse FrozenFeatures field: Failed to parse Id field: Couldn\'t parse integer: 0.4...',
        )

    def test_frozen_feature_id_negative_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [
                {
                    'Id': -333,
                },
            ],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Failed to parse FrozenFeatures field: Failed to parse Id field: Value out of range: -333..',
        )

    def test_frozen_features_too_much_error(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'FrozenFeatures': [{'Id': i} for i in range(0, 51)],
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        eq_(
            e.exception.msg,
            'Cannot parse/validate JSON: Feature list size must be less than 50',
        )

    def test_unknown_field_ok(self):
        validator = validators.PlusSubscriberStateValidator()
        value = {
            'AvailableFeatures': [
                {
                    'Id': 111,
                    'End': 1234567890,
                    'Value': 'foo',
                },
                {
                    'Id': 222,
                },
            ],
            'AvailableFeaturesEnd': 1234567899,
            'FrozenFeatures': [
                {
                    'Id': 333,
                    'Value': 'bar',
                },
            ],
            'SomethingUnknown': '',
        }
        with assert_raises(validators.Invalid) as e:
            validator.to_python(json.dumps(value))
        ok_(
            e.exception.msg.startswith('Cannot parse/validate JSON: Message type "plus_subscriber_state.PlusSubscriberState" has no field named "SomethingUnknown"')
        )


class TestAnyOfStringsOrEmptyValidator(unittest.TestCase):
    def test_ok(self):
        validator = validators.AnyOfStringsOrEmptyValidator(['foo', 'bar'], strip=True)
        assert validator.to_python('foo') == 'foo'
        assert validator.to_python('  foo  ') == 'foo'
        assert validator.to_python('bar') == 'bar'
        assert validator.to_python('zar') == ''


class TestPublicId(unittest.TestCase):
    def test_passed(self):
        v = validators.PublicId()
        v.to_python('a')
        v.to_python('a.a-a')
        v.to_python('aaa.a0')
        v.to_python('a.a.a.a0')
        v.to_python('a' * 30)

    @parameterized.expand([
        ('a a',),
        ('a.',),
        ('0',),
        ('a..a',),
        ('a.-a',),
        ('a-.a',),
        ('a--a',),
        ('.a',),
        ('a' * 31,),
        ('Абырвалг',),
    ])
    @raises(validators.Invalid)
    def test_failed(self, value):
        v = validators.PublicId()
        v.to_python(value)

    @parameterized.expand([
        ('.foo..bar--qwe.-rty-.', {'public_id': ['startsWithDot', 'endsWithDot', 'doubledDot', 'doubledHyphen', 'dotHyphen', 'hyphenDot']}),
        ('1foo..bar£qwe.-rty' + 'a' * 300 + '-', {'public_id': ['startsWithDigit', 'endsWithHyphen', 'doubledDot', 'dotHyphen', 'prohibitedSymbols', 'tooLong']}),
        ('-foo..bar£qwe-.rty' + 'a' * 300 + '-', {'public_id': ['startsWithHyphen', 'endsWithHyphen', 'doubledDot', 'hyphenDot', 'prohibitedSymbols', 'tooLong']}),
        ('asd fgh', {'public_id': ['prohibitedSymbols']}),
        ('asdfgh#аа', {'public_id': ['prohibitedSymbols']}),
    ])
    def test_expected_errors(self, value, expected_codes):
        check_error_codes(validators.PublicId, value, expected_codes)


class TestPasswordForAuth(unittest.TestCase):
    def test_passed(self):
        v = validators.PasswordForAuth()
        v.to_python('a')
        v.to_python('a' * 255)

    def test_invalid_passwords(self):
        invalid_passwords = [
            'a' * 256,
        ]

        for invalid_password in invalid_passwords:
            check_error_codes(validators.PasswordForAuth, invalid_password, {'password': ['notMatched']})


class TestVersion(unittest.TestCase):
    def test_passed(self):
        v = validators.Version()
        v.to_python('1')
        v.to_python('10')
        v.to_python('12345678')
        v.to_python('12345678.9012345')
        v.to_python('1.2')
        v.to_python('10.20')
        v.to_python('1.2.3')
        v.to_python('1.2.3.4')
        v.to_python('1.2.3.4.5')

    @parameterized.expand([
        ('a',),
        ('abcdef',),
        ('привет',),
        ('.1',),
        ('1.',),
        ('1.2.',),
        ('.1.2',),
        ('1 2',),
        ('1-2',),
        ('1,2',),
    ])
    def test_failed(self, value):
        with self.assertRaises(validators.Invalid):
            validators.Version().to_python(value)
