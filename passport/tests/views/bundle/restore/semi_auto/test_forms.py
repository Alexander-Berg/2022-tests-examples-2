# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.restore.semi_auto.forms import (
    RestoreSemiAutoCommitShortForm,
    RestoreSemiAutoSubmitForm,
    RestoreSemiAutoSubmitWithCaptchaForm,
    RestoreSemiAutoValidateForm,
)
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


@with_settings(
    RESTORE_SEMI_AUTO_MAX_PHOTO_FILE_BYTES=10,
)
class TestForms(unittest.TestCase):
    def test_semi_auto_submit_form(self):
        invalid_params = [
            (
                {},
                ['login.empty'],
            ),
            (
                {
                    'login': '',
                    'request_source': '',
                    'email': 'a@b.c',
                    'question_id': '10',
                    'question': 'Www',
                    'answer': 'a',
                    'phone_number': 'kk915qwe',
                },
                [
                    'login.empty',
                    'request_source.empty',
                ],
            ),
            (
                {
                    'login': 'foobar@',
                    'request_source': '',
                    'email': 'a@b.c',
                    'question_id': '10',
                    'question': 'Www',
                    'answer': 'a',
                    'phone_number': 'kk915qwe',
                },
                [
                    'login.invalid',
                    'request_source.empty',
                ],
            ),
            (
                {
                    'login': 'login',
                    'email': 'a@b.cc',
                    'question_id': '10',
                    'question': 'Www',
                    'answer': 'a',
                    'phone_number': '+79991234567',
                },
                ['form.invalid'],
            ),
        ]

        valid_full_data = {
            'login': 'login@domain.com',
            'request_source': 'some request_source',
            'email': u'Вася@pupkin.com',
            'question': 'Favorite color',
            'answer': 'green',
            'phone_number': '+79151234567',
        }
        valid_full_cleaned_data = dict(
            valid_full_data,
            app_id=None,
            question_id=None,
            phone_number=PhoneNumber.parse('+79151234567'),
        )

        valid_params = [
            (
                {'login': '  login which can\'t be real'},
                {
                    'login': 'login which can\'t be real',  # Принимаем почти все что угодно от пользователя
                    'request_source': 'restore',
                    'app_id': None,
                    'email': None,
                    'question': None,
                    'question_id': None,
                    'answer': None,
                    'phone_number': None,
                },
            ),
            (
                valid_full_data,
                valid_full_cleaned_data,
            ),
        ]

        check_form(RestoreSemiAutoSubmitForm(), invalid_params, valid_params, None)

    def test_semi_auto_submit_with_captcha_form(self):
        invalid_params = [
            (
                {},
                ['login.empty'],
            ),
            (
                {
                    'login': '',
                    'request_source': '',
                },
                [
                    'login.empty',
                    'request_source.empty',
                ],
            ),
            (
                {
                    'login': 'login@domain..com',
                    'request_source': 'test-source',
                },
                [
                    'login.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {'login': 'login'},
                {
                    'login': 'login',
                    'request_source': 'restore',
                    'is_unconditional_pass': False,
                },
            ),
            (
                {'login': '\t+79991234567\n'},
                {
                    'login': '+79991234567',
                    'request_source': 'restore',
                    'is_unconditional_pass': False,
                },
            ),
            (
                {
                    'login': 'login@value.com',
                    'request_source': 'some request_source',
                    'is_unconditional_pass': 'yes',
                },
                {
                    'login': 'login@value.com',
                    'request_source': 'some request_source',
                    'is_unconditional_pass': True,
                },
            ),
        ]

        check_form(RestoreSemiAutoSubmitWithCaptchaForm(), invalid_params, valid_params, None)

    def test_semi_auto_validate_form(self):
        invalid_params = [
            (
                {},
                ['contact_email.empty'],
            ),
            (
                {'contact_email': ''},
                ['contact_email.empty'],
            ),
            (
                {'contact_email': 'abcd'},
                ['contact_email.invalid'],
            ),
            (
                {'contact_email': 'abcd@ cdef'},
                ['contact_email.invalid'],
            ),
        ]
        valid_params = [
            (
                {'contact_email': 'vasia@pupkin.ru'},
                {'contact_email': 'vasia@pupkin.ru'},
            ),
            (
                {'contact_email': u'\tвася@пупкин.рф    '},
                {'contact_email': u'вася@пупкин.рф'},
            ),
        ]

        check_form(RestoreSemiAutoValidateForm(), invalid_params, valid_params, None)

    def test_semi_auto_commit_short_form(self):

        invalid_params = [
            (
                {},
                [
                    'birthday.empty',
                    'eula_accepted.empty',
                    'firstname.empty',
                    'lastname.empty',
                    'registration_country.empty',
                    'registration_date.empty',
                ],
            ),
            (
                {
                    'birthday': '',
                    'eula_accepted': '',
                    'firstname': '',
                    'lastname': '',
                    'registration_country': '',
                    'registration_date': '',
                },
                [
                    'birthday.empty',
                    'eula_accepted.empty',
                    'firstname.empty',
                    'lastname.empty',
                    'registration_country.empty',
                    'registration_date.empty',
                ],
            ),
            (
                {
                    'birthday': '1955-01-41',
                    'eula_accepted': 'falsee',
                    'firstname': 'A',
                    'lastname': 'B',
                    'registration_country': 'Russia',
                    'registration_date': '1999-00-01',
                },
                [
                    'registration_date.invalid',
                    'birthday.invalid',
                    'eula_accepted.invalid',
                ],
            ),
            (
                {
                    'birthday': '1955-01-01',
                    'eula_accepted': 'false',
                    'firstname': 'A',
                    'lastname': 'B',
                    'registration_country': 'Russia',
                    'registration_date': '1999-01-01',
                },
                [
                    'registration_date.tooearly',
                ],
            ),
            (
                {
                    'birthday': '1955-01-01',
                    'eula_accepted': 'false',
                    'firstname': 'A',
                    'lastname': 'B',
                    'registration_country': 'Russia',
                    'registration_date': '9999-12-31',
                },
                [
                    'registration_date.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'birthday': '2000-01-01',
                    'eula_accepted': 'true',
                    'firstname': 'ivan',
                    'lastname': 'ivanov',
                    'registration_country': 'Russia',
                    'registration_date': '2000-01-01',
                },
                {
                    'birthday': '2000-01-01',
                    'eula_accepted': True,
                    'firstname': 'ivan',
                    'lastname': 'ivanov',
                    'registration_country': 'Russia',
                    'registration_date': datetime(2000, 1, 1),
                    'registration_city': None,
                    'registration_city_id': None,
                    'registration_country_id': None,
                },
            ),
            (
                {
                    'birthday': '2000-01-01',
                    'eula_accepted': 'true',
                    'firstname': 'ivan',
                    'lastname': 'ivanov',
                    'registration_country': 'Russia',
                    'registration_date': '2000-01-01',
                    'registration_city': 'Moscow',
                    'registration_city_id': 213,
                    'registration_country_id': 255,
                },
                {
                    'birthday': '2000-01-01',
                    'eula_accepted': True,
                    'firstname': 'ivan',
                    'lastname': 'ivanov',
                    'registration_country': 'Russia',
                    'registration_date': datetime(2000, 1, 1),
                    'registration_city': 'Moscow',
                    'registration_city_id': 213,
                    'registration_country_id': 255,
                },
            ),
        ]

        check_form(RestoreSemiAutoCommitShortForm(), invalid_params, valid_params, None)
