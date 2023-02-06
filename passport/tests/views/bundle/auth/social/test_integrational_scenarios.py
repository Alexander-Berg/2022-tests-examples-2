# -*- coding: utf-8 -*-

import time

import mock
from nose.tools import eq_
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth.faker import oauth_bundle_error_response
from passport.backend.core.builders.oauth.oauth import OAUTH_FORBIDDEN_ACCOUNT_TYPE_ERROR_DESCRIPTION
from passport.backend.core.builders.social_broker.exceptions import SocialBrokerTemporaryError
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.utils import (
    check_url_contains_params,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import merge_dicts

from .base_test_data import (
    TEST_APPLICATION,
    TEST_BROKER_CONSUMER,
    TEST_CODE_CHALLENGE,
    TEST_CODE_CHALLENGE_METHOD,
    TEST_HOST,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_PHONE_ID,
    TEST_PHONE_NUMBER,
    TEST_PROVIDER,
    TEST_PROVIDER_TOKEN,
    TEST_RETPATH,
    TEST_RETPATH_NONSTANDARD_SCHEME,
    TEST_SCOPE,
    TEST_SERVICE,
    TEST_SOCIAL_OTHER_UID,
    TEST_SOCIAL_UID,
    TEST_TASK_ID,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_USER_LOGIN,
    TEST_YANDEXUID_COOKIE,
)
from .integrational_base import TestSocialIntegrationalBase


TEST_AUTH_ID = '123:1422501443:126'
TEST_SESSIONID = 'old-sessionid'
TEST_ORIGIN = 'origin'

TEST_DEVICE_INFO = {
    'app_id': 'device_application',
    'app_platform': 'device_os_id',
    'os_version': 'device_os_version',
    'app_version': 'device_application_version',
    'manufacturer': 'device_manufacturer',
    'model': 'device_hardware_model',
    'uuid': 'device_app_uuid',
    'deviceid': 'device_hardware_id',
    'ifv': 'device_ifv',
    'device_name': 'device_name',
}


@with_settings_hosts(
    ALLOWED_SOCIAL_RETPATH_SCHEMES=['yandexmail'],
    BLACKBOX_URL='localhost',
    LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=1,
    OAUTH_RETRIES=1,
    OAUTH_URL='http://localhost/',
    PASSPORT_SUBDOMAIN='passport-test',
    SOCIAL_PROVIDERS_TO_USE_EXTERNAL_USERAGENT=('gg', 'google'),
    YABS_URL='localhost',
    YAPICS_URL='localhost',
)
class TestSocialIntegrationalScenarios(TestSocialIntegrationalBase):
    start_args = {
        'retpath': TEST_RETPATH,
        'place': 'query',
        'provider': TEST_PROVIDER['code'],
        'application': TEST_APPLICATION,
        'broker_consumer': TEST_BROKER_CONSUMER,
    }
    start_args_with_service = dict(start_args, service=TEST_SERVICE)
    start_args_with_code_challenge = dict(
        start_args,
        code_challenge=TEST_CODE_CHALLENGE,
        code_challenge_method=TEST_CODE_CHALLENGE_METHOD,
    )
    native_start_args = {
        'retpath': TEST_RETPATH,
        'place': 'query',
        'provider': TEST_PROVIDER['code'],
        'provider_token': TEST_PROVIDER_TOKEN,
        'scope': TEST_SCOPE,
        'broker_consumer': TEST_BROKER_CONSUMER,
    }
    native_start_args_with_device_info = dict(native_start_args, **TEST_DEVICE_INFO)

    def test_callback_auth(self):
        """
        Никаких ошибок, авторизуемся в /callback
        """

        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся:
        self.mock_callback_externals(profiles_count=1)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_auth_response(response, check_subscription=True)
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            uids_count='1',
        )

        create_session_url = self.env.blackbox._mock.request.call_args_list[1][0][1]
        check_url_contains_params(
            create_session_url,
            {
                'social_id': '123456789',
            },
        )

        # попробуем сходить еще раз в какую-нибудь ручку
        self.mock_callback_externals(
            profiles_count=1,
            # На повторный вызов данные соц. таски уже будут в треке, поэтому
            # Паспорт не пойдёт за ними в Социализм.
            with_social_api_get_task_data_request=False,
        )
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}

        response = self.make_api_request('callback', data=data)

        self.assert_auth_response(response, check_subscription=True)
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            uids_count='1',
        )

    def test_start_with_origin(self):
        response = self.make_api_request(
            'start',
            data=dict(self.start_args_with_service, origin=TEST_ORIGIN),
        )
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True, origin=TEST_ORIGIN)

    def test_choose_auth(self):
        """
        Никаких ошибок, авторизуемся в /choose
        """
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(3)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_choose_response(response)
        self.assert_records_callback_and_reset(
            'choose',
            uids=[TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID],
            enabled_count=2,
            with_service=False,
        )

        # выбираем первый аккаунт из списка
        uid = self.mock_choose_externals(0)
        data = {'track_id': self.track_id, 'uid': uid}
        response = self.make_api_request('choose', data=data)
        self.assert_auth_response(response, check_subscription=True)
        self.assert_records_choose_and_reset(
            with_service=True,
            uid=TEST_SOCIAL_UID,
            login=TEST_USER_LOGIN,
        )

    def test_register_auth(self):
        """
        Никаких ошибок, авторизуемся в /register
        """
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(0)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_register_response(response)
        self.assert_records_callback_and_reset('register', with_service=False)

        # все же пойдем на регистрацию
        self.mock_register_externals()
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_auth_response(response, check_subscription=True, check_frodo=True, registered=True)
        self.assert_records_register_and_reset(with_service=True)

    def test_register_auth_with_captcha(self):
        """
        Пытаемся зарегистрироваться, просят ввести капчу, ошибаемся, вводим правильно.
        """
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(0)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_register_response(response)
        self.assert_records_callback_and_reset('register', with_service=False)

        # все же пойдем на регистрацию, получим ошибку капчи
        self.mock_register_externals(captcha_raised=True)
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_error_response(response, ['captcha.required'])
        self.env.statbox.assert_has_written([])

        # попробуем пойти еще раз, не угадав капчи
        self.mock_register_externals(captcha_raised=False)
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_error_response(response, ['captcha.required'])
        self.env.statbox.assert_has_written([])

        # а теперь все же угадаем
        with self.track_transaction() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True
        self.mock_register_externals(captcha_raised=False)
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_auth_response(response, check_subscription=True, check_frodo=True, registered=True)
        self.assert_records_register_and_reset(with_service=True, captcha_passed=1)

    def test_register_after_blocked_callback(self):
        """
        В callback попадаем на заблокированный аккаунт, потом идем на регистрацию.
        """
        response = self.make_api_request('start', data=self.start_args)
        self.assert_start_response(response)
        self.assert_records__start_and_reset()

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(2, account_enabled=False)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_error_response(response, ['account.disabled'])
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=0,
            with_service=False,
        )

        self.mock_register_externals()
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_auth_response(response, registered=True)
        self.assert_records_register_and_reset(with_service=False)

    def test_register_after_blocked_choose(self):
        """
        В choose попадаем на заблокированный аккаунт, потом идем на регистрацию.
        """
        response = self.make_api_request('start', data=self.start_args)
        self.assert_start_response(response)
        self.assert_records__start_and_reset()

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(0)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_register_response(response)
        self.assert_records_callback_and_reset('register', with_service=False)

        # выбираем первый аккаунт из списка
        uid = self.mock_choose_externals(0, account_enabled=False)
        data = {'track_id': self.track_id, 'uid': uid}
        response = self.make_api_request('choose', data=data)
        self.assert_error_response(response, ['account.disabled'])
        self.env.statbox.assert_has_written([])

        # все же пойдем на регистрацию
        self.mock_register_externals()
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_auth_response(response, registered=True)
        self.assert_records_register_and_reset(with_service=False)

    def test_register_with_existing_accounts(self):
        """
        Из /callback получаем направление в /choose, но идем в /register.
        """
        response = self.make_api_request('start', data=self.start_args)
        self.assert_start_response(response)
        self.assert_records__start_and_reset()

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(3)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_choose_response(response)
        self.assert_records_callback_and_reset(
            'choose',
            uids=[TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID],
            enabled_count=2,
            with_service=False,
        )

        self.mock_register_externals(account_has_profiles=True)
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_error_response(response, ['account.already_registered'])
        self.env.statbox.assert_has_written([])

    def test_native_start_auth(self):
        self.mock_native_start_externals(2)
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_auth_response(response, is_xtoken_response=True)
        self.assert_records_native_start_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            cookie_set=False,
        )

        # попробуем сходить еще раз в какую-нибудь ручку
        self.mock_callback_externals(
            profiles_count=2,
            # На повторный вызов данные соц. таски уже будут в треке, поэтому
            # Паспорт не пойдёт за ними в Социализм.
            with_social_api_get_task_data_request=False,
        )

        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)

        self.assert_auth_response(response, is_xtoken_response=True)
        self.assert_records_callback_and_reset(
            'auth',
            auth=True,
            cookie_set=False,
            enabled_count=1,
            uids=[TEST_SOCIAL_UID],
            uids_count='1',
            with_service=False,
        )

    def test_native_start_with_origin(self):
        self.mock_native_start_externals(2)
        response = self.make_api_request('native_start', data=dict(self.native_start_args, origin=TEST_ORIGIN))
        self.assert_auth_response(response, is_xtoken_response=True)
        self.assert_records_native_start_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            origin=TEST_ORIGIN,
            cookie_set=False,
        )

    def test_native_start_auth_with_device_info(self):
        self.mock_native_start_externals(2)
        response = self.make_api_request('native_start', data=self.native_start_args_with_device_info)
        self.assert_auth_response(response, is_xtoken_response=True)
        self.assert_records_native_start_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            cookie_set=False,
        )
        self.env.oauth.requests[0].assert_query_contains(TEST_DEVICE_INFO)

    def test_native_start_auth_2fa_account__error(self):
        """Если у пользователя включена 2ФА, то нужно потребовать одноразовый пароль перед авторизацией"""
        self.mock_native_start_externals(2, bb_kwargs={'attributes': {'account.2fa_on': '1'}})

        response = self.make_api_request('native_start', data=self.native_start_args)

        self.assert_error_response(response, ['account.2fa_enabled'], is_native=True)

    def test_native_start_auth_strong_password_policy__error(self):
        """При включенной политике сложного пароля пользователю нужно отказать в авторизации"""
        self.mock_native_start_externals(2, bb_kwargs={'subscribed_to': [67]})
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_error_response(response, ['account.strong_password_policy_enabled'], is_native=True)

    def test_native_start_auth_nonstandard_scheme(self):
        self.mock_native_start_externals(2)

        response = self.make_api_request(
            'native_start',
            data=dict(self.native_start_args, retpath=TEST_RETPATH_NONSTANDARD_SCHEME),
        )

        self.assert_auth_response(response, is_xtoken_response=True, nonstandard_scheme=True)
        self.assert_records_native_start_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            nonstandard_scheme=True,
            cookie_set=False,
        )

    def test_native_choose_auth(self):
        self.mock_native_start_externals(3)
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_choose_response(response, is_xtoken_response=True)
        self.assert_records_native_start_and_reset(
            'choose',
            uids=[TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID],
            enabled_count=2,
        )

    def test_native_social_broker_permanent_error(self):
        self.mock_native_start_externals(3)
        self.env.social_broker.set_social_broker_response_value(
            '<html>Hi! I\'m HTML!</html>',
        )
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_error_response(response, ['backend.social_broker_permanent_error'], is_native=True)

    def test_native_blackbox_permanent_error(self):
        self.mock_native_start_externals(3)
        self.env.blackbox.set_blackbox_response_value('userinfo', 'not json')
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_error_response(response, ['backend.blackbox_permanent_error'], is_native=True)

    def test_native_blackbox_temporary_error(self):
        self.mock_native_start_externals(3)
        self.env.blackbox.set_blackbox_response_side_effect('userinfo', BlackboxTemporaryError)
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_error_response(response, ['backend.blackbox_failed'], is_native=True)

    def test_native_social_broker_temporary_error(self):
        self.mock_native_start_externals(3)
        self.env.social_broker.set_social_broker_response_side_effect(
            SocialBrokerTemporaryError,
        )
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_error_response(response, ['backend.social_broker_failed'], is_native=True)

    def test_native_start_oauth_error(self):
        self.mock_native_start_externals(2, oauth_error='invalid_grant', oauth_error_description='account disabled')
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_error_response(response, ['exception.unhandled'], is_native=True)

    def test_native_start_oauth_account_type_forbidden(self):
        self.mock_native_start_externals(
            2,
            oauth_error='invalid_grant',
            oauth_error_description=OAUTH_FORBIDDEN_ACCOUNT_TYPE_ERROR_DESCRIPTION,
        )
        response = self.make_api_request('native_start', data=self.native_start_args)
        self.assert_error_response(response, ['auth.not_allowed'], is_native=True)

    def test_callback_auth_with_authorization_code(self):
        response = self.make_api_request('start', data=self.start_args_with_code_challenge)
        self.assert_start_response(response)

        # Тут должен быть поход в брокер. Возвращаемся:
        self.mock_callback_externals(2)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_auth_response(response, is_auth_code_response=True)

    def test_callback_auth_with_authorization_code_oauth_error(self):
        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_error_response(error='backend.failed'),
        )
        response = self.make_api_request('start', data=self.start_args_with_code_challenge)
        self.assert_start_response(response)

        # Тут должен быть поход в брокер. Возвращаемся:
        self.mock_callback_externals(2)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_error_response(response, ['backend.oauth_failed'])

    def test_choose_auth_with_authorization_code(self):
        response = self.make_api_request('start', data=self.start_args_with_code_challenge)
        self.assert_start_response(response)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(3)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_choose_response(response, is_auth_code_response=True)

        # выбираем первый аккаунт из списка
        uid = self.mock_choose_externals(0)
        data = {'track_id': self.track_id, 'uid': uid}
        response = self.make_api_request('choose', data=data)
        self.assert_auth_response(response, is_auth_code_response=True)

    def test_register_auth_with_authorization_code(self):
        response = self.make_api_request('start', data=self.start_args_with_code_challenge)
        self.assert_start_response(response)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(0)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_register_response(response, is_auth_code_response=True)

        # пойдем на регистрацию
        self.mock_register_externals()
        data = {'eula_accepted': True, 'track_id': self.track_id}
        response = self.make_api_request('register', data=data)
        self.assert_auth_response(
            response,
            registered=True,
            is_auth_code_response=True,
        )

    def test_account_global_logout_after_track_created_error(self):
        """
        Хотим выписать куку, но аккаунт был глобально разлогинен
        уже после того, как завели трек для создания кук.
        """
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся:
        self.mock_callback_externals(2)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_SOCIAL_UID,
                attributes={'account.global_logout_datetime': str(int(time.time()) + 1)},
            ),
        )
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_error_response(response, ['account.global_logout'])

    def test_callback_auth_force_complete_lite(self):
        """
        Лайта с паролем отправляем на дорегистрацию
        """
        response = self.make_api_request('start', data=self.start_args)
        self.assert_start_response(response)
        self.assert_records__start_and_reset()

        self.mock_callback_externals(1, bb_kwargs={
            'login': TEST_LITE_LOGIN,
            'aliases': {
                'lite': TEST_LITE_LOGIN,
            },
        })
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_force_complete_lite_response(response, has_recovery_method=True)
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            uids_count='1',
            with_service=False,
        )

    def test_callback_auth_force_complete_lite_with_recovery_method(self):
        """
        Лайта с паролем и средством восстановления с почетом отправляем на дорегистрацию
        """
        response = self.make_api_request('start', data=self.start_args)
        self.assert_start_response(response)
        self.assert_records__start_and_reset()

        self.mock_callback_externals(
            1,
            bb_kwargs=merge_dicts(
                {
                    'login': TEST_LITE_LOGIN,
                    'aliases': {
                        'lite': TEST_LITE_LOGIN,
                    },
                },
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
            ),
        )
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_force_complete_lite_response(response, has_recovery_method=True)
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            uids_count='1',
            with_service=False,
        )

    def test_native_start_auth_force_complete_lite_with_recovery_method(self):
        track_id_generator = FakeTrackIdGenerator().start()
        track_id_generator.set_return_value(self.track_id)
        try:
            self.mock_native_start_externals(
                1,
                bb_kwargs=merge_dicts(
                    {
                        'login': TEST_LITE_LOGIN,
                        'aliases': {
                            'lite': TEST_LITE_LOGIN,
                        },
                    },
                    build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                ),
            )
            response = self.make_api_request('native_start', data=self.native_start_args)
            self.assert_force_complete_lite_response(response, has_recovery_method=True, is_native=True)
            self.assert_records_native_start_and_reset(
                'auth',
                uids=[TEST_SOCIAL_UID],
                enabled_count=1,
            )
        finally:
            track_id_generator.stop()

    def test_choose_auth_force_complete_lite(self):
        """Лайта с паролем отправляем на дорегистрацию"""
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(3)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_choose_response(response)
        self.assert_records_callback_and_reset(
            'choose',
            uids=[TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID],
            enabled_count=2,
            with_service=False,
        )

        # выбираем первый аккаунт из списка
        uid = self.mock_choose_externals(
            0,
            bb_kwargs={
                'login': TEST_LITE_LOGIN,
                'aliases': {
                    'lite': TEST_LITE_LOGIN,
                },
            },
        )
        data = {'track_id': self.track_id, 'uid': uid}
        response = self.make_api_request('choose', data=data)

        self.assert_force_complete_lite_response(response, has_recovery_method=True)
        self.env.statbox.assert_has_written([])

    def test_callback_auth_with_password_is_changing_required__social_account(self):
        """
        https://st.yandex-team.ru/PASSP-8733
        Если для соц аккаунта вдруг ЧЯ вернул признак необходимости смены пароля
        (password.is_changing_required в терминах моделей passport-api),
        то мы не должны отправлять его на смену пароля или еще как-то на это реагировать.
        """

        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        self.mock_callback_externals(2, bb_kwargs={'password_changing_required': True})
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_auth_response(response, check_subscription=True)
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            uids_count='1',
        )

    def test_callback_auth_with_password_is_changing_required__full_account(self):
        """
        https://st.yandex-team.ru/PASSP-9628
        Если для аккаунта с паролем вдруг ЧЯ вернул признак необходимости смены пароля
        (password.is_changing_required в терминах моделей passport-api),
        то мы должны отправлять его на смену пароля.
        """

        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        self.mock_callback_externals(
            2,
            bb_kwargs={'crypt_password': '1:pass', 'password_changing_required': True},
        )
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)

        self.assert_error_response(response, ['account.required_change_password'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin', track_id=self.track_id),
            self.env.statbox.entry(
                'callback_end',
                accounts=str(TEST_SOCIAL_UID),
                enabled_accounts_count='1',
                disabled_accounts_count='0',
                state='auth',
                track_id=self.track_id,
            ),
            self.env.statbox.entry(
                'defined_validation_method',
                track_id=self.track_id,
            ),
        ])

    def test_choose_auth_with_password_is_changing_required__full_account(self):
        """
        Никаких ошибок, авторизуемся в /choose
        """
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(3)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_choose_response(response)
        self.assert_records_callback_and_reset(
            'choose',
            uids=[TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID],
            enabled_count=2,
            with_service=False,
        )

        # выбираем первый аккаунт из списка
        uid = self.mock_choose_externals(
            0,
            password_changing_required=True,
            bb_kwargs={'crypt_password': '1:pass'},
        )
        data = {'track_id': self.track_id, 'uid': uid}
        response = self.make_api_request('choose', data=data)

        self.assert_error_response(response, ['account.required_change_password'])

    def test_native_start_auth_with_password_is_changing_required__full_account(self):
        self.mock_native_start_externals(
            2,
            bb_kwargs={'crypt_password': '1:pass', 'password_changing_required': True},
        )
        response = self.make_api_request('native_start', data=self.native_start_args)

        self.assert_error_response(response, ['account.required_change_password'], is_native=True)

    def test_cant_auth_phonish(self):
        """
        Проверим, что фониши не появляются в списке доступных для соц авторизации аккаунтов.
        """
        response = self.make_api_request('start', data=self.start_args)
        self.assert_start_response(response)
        self.assert_records__start_and_reset()

        self.mock_callback_externals(2, bb_kwargs={'aliases': {'mailish': 'phne-login'}, 'login': 'phne-login'})
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_register_response(response)

    def test_cant_auth_mailish(self):
        """
        Проверим, что мейлиши не появляются в списке доступных для соц авторизации аккаунтов.
        """
        response = self.make_api_request('start', data=self.start_args)
        self.assert_start_response(response)
        self.assert_records__start_and_reset()

        self.mock_callback_externals(2, bb_kwargs={'aliases': {'mailish': 'abc@example.com'}, 'login': 'abc@example.com'})
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_register_response(response)


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestMultiAuthSocialIntegrationalScenariosBase(TestSocialIntegrationalBase):

    def setUp(self):
        super(TestMultiAuthSocialIntegrationalScenariosBase, self).setUp()
        self.start_args = {
            'retpath': TEST_RETPATH,
            'place': 'query',
            'provider': TEST_PROVIDER['code'],
            'application': TEST_APPLICATION,
            'broker_consumer': TEST_BROKER_CONSUMER,
        }
        self.start_args_with_service = dict(self.start_args, service=TEST_SERVICE)
        self.uid = TEST_SOCIAL_UID
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid=TEST_AUTH_ID),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_USER_IP,
            ),
        )

    def assert_sessionid_called(self, call_index=1):
        sessionid_url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        check_url_contains_params(
            sessionid_url,
            {
                'method': 'sessionid',
                'multisession': 'yes',
                'sessionid': TEST_SESSIONID,
            },
        )

    def assert_createsession_called(self, call_index=0):
        url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        check_url_contains_params(
            url,
            {
                'uid': str(self.uid),
                'is_lite': '0',
                'method': 'createsession',
                'social_id': '123456789',
                'have_password': '0',
                'keyspace': 'yandex.ru',
                'userip': TEST_USER_IP,
                'format': 'json',
                'ttl': '5',
                'host_id': '7f',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport-test.yandex.ru,www.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def assert_editsession_called(self, call_index=3):
        edit_session_url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        check_url_contains_params(
            edit_session_url,
            {
                'uid': str(self.uid),
                'new_default': str(self.uid),
                'format': 'json',
                'sessionid': TEST_SESSIONID,
                'host': TEST_HOST,
                'userip': TEST_USER_IP,
                'method': 'editsession',
                'op': 'add',
                'social_id': '123456789',
                'keyspace': 'yandex.ru',
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru,www.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def build_auth_log_entry(self, status, uid):
        return [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', TEST_USER_AGENT),
            ('ip_from', TEST_USER_IP),
        ]

    def assert_auth_log_ok(self, expected_records):
        """Произошел один вызов логгера авторизации - обновление сессии пользователя"""
        eq_(self.env.auth_handle_mock.call_count, len(expected_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_records,
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YABS_URL='localhost',
)
class TestMultiAuthSocialCallbackScenarios(TestMultiAuthSocialIntegrationalScenariosBase):

    def _make_request(self, cookie=None):
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся:
        self.mock_callback_externals(2)
        data = {
            'task_id': TEST_TASK_ID,
            'status': 'ok',
            'track_id': self.track_id,
        }
        return self.make_api_request('callback', data=data, cookie=cookie)

    def test_ok_without_cookie(self):

        response = self._make_request()
        self.assert_auth_response(response, check_subscription=True)

        self.assert_createsession_called(call_index=1)
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            uids_count='1',
        )
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )

    def test_ok_with_invalid_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )
        self.assert_auth_response(response, check_subscription=True)

        self.assert_sessionid_called()
        self.assert_createsession_called(call_index=2)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_records_callback_and_reset(
            'auth',
            uids=[TEST_SOCIAL_UID],
            enabled_count=1,
            auth=True,
            uids_count='1',
            with_check_cookies=True,
        )

    def test_ok_with_cookie_with_other_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                ttl=5,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )

        self.assert_auth_response(response, check_subscription=True, check_createsession=False)

        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_OTHER_UID),
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_records_callback_and_reset(
            'auth',
            uids=[self.uid],
            enabled_count=1,
            auth=True,
            uids_count='2',
            session_method='edit',
            old_session_uids=TEST_OTHER_UID,
            with_check_cookies=True,
        )

    def test_ok_with_cookie_with_same_valid_and_other_invalid_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=self.uid,
                    login=TEST_LOGIN,
                    ttl=5,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )

        self.assert_auth_response(response, check_subscription=True, check_createsession=False)

        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_update', self.uid),
            ],
        )
        self.assert_records_callback_and_reset(
            'auth',
            uids=[self.uid],
            enabled_count=1,
            auth=True,
            uids_count='2',
            session_method='edit',
            old_session_uids='%s,1234' % self.uid,
            with_check_cookies=True,
        )

    def test_error_session_logged_out(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
            ),
        )

        self.env.blackbox.set_blackbox_response_side_effect(
            'editsession',
            blackbox.BlackboxInvalidParamsError(blackbox.BLACKBOX_ERROR_SESSION_LOGGED_OUT),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=yandexuid' % TEST_SESSIONID,
        )

        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2)
        self.assert_error_response(response, ['sessionid.expired'])


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YABS_URL='localhost',
    ALLOWED_SOCIAL_RETPATH_SCHEMES=['yandexmail'],
)
class TestMultiAuthSocialChooseScenarios(TestMultiAuthSocialIntegrationalScenariosBase):

    def _make_request(self, cookie=None):
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(3)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data, cookie=cookie)
        self.assert_choose_response(response)
        self.assert_records_callback_and_reset(
            'choose',
            uids=[TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID],
            enabled_count=2,
            with_service=False,
        )
        # выбираем первый аккаунт из списка
        uid = self.mock_choose_externals(0)
        data = {'track_id': self.track_id, 'uid': uid}
        return self.make_api_request('choose', data=data, cookie=cookie)

    def test_ok_without_cookie(self):

        response = self._make_request()
        self.assert_auth_response(response, check_subscription=True)

        self.assert_createsession_called(call_index=2)
        self.assert_records_choose_and_reset(
            with_service=True,
            uid=TEST_SOCIAL_UID,
            login=TEST_USER_LOGIN,
        )
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )

    def test_ok_with_invalid_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )
        self.assert_auth_response(response, check_subscription=True)

        self.assert_sessionid_called(call_index=2)
        self.assert_createsession_called(call_index=3)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_records_choose_and_reset(
            with_service=True,
            uid=TEST_SOCIAL_UID,
            login=TEST_USER_LOGIN,
            with_multibrowser=False,
            with_check_cookies=True,
        )

    def test_ok_with_cookie_with_other_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                ttl=5,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )

        self.assert_auth_response(response, check_subscription=True, check_createsession=False)

        self.assert_sessionid_called(call_index=2)
        self.assert_editsession_called(call_index=3)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_OTHER_UID),
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_records_choose_and_reset(
            with_service=True,
            uid=TEST_SOCIAL_UID,
            login=TEST_USER_LOGIN,
            uids_count='2',
            session_method='edit',
            with_multibrowser=False,
            old_session_uids=TEST_OTHER_UID,
            with_check_cookies=True,
        )

    def test_error_cookie_overflow(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                allow_more_users=False,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=yandexuid' % TEST_SESSIONID,
        )
        self.assert_error_response(response, ['sessionid.overflow'])

    def test_ok_with_cookie_with_same_valid_and_other_invalid_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=self.uid,
                    login=TEST_LOGIN,
                    ttl=5,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )

        self.assert_auth_response(response, check_subscription=True, check_createsession=False)

        self.assert_sessionid_called(call_index=2)
        self.assert_editsession_called(call_index=3)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_update', self.uid),
            ],
        )
        self.assert_records_choose_and_reset(
            with_service=True,
            uid=self.uid,
            login=TEST_USER_LOGIN,
            uids_count='2',
            session_method='edit',
            with_multibrowser=False,
            old_session_uids='%s,1234' % self.uid,
            with_check_cookies=True,
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YABS_URL='localhost',
    ALLOWED_SOCIAL_RETPATH_SCHEMES=['yandexmail'],
)
class TestMultiAuthSocialRegisterScenarios(TestMultiAuthSocialIntegrationalScenariosBase):

    def _make_request(self, cookie=None):
        response = self.make_api_request('start', data=self.start_args_with_service)
        self.assert_start_response(response)
        self.assert_records__start_and_reset(with_service=True)

        # Тут должен быть поход в брокер. Возвращаемся из него:
        self.mock_callback_externals(0)
        data = {'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id}
        response = self.make_api_request('callback', data=data)
        self.assert_register_response(response)
        self.assert_records_callback_and_reset('register', with_service=False)

        # все же пойдем на регистрацию
        self.mock_register_externals()
        data = {'eula_accepted': True, 'track_id': self.track_id}
        return self.make_api_request('register', data=data, cookie=cookie)

    def test_ok_without_cookie(self):
        response = self._make_request()
        self.assert_auth_response(response, check_subscription=True, registered=True)

        self.assert_createsession_called(call_index=2)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_records_register_and_reset(with_service=True)

    def test_ok_with_invalid_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )
        self.assert_auth_response(response, check_subscription=True, registered=True)

        self.assert_sessionid_called(call_index=1)
        self.assert_createsession_called(call_index=2)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_records_register_and_reset(with_service=True, with_multibrowser=False, with_check_cookies=True)

    def test_ok_with_cookie_with_other_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
            ),
        )

        response = self._make_request(
            cookie='Session_id=%s;yandexuid=%s' % (TEST_SESSIONID, TEST_YANDEXUID_COOKIE),
        )

        self.assert_auth_response(
            response,
            check_subscription=True,
            check_createsession=False,
            registered=True,
            with_lah_cookie=False,
        )
        self.assert_sessionid_called(call_index=1)
        self.assert_editsession_called(call_index=2)
        self.assert_auth_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_OTHER_UID),
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_records_register_and_reset(
            with_service=True,
            uids_count='2',
            session_method='edit',
            with_multibrowser=False,
            old_session_uids=TEST_OTHER_UID,
            ttl=0,
            with_check_cookies=True,
        )
