# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_KEY,
    TEST_DISPLAY_NAME,
    TEST_PASSPORT_DISPLAY_NAME_FROM_VARIANTS,
    TEST_PDD_DOMAIN_TEMPLATE,
    TEST_SOCIAL_DISPLAY_NAME_FROM_VARIANTS,
    TEST_SOCIAL_NAME,
    TEST_SOCIAL_PROFILE_ID,
    TEST_SOCIAL_PROVIDER,
)
from passport.backend.api.views.bundle.account import forms
from passport.backend.core import validators
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    FakeBlackbox,
)
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
    PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
)
from passport.backend.core.models.person import DisplayName
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types import birthday
from passport.backend.core.types.gender import Gender
from passport.backend.core.types.phone_number import phone_number
import pytz


TEST_TRACK_ID = 'a' * 34
MAX_LONG_VALUE = 2147483647
TEST_MAILISH_ID_RAW = 'ONXW2ZJNNFSA===='
TEST_MAILISH_ID = 'onxw2zjnnfsa'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    ALT_DOMAINS={
        'galatasaray.net': 2,
        'auto.ru': 1120001,
    },
)
class TestForms(unittest.TestCase):

    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.blackbox = FakeBlackbox()
        self.blackbox.start()

    def tearDown(self):
        self.blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.blackbox
        del self.fake_tvm_credentials_manager

    def test_password_options_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'update_timestamp': 223344,
                },
                {
                    'uid': 1234,
                    'is_changing_required': None,
                    'update_timestamp': 223344,
                    'global_logout': None,
                    'revoke_tokens': None,
                    'revoke_app_passwords': None,
                    'revoke_web_sessions': None,
                    'notify_by_sms': None,
                    'max_change_frequency_in_days': None,
                    'show_2fa_promo': None,
                    'admin_name': None,
                    'comment': None,
                    'changing_requirement_reason': None,
                },
            ),
            (
                {
                    'uid': 1234,
                    'is_changing_required': 'yes',
                    'update_timestamp': 123456,
                    'global_logout': 'true',
                    'revoke_tokens': 'true',
                    'revoke_app_passwords': 'true',
                    'revoke_web_sessions': 'true',
                    'notify_by_sms': 'true',
                    'max_change_frequency_in_days': 12345,
                    'show_2fa_promo': 'yes',
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                },
                {
                    'uid': 1234,
                    'is_changing_required': True,
                    'update_timestamp': 123456,
                    'global_logout': True,
                    'revoke_tokens': True,
                    'revoke_app_passwords': True,
                    'revoke_web_sessions': True,
                    'notify_by_sms': True,
                    'max_change_frequency_in_days': 12345,
                    'show_2fa_promo': True,
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                    'changing_requirement_reason': None,
                },
            ),
            (
                {
                    'uid': 1234,
                    'is_changing_required': 'false',
                    'update_timestamp': '123456',
                    'global_logout': 'false',
                    'revoke_tokens': 'false',
                    'revoke_app_passwords': 'false',
                    'revoke_web_sessions': 'false',
                    'notify_by_sms': 'false',
                    'max_change_frequency_in_days': '12345',
                    'show_2fa_promo': '0',
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                    'changing_requirement_reason': 'PASSWORD_CHANGING_REASON_HACKED',
                },
                {
                    'uid': 1234,
                    'is_changing_required': False,
                    'update_timestamp': 123456,
                    'global_logout': False,
                    'revoke_tokens': False,
                    'revoke_app_passwords': False,
                    'revoke_web_sessions': False,
                    'notify_by_sms': False,
                    'max_change_frequency_in_days': 12345,
                    'show_2fa_promo': False,
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                    'changing_requirement_reason': 'PASSWORD_CHANGING_REASON_HACKED',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty'],
            ),
            (
                {
                    'uid': 234,
                    'changing_requirement_reason': 'I_WANT_IT_SO_BADLY',
                },
                ['changing_requirement_reason.invalid'],
            ),

            # Проверим chained_validators
            (
                {
                    'uid': 234,
                },
                ['form.invalid'],
            ),
            (
                {
                    'uid': 234,
                    'update_timestamp': 123456,
                    'notify_by_sms': True,
                },
                ['is_changing_required.empty'],
            ),
            (
                {
                    'uid': 234,
                    'is_changing_required': '1',
                    'max_change_frequency_in_days': -7,
                },
                ['max_change_frequency_in_days.invalid'],
            ),
            (
                {
                    'uid': 234,
                    'max_change_frequency_in_days': 7,
                },
                ['form.invalid'],
            ),
            (
                {
                    'uid': 234,
                    'show_2fa_promo': True,
                },
                ['form.invalid'],
            ),
            (
                {
                    'uid': 234,
                    'is_changing_required': '1',
                    'comment': 'some comment',
                },
                ['form.invalid'],
            ),
        ]

        check_form(forms.PasswordOptionsForm(), invalid_params, valid_params, None)

    def test_account_options_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'is_enabled': '1',
                },
                {
                    'uid': 1234,
                    'is_enabled': True,
                    'is_app_password_enabled': None,
                    'is_shared': None,
                    'is_maillist': None,
                    'admin_name': None,
                    'comment': None,
                },
            ),
            (
                {
                    'uid': 1234,
                    'is_enabled': 'yes',
                    'is_app_password_enabled': 'true',
                    'is_shared': 'true',
                    'is_maillist': 'true',
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                },
                {
                    'uid': 1234,
                    'is_enabled': True,
                    'is_app_password_enabled': True,
                    'is_shared': True,
                    'is_maillist': True,
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                },
            ),
            (
                {
                    'uid': 1234,
                    'is_enabled': 'false',
                    'is_app_password_enabled': 'false',
                    'is_shared': 'false',
                    'is_maillist': 'false',
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                },
                {
                    'uid': 1234,
                    'is_enabled': False,
                    'is_app_password_enabled': False,
                    'is_shared': False,
                    'is_maillist': False,
                    'admin_name': 'test-admin',
                    'comment': 'some comment',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty'],
            ),

            # Проверим chained_validators
            (
                {
                    'uid': 234,
                },
                ['form.invalid'],
            ),
            (
                {
                    'uid': 234,
                    'is_enabled': '1',
                    'comment': 'some comment',
                },
                ['form.invalid'],
            ),
        ]

        check_form(forms.AccountOptionsForm(), invalid_params, valid_params, None)

    def test_account_alias_delete_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'alias_type': 'altdomain',
                },
                {
                    'uid': 1234,
                    'alias_type': 'altdomain',
                },

            ),
            (
                {
                    'uid': 1234,
                    'alias_type': 'pdddomain',
                },
                {
                    'uid': 1234,
                    'alias_type': 'pdddomain',
                },

            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty', 'alias_type.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'alias_type': 'foo',
                },
                ['alias_type.invalid'],
            ),
        ]

        check_form(forms.AccountAliasDeleteForm(), invalid_params, valid_params, None)

    def test_account_alias_create_form(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                'foo@auto.ru': 'free',
                'bar@auto.ru': 'occupied',
            }),
        )

        valid_params = [
            (
                {
                    'uid': 1234,
                    'alias': 'foo@auto.ru',
                },
                {
                    'uid': 1234,
                    'alias': 'foo@auto.ru',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty', 'alias.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'alias': '   ',
                },
                ['alias.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'alias': 'foo@auto.com',
                },
                ['alias.invalid'],
            ),
            (
                {
                    'uid': 1234,
                    'alias': 'bar@auto.ru',
                },
                ['alias.notavailable'],
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.AccountAliasCreateForm(), invalid_params, valid_params, state)

    def test_account_pdd_create_form(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                'foo@auto.ru': 'free',
                'bar@auto.ru': 'occupied',
            }),
        )

        valid_params = [
            (
                {
                    'uid': 1234,
                    'alias': 'foo@auto.ru',
                },
                {
                    'uid': 1234,
                    'alias': 'foo@auto.ru',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty', 'alias.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'alias': '   ',
                },
                ['alias.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'alias': 'bar@auto.ru',
                },
                ['alias.notavailable'],
            ),
            (
                {
                    'uid': 1234,
                    'alias': 'barauto.ru',
                },
                ['alias.invalid'],
            ),
            (
                {
                    'uid': 1234,
                    'alias': 'bar@yandex.ru',
                },
                ['alias.invalid'],
            )
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.AccountPDDCreateForm(), invalid_params, valid_params, state)

    def test_account_bank_phone_alias_delete_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                },
                {
                    'uid': 1234,
                },

            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty'],
            ),
        ]

        check_form(forms.AccountBankPhoneNumberAliasDeleteForm(), invalid_params, valid_params, None)

    def test_account_bank_phone_alias_create_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'phone_number': '79151234567',
                },
                {
                    'uid': 1234,
                    'phone_number': phone_number.PhoneNumber.parse('79151234567'),
                    'phone_id': None,
                    'country': None,
                },
            ),
            (
                {
                    'uid': 1234,
                    'phone_id': 1,
                },
                {
                    'uid': 1234,
                    'phone_number': None,
                    'phone_id': 1,
                    'country': None,
                },
            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'phone_number': '    ',
                },
                ['phone_number.invalid'],
            ),
            (
                {
                    'uid': 1234,
                    'phone_id': '    ',
                },
                ['phone_id.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'phone_number': '+798',
                },
                ['phone_number.invalid'],
            ),
            (
                {
                    'uid': 1234,
                    'phone_number': '79151234567',
                    'phone_id': 1,
                },
                ['form.invalid'],
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.AccountBankPhoneNumberAliasCreateForm(), invalid_params, valid_params, state)

    def test_account_set_password_form(self):
        valid_md5_salted_hash = '$1$%s$%s' % ('a' * 8, 'b' * 22)
        valid_md5_hex_hash = '1234abcdefABCDEF0123456789abcDEF'

        valid_params = [
            (
                {
                    'uid': 1234,
                    'password': 'password123456',
                },
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'password_hash': None,
                    'force_password_change': False,
                },
            ),
            (
                {
                    'uid': 1234,
                    'password_hash': valid_md5_salted_hash,
                    'force_password_change': 'no',
                },
                {
                    'uid': 1234,
                    'password': None,
                    'password_hash': (
                        PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
                        valid_md5_salted_hash,
                    ),
                    'force_password_change': False,
                },
            ),
            (
                {
                    'uid': 1234,
                    'password_hash': valid_md5_hex_hash,
                    'force_password_change': '1',
                },
                {
                    'uid': 1234,
                    'password': None,
                    'password_hash': (
                        PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
                        valid_md5_hex_hash,
                    ),
                    'force_password_change': True,
                },
            ),
        ]

        invalid_params = [
            (
                {},
                ['uid.empty'],
            ),
            # Необходимо задать значение 'password' или 'password_hash'
            (
                {
                    'uid': 1234,
                },
                ['form.invalid'],
            ),
            # Возможно указание только одного из полей 'password'/'password_hash'
            (
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'password_hash': valid_md5_salted_hash,

                },
                ['form.invalid'],
            ),
            # Указан некорректный хэш
            (
                {
                    'uid': 1234,
                    'password_hash': 'hash_as_it_is',
                },
                ['password_hash.invalid'],
            ),
            # Указан некорректный тип хэша (MD5-crypt, но содержимое - MD5-hex)
            (
                {
                    'uid': 1234,
                    'password_hash': '$1$%s' % 'a' * 32,
                },
                ['password_hash.invalid'],
            ),
            # Указано некорректное значение force_password_change
            (
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'force_password_change': 'bad value',
                },
                ['force_password_change.invalid'],
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.AccountSetPasswordForm(), invalid_params, valid_params, state)

    def test_account_full_info_form(self):
        valid_params = [
            (
                {},
                {
                    'need_display_name_variants': True,
                    'need_phones': True,
                    'need_emails': True,
                    'need_social_profiles': True,
                    'need_question': True,
                    'need_additional_account_data': True,
                    'need_family_info': False,
                    'need_family_invites': False,
                    'need_family_members': False,
                    'need_family_kids': False,
                },
            ),
            (
                {
                    'need_display_name_variants': 'true',
                    'need_phones': 'true',
                    'need_emails': 'true',
                    'need_social_profiles': 'true',
                    'need_question': 'true',
                    'need_additional_account_data': 'true',
                    'need_family_info': 'true',
                    'need_family_members': 'true',
                    'need_family_invites': 'true',
                    'need_family_kids': 'true',
                },
                {
                    'need_display_name_variants': True,
                    'need_phones': True,
                    'need_emails': True,
                    'need_social_profiles': True,
                    'need_question': True,
                    'need_additional_account_data': True,
                    'need_family_info': True,
                    'need_family_members': True,
                    'need_family_invites': True,
                    'need_family_kids': True,

                },
            ),
            (
                {
                    'need_display_name_variants': 'false',
                    'need_phones': 'false',
                    'need_emails': 'false',
                    'need_social_profiles': 'false',
                    'need_question': 'false',
                    'need_additional_account_data': 'false',
                    'need_family_info': 'false',
                    'need_family_members': 'false',
                    'need_family_invites': 'false',
                    'need_family_kids': 'false',

                },
                {
                    'need_display_name_variants': False,
                    'need_phones': False,
                    'need_emails': False,
                    'need_social_profiles': False,
                    'need_question': False,
                    'need_additional_account_data': False,
                    'need_family_info': False,
                    'need_family_members': False,
                    'need_family_invites': False,
                    'need_family_kids': False,

                },
            ),
        ]

        invalid_params = [
            (
                {
                    'need_display_name_variants': 'foo',
                    'need_phones': 'foo',
                    'need_emails': 'foo',
                    'need_social_profiles': 'foo',
                    'need_question': 'foo',
                    'need_additional_account_data': 'foo',

                },
                [
                    'need_display_name_variants.invalid',
                    'need_phones.invalid',
                    'need_emails.invalid',
                    'need_social_profiles.invalid',
                    'need_question.invalid',
                    'need_additional_account_data.invalid',
                ],
            ),
        ]

        check_form(forms.AccountFullInfoForm(), invalid_params, valid_params, None)

    def test_account_personal_info_form(self):
        pdd_display_name = DisplayName()
        pdd_display_name.set(TEST_PDD_DOMAIN_TEMPLATE)

        valid_params = [
            (
                {
                    'uid': 1,
                    'firstname': ' Elon ',
                    'firstname_global': ' Elon ',
                    'lastname': ' Musk ',
                    'lastname_global': ' Musk ',
                    'display_name': ' eMusk ',
                    'gender': 'm',
                    'birthday': '1971-06-28',
                    'country': 'ru',
                    'language': 'ru',
                    'city': 'Moscow',
                    'city_id': 214,
                    'timezone': 'Europe/Moscow',
                    'contact_phone_number': '+78009008080',
                    'public_id': 'Elon.Musk',
                },
                {
                    'uid': 1,
                    'track_id': None,
                    'firstname': 'Elon',
                    'firstname_global': 'Elon',
                    'lastname': 'Musk',
                    'lastname_global': 'Musk',
                    'display_name': DisplayName(name='eMusk'),
                    'gender': Gender.Male,
                    'birthday': birthday.Birthday.parse('1971-06-28'),
                    'country': 'ru',
                    'language': 'ru',
                    'city': 'Moscow',
                    'city_id': 214,
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'contact_phone_number': phone_number.PhoneNumber.parse('+78009008080'),
                    'force_clean_web': False,
                    'public_id': 'Elon.Musk',
                },
            ),
            (
                {
                    'track_id': TEST_TRACK_ID,
                    'contact_phone_number': ' +78009008080  ',
                },
                {
                    'track_id': TEST_TRACK_ID,
                    'uid': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': None,
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'language': None,
                    'city': None,
                    'city_id': None,
                    'timezone': None,
                    'contact_phone_number': phone_number.PhoneNumber.parse('+78009008080'),
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'uid': 3,
                    'display_name': ' chumscrabber ',
                    'provider': 'vk',
                    'profile_id': 3,
                },
                {
                    'uid': 3,
                    'track_id': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': DisplayName(name='chumscrabber', provider='vk', profile_id=3),
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'language': None,
                    'city': None,
                    'city_id': None,
                    'timezone': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'track_id': TEST_TRACK_ID,
                    'birthday': '',
                    'city': '',
                },
                {
                    'uid': None,
                    'track_id': TEST_TRACK_ID,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': None,
                    'gender': None,
                    'birthday': '',
                    'country': None,
                    'city': '',
                    'city_id': None,
                    'timezone': None,
                    'language': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'uid': 4,
                    'city_id': 214,
                },
                {
                    'uid': 4,
                    'track_id': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': None,
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'city': None,
                    'city_id': 214,
                    'timezone': None,
                    'language': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'uid': 5,
                    'city_id': u'214',
                },
                {
                    'uid': 5,
                    'track_id': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': None,
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'city': None,
                    'city_id': 214,
                    'timezone': None,
                    'language': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'uid': 6,
                    'display_name': TEST_PASSPORT_DISPLAY_NAME_FROM_VARIANTS,
                    'is_from_variants': True,
                },
                {
                    'uid': 6,
                    'track_id': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': DisplayName(name=TEST_DISPLAY_NAME),
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'city': None,
                    'city_id': None,
                    'timezone': None,
                    'language': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'uid': 7,
                    'display_name': TEST_PASSPORT_DISPLAY_NAME_FROM_VARIANTS,
                    'is_from_variants': False,
                },
                {
                    'uid': 7,
                    'track_id': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': DisplayName(name=TEST_PASSPORT_DISPLAY_NAME_FROM_VARIANTS),
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'city': None,
                    'city_id': None,
                    'timezone': None,
                    'language': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'uid': 8,
                    'display_name': TEST_SOCIAL_DISPLAY_NAME_FROM_VARIANTS,
                    'is_from_variants': True,
                },
                {
                    'uid': 8,
                    'track_id': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': DisplayName(
                        name=TEST_SOCIAL_NAME,
                        profile_id=TEST_SOCIAL_PROFILE_ID,
                        provider=TEST_SOCIAL_PROVIDER,
                    ),
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'city': None,
                    'city_id': None,
                    'timezone': None,
                    'language': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
            (
                {
                    'uid': 9,
                    'display_name': TEST_PDD_DOMAIN_TEMPLATE,
                    'is_from_variants': True,
                },
                {
                    'uid': 9,
                    'track_id': None,
                    'firstname': None,
                    'firstname_global': None,
                    'lastname': None,
                    'lastname_global': None,
                    'display_name': pdd_display_name,
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'city': None,
                    'city_id': None,
                    'timezone': None,
                    'language': None,
                    'contact_phone_number': None,
                    'force_clean_web': False,
                    'public_id': None,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['form.invalid'],
            ),
            (
                {'uid': 1, 'track_id': TEST_TRACK_ID},
                ['form.invalid'],
            ),
            (
                {'uid': 1},
                ['form.invalid'],
            ),
            (
                {
                    'uid': '',
                    'track_id': '',
                    'firstname': '',
                    'lastname': '',
                    'gender': '',
                    'country': '',
                    'is_from_variants': '',
                    'timezone': '',
                    'display_name': '',
                    'language': '',
                    'contact_phone_number': '',
                    'city_id': '',
                    'public_id': '',
                },
                ['uid.empty', 'track_id.empty', 'firstname.empty', 'lastname.empty',
                 'gender.empty', 'country.empty', 'timezone.empty', 'display_name.empty',
                 'is_from_variants.empty', 'language.empty', 'contact_phone_number.empty',
                 'city_id.empty', 'public_id.empty'],
            ),
            (
                {
                    'uid': 2,
                    'city_id': 0,
                },
                ['city_id.invalid'],
            ),
            (
                {
                    'uid': 3,
                    'city_id': 4000,
                },
                ['city_id.invalid'],
            ),
            (
                {
                    'uid': 4,
                    'city_id': MAX_LONG_VALUE + 1,
                },
                ['city_id.invalid'],
            ),
            (
                {
                    'uid': 5,
                    'city_id': 'city_id',
                },
                ['city_id.invalid'],
            ),
            (
                {
                    'track_id': TEST_TRACK_ID,
                    'birthday': '12-12-12',
                },
                ['birthday.invalid'],
            ),
            (
                {
                    'track_id': TEST_TRACK_ID,
                    'birthday': '0000-12-12',
                },
                ['birthday.invalid'],
            ),
            (
                {
                    'track_id': TEST_TRACK_ID,
                    'birthday': '2004-00-12',
                },
                ['birthday.invalid'],
            ),
            (
                {
                    'track_id': TEST_TRACK_ID,
                    'birthday': '1999-01-00',
                },
                ['birthday.invalid'],
            ),
            (
                {
                    'track_id': TEST_TRACK_ID,
                    'birthday': '0000-00-00',
                },
                ['birthday.invalid'],
            ),
        ]
        check_form(forms.AccountPersonalInfoForm(), invalid_params, valid_params, None)

    def test_account_flush_pdd_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'password': 'password123456',
                },
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'force_password_change': False,
                },
            ),
            (
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'force_password_change': 'no',
                },
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'force_password_change': False,
                },
            ),
            (
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'force_password_change': '1',
                },
                {
                    'uid': 1234,
                    'password': 'password123456',
                    'force_password_change': True,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['uid.empty', 'password.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                    'password': 'password123456',
                    'force_password_change': 'bad value',
                },
                ['uid.invalid', 'force_password_change.invalid'],
            ),
        ]

        check_form(forms.FlushPddCommitForm(), invalid_params, valid_params, None)

    def test_migrate_mailish_form(self):
        valid_params = [
            (
                {
                    'email': 'admin@google.ru',
                    'mailish_id': TEST_MAILISH_ID_RAW,
                },
                {
                    'email': 'admin@google.ru',
                    'mailish_id': TEST_MAILISH_ID,
                },
            ),
            (
                {
                    'email': '  admin@google.ru  ',
                    'mailish_id': '  %s  ' % TEST_MAILISH_ID,
                },
                {
                    'email': 'admin@google.ru',
                    'mailish_id': TEST_MAILISH_ID,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['email.empty', 'mailish_id.empty'],
            ),
            (
                {
                    'email': 'wtf',
                    'mailish_id': 'wtf',
                },
                ['email.invalid', 'mailish_id.invalid'],
            ),
            (
                {
                    'email': 'admin@google.ru',
                    'mailish_id': 'a' * 256,
                },
                ['mailish_id.long'],
            ),
        ]

        check_form(forms.MigrateMailishForm(), invalid_params, valid_params, None)

    def test_reset_avatar_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'avatar_key': TEST_AVATAR_KEY,
                },
                {
                    'uid': 1234,
                    'avatar_key': TEST_AVATAR_KEY,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['uid.empty', 'avatar_key.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                    'avatar_key': '',
                },
                ['uid.invalid', 'avatar_key.empty'],
            ),
        ]

        check_form(forms.AccountResetAvatarForm(), invalid_params, valid_params, None)

    def test_reset_display_name_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'full_name': TEST_DISPLAY_NAME,
                },
                {
                    'uid': 1234,
                    'full_name': TEST_DISPLAY_NAME,
                    'public_name': None,
                },
            ),
            (
                {
                    'uid': 1234,
                    'public_name': TEST_DISPLAY_NAME,
                },
                {
                    'uid': 1234,
                    'full_name': None,
                    'public_name': TEST_DISPLAY_NAME,
                },
            ),
        ]
        invalid_params = [
            (
                {
                    'public_name': TEST_DISPLAY_NAME,
                },
                ['uid.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                    'public_name': TEST_DISPLAY_NAME,
                },
                ['uid.invalid'],
            ),
            (
                {
                    'uid': 1234,
                },
                ['form.invalid'],
            ),
            (
                {
                    'uid': 1234,
                    'full_name': TEST_DISPLAY_NAME,
                    'public_name': TEST_DISPLAY_NAME,
                },
                ['form.invalid'],
            ),
        ]

        check_form(forms.AccountResetDisplayNameForm(), invalid_params, valid_params, None)

    def test_reset_question_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                },
                {
                    'uid': 1234,
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['uid.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                },
                ['uid.invalid'],
            ),
        ]

        check_form(forms.AccountResetQuestionForm(), invalid_params, valid_params, None)

    def test_reset_email_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'email': 'admin@google.ru',
                },
                {
                    'uid': 1234,
                    'email': 'admin@google.ru',
                },
            ),
            (
                {
                    'uid': 1234,
                    'email': '  admin@google.ru  ',
                },
                {
                    'uid': 1234,
                    'email': 'admin@google.ru',
                },
            ),
        ]
        invalid_params = [
            (
                {
                    'email': 'admin@google.ru',
                },
                ['uid.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                    'email': 'admin@google.ru',
                },
                ['uid.invalid'],
            ),
            (
                {
                    'uid': 1234,
                },
                ['email.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'email': '',
                },
                ['email.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                    'email': 'wtf',
                },
                ['email.invalid', 'uid.invalid'],
            ),
        ]

        check_form(forms.AccountResetEmailForm(), invalid_params, valid_params, None)

    def test_reset_phone_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                    'phone_number': '+78009008080',
                },
                {
                    'uid': 1234,
                    'phone_number': phone_number.PhoneNumber.parse('+78009008080')
                },
            ),
            (
                {
                    'uid': 1234,
                    'phone_number': '+7(800)900-8080',
                },
                {
                    'uid': 1234,
                    'phone_number': phone_number.PhoneNumber.parse('+78009008080')
                },
            ),
        ]
        invalid_params = [
            (
                {
                    'phone_number': '+78009008080',
                },
                ['uid.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                    'phone_number': '+78009008080',
                },
                ['uid.invalid'],
            ),
            (
                {
                    'uid': 1234,
                },
                ['phone_number.empty'],
            ),
            (
                {
                    'uid': 1234,
                    'phone_number': '',
                },
                ['phone_number.empty'],
            ),
            (
                {
                    'uid': 'wtf',
                    'phone_number': 'wtf',
                },
                ['uid.invalid'],
            ),
        ]

        check_form(forms.AccountResetPhoneForm(), invalid_params, valid_params, None)
