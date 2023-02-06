# -*- coding: utf-8 -*-

import unittest

from passport.backend.api.test.utils import check_bundle_form
from passport.backend.api.views.bundle.validate import forms
from passport.backend.core import validators
from passport.backend.core.models.person import DisplayName
from passport.backend.core.test.consts import (
    TEST_PHONE_ID1,
    TEST_UID,
)
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')


@with_settings
class TestValidationForms(unittest.TestCase):
    def test_validate_phone_number_form(self):
        invalid_params = [
            ({}, ['phone_number.empty']),
            ({'phone_number': 'abcd'}, ['phone_number.invalid']),
            ({'phone_number': '89261234567'}, ['phone_number.invalid']),
            ({'phone_number': TEST_PHONE_NUMBER.e164, 'validate_for_call': 'nope'}, ['validate_for_call.invalid']),
        ]

        valid_params = [
            ({'phone_number': TEST_PHONE_NUMBER.e164},
             {'phone_number': TEST_PHONE_NUMBER, 'country': None, 'validate_for_call': False}),
            (
                {'phone_number': '89261234567', 'country': 'ru', 'validate_for_call': 'yes'},
                {
                    'phone_number': PhoneNumber.parse('+79261234567'),
                    'country': 'ru',
                    'validate_for_call': True,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.PhoneNumberForm(), invalid_params, valid_params, state)

    def test_validate_phone_number_by_squatter_form(self):
        invalid_params = [
            ({}, ['phone_number.empty']),
            ({'phone_number': 'abcd'}, ['phone_number.invalid']),
            ({'phone_number': '89261234567'}, ['phone_number.invalid']),
            ({'phone_number': 'TEST_PHONE_NUMBER.e164', 'scenario': 'foo'}, ['scenario.invalid']),
        ]

        valid_params = [
            (
                {'phone_number': TEST_PHONE_NUMBER.e164},
                {
                    'phone_number': TEST_PHONE_NUMBER,
                    'country': None,
                    'scenario': 'register',
                },
            ),
            (
                {'phone_number': '89261234567', 'country': 'ru', 'scenario': 'auth'},
                {
                    'phone_number': PhoneNumber.parse('+79261234567'),
                    'country': 'ru',
                    'scenario': 'auth',
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.PhoneNumberBySquatterForm(), invalid_params, valid_params, state)

    def test_validate_phone_id_form(self):
        invalid_params = [
            ({}, ['phone_id.empty']),
            ({'phone_id': 'abc'}, ['phone_id.invalid']),
            ({'phone_id': TEST_PHONE_ID1, 'uid': 'abc'}, ['uid.invalid']),
        ]

        valid_params = [
            ({'phone_id': TEST_PHONE_ID1},
             {'phone_id': TEST_PHONE_ID1, 'uid': None}),
            ({'phone_id': TEST_PHONE_ID1, 'uid': TEST_UID},
             {'phone_id': TEST_PHONE_ID1, 'uid': TEST_UID}),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.PhoneIDForm(), invalid_params, valid_params, state)

    def test_validate_login_form(self):
        invalid_params = [
            ({}, ['login.empty']),
            ({'login': 'cooper@black.org', 'ignore_stoplist': ''}, ['ignore_stoplist.empty']),
            ({'login': 'cooper@black.org', 'is_pdd': '1', 'is_lite': '1'}, ['form.invalid']),
        ]

        valid_params = [
            (
                {
                    'login': 'double..dot..guy@common.org',
                },
                {
                    'login': 'double..dot..guy@common.org',
                    'is_pdd': False,
                    'is_lite': False,
                    'ignore_stoplist': False,
                    'strict': False,
                    'require_domain_existence': True,
                },
            ),
            (
                {
                    'login': 'volozh.2015.@common.org',
                    'is_pdd': 'true',
                    'ignore_stoplist': 'true',
                    'strict': 'true',
                },
                {
                    'login': 'volozh.2015.@common.org',
                    'is_pdd': True,
                    'is_lite': False,
                    'ignore_stoplist': True,
                    'strict': True,
                    'require_domain_existence': True,
                },
            ),
            (
                {
                    'login': ' cooper@common.org  ',
                    'strict': ' ',
                    'is_lite': ' yes ',
                    'require_domain_existence': 'f',
                },
                {
                    'login': 'cooper@common.org',
                    'is_pdd': False,
                    'is_lite': True,
                    'ignore_stoplist': False,
                    'strict': False,
                    'require_domain_existence': False,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.LoginForm(), invalid_params, valid_params, state)

    def test_validate_lite_login_form(self):
        invalid_params = [
            (
                {},
                ['login.empty'],
            ),
            (
                {'login': 'foo@yandex.ru'},
                ['login.native'],
            ),
            (
                {'login': 'a' * 40 + '@gmail.ru'},
                ['login.long'],
            ),
            (
                {'login': 'admin@xn--80atjc.xn--p1ai'},
                ['login.invalid'],
            ),
            (
                {'login': u'admin@окна.рф'},
                ['login.prohibitedsymbols'],
            ),
        ]

        valid_params = [
            (
                {
                    'login': 'foo@gmail.com',
                },
                {
                    'login': 'foo@gmail.com',
                },
            ),
            (
                {
                    'login': ' cooper@common.org  ',
                },
                {
                    'login': 'cooper@common.org',
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.LiteLoginForm(), invalid_params, valid_params, state)

    def test_validate_password_form(self):
        invalid_params = [
            (
                {},
                ['password.empty'],
            ),
            (
                {'password': 'pass', 'policy': 'foo', 'country': 'foo'},
                ['policy.invalid', 'country.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'password': 'pass',
                },
                {
                    'password': 'pass',
                    'login': None,
                    'policy': None,
                    'phone_number': None,
                    'country': None,
                }),
            (
                {
                    'password': 'pass',
                    'login': 'test.login',
                    'policy': 'strong',
                    'phone_number': '+79261234567',
                    'country': 'ru',
                },
                {
                    'password': 'pass',
                    'login': 'test.login',
                    'policy': 'strong',
                    'phone_number': '+79261234567',
                    'country': 'ru',
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.PasswordForm(), invalid_params, valid_params, state)

    def test_validate_display_name_form(self):
        valid_params = [
            (
                {
                    'display_name': ' eMusk ',
                },
                {
                    'display_name': DisplayName(name='eMusk'),
                    'force_clean_web': False,
                },
            ),
            (
                {
                    'display_name': ' chumscrabber ',
                    'provider': 'vk',
                    'profile_id': 3,
                },
                {
                    'display_name': DisplayName(name='chumscrabber', provider='vk', profile_id=3),
                    'force_clean_web': False,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['form.invalid'],
            ),
            (
                {
                    'display_name': '',
                },
                ['display_name.empty'],
            ),
            (
                {
                    'display_name': u'\u200c',
                },
                ['display_name.invalid'],
            ),
        ]
        check_bundle_form(forms.DisplayNameForm(), invalid_params, valid_params, None)

    def test_validate_firstname_form(self):
        valid_params = [
            (
                {
                    'firstname': ' Elon ',
                },
                {
                    'firstname': 'Elon',
                    'force_clean_web': False,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['firstname.empty'],
            ),
            (
                {
                    'firstname': '',
                },
                ['firstname.empty'],
            ),
            (
                {
                    'firstname': 'A' * 51,
                },
                ['firstname.long'],
            ),
            (
                {
                    'firstname': u'\u200c',
                },
                ['firstname.invalid'],
            )
        ]
        check_bundle_form(forms.FirstNameForm(), invalid_params, valid_params, None)

    def test_validate_lastname_form(self):
        valid_params = [
            (
                {
                    'lastname': ' Musk ',
                },
                {
                    'lastname': 'Musk',
                    'force_clean_web': False,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['lastname.empty'],
            ),
            (
                {
                    'lastname': '',
                },
                ['lastname.empty'],
            ),
            (
                {
                    'lastname': 'A' * 51,
                },
                ['lastname.long'],
            ),
            (
                {
                    'lastname': u'\u200c',
                },
                ['lastname.invalid'],
            )
        ]
        check_bundle_form(forms.LastNameForm(), invalid_params, valid_params, None)

    def test_validate_fullname_form(self):
        valid_params = [
            (
                {
                    'lastname': ' Musk ',
                },
                {
                    'firstname': None,
                    'lastname': 'Musk',
                    'force_clean_web': False,
                },
            ),
            (
                {
                    'firstname': ' Elon ',
                },
                {
                    'firstname': 'Elon',
                    'lastname': None,
                    'force_clean_web': False,
                },
            ),
            (
                {
                    'firstname': ' Elon ',
                    'lastname': ' Musk ',
                },
                {
                    'firstname': 'Elon',
                    'lastname': 'Musk',
                    'force_clean_web': False,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                [
                    'form.invalid',
                ]
            ),
            (
                {
                    'lastname': '',
                },
                [
                    'lastname.empty',
                ]
            ),
            (
                {
                    'firstname': '',
                },
                [
                    'firstname.empty',
                ]
            ),
            (
                {
                    'firstname': '',
                    'lastname': ' ',
                },
                [
                    'firstname.empty',
                    'lastname.empty',
                ]
            ),
            (
                {
                    'firstname': 'Elon',
                    'lastname': ' ',
                },
                [
                    'lastname.empty',
                ]
            ),
            (
                {
                    'firstname': 'Elon',
                    'lastname': 'A' * 51,
                },
                ['lastname.long'],
            ),
            (
                {
                    'firstname': 'A' * 51,
                    'lastname': 'Musk',
                },
                ['firstname.long'],
            ),
        ]
        check_bundle_form(forms.FullNameForm(), invalid_params, valid_params, None)

    def test_validate_public_id_form(self):
        valid_params = [
            (
                {
                    'public_id': 'Elon.Musk.1234',
                },
                {
                    'public_id': 'Elon.Musk.1234',
                    'force_clean_web': False,
                    'uid': None,
                    'multisession_uid': None,
                },
            ),
            (
                {
                    'public_id': 'Elon.Musk.1234',
                    'uid': TEST_UID,
                    'multisession_uid': TEST_UID,
                },
                {
                    'public_id': 'Elon.Musk.1234',
                    'force_clean_web': False,
                    'uid': TEST_UID,
                    'multisession_uid': TEST_UID,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['public_id.empty'],
            ),
            (
                {
                    'public_id': '  ',
                },
                ['public_id.empty'],
            ),
            (
                {
                    'public_id': 'A' * 31,
                },
                ['public_id.long'],
            ),
            (
                {
                    'public_id': u'Илон',
                },
                ['public_id.prohibitedsymbols'],
            ),
            (
                {
                    'public_id': u'musk.',
                },
                ['public_id.endwithdot'],
            ),
            (
                {
                    'public_id': u'0musk',
                },
                ['public_id.startswithdigit'],
            ),
        ]
        check_bundle_form(forms.PublicIdForm(), invalid_params, valid_params, None)
