# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.common.authorization import (
    AUTHORIZATION_SESSION_POLICY_PERMANENT,
    AUTHORIZATION_SESSION_POLICY_SESSIONAL,
)
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    ProfileTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    COOKIE_YP_VALUE,
    COOKIE_YS_VALUE,
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE_TEMPLATE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    MDA2_BEACON_VALUE,
    SESSION,
    TEST_ALLOWED_PDD_HOSTS,
    TEST_AUTH_ID,
    TEST_COOKIE_AGE,
    TEST_COOKIE_MY,
    TEST_COOKIE_TIMESTAMP,
    TEST_DOMAIN,
    TEST_ENTERED_LITE_LOGIN,
    TEST_ENTERED_LOGIN,
    TEST_FEATURES_DESCRIPTION,
    TEST_FRETPATH,
    TEST_GALATASARAY_ALIAS,
    TEST_HOST,
    TEST_INVALID_PASSWORD,
    TEST_IP,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_MODEL_CONFIGS,
    TEST_OLD_AUTH_ID,
    TEST_ORIGIN,
    TEST_PASSWORD,
    TEST_PHONE_ID,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMP,
    TEST_PROFILE_BAD_ESTIMATE,
    TEST_PROFILE_GOOD_ESTIMATE,
    TEST_PROFILE_MODEL,
    TEST_PROFILE_USER_LOGIN,
    TEST_RAW_ENV_FOR_PROFILE,
    TEST_REFERER,
    TEST_RETPATH,
    TEST_RETPATH_HOST,
    TEST_THRESHOLD,
    TEST_TOTP_CHECK_TIME,
    TEST_UFO_TIMEUUID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_USER_LANGUAGE,
    TEST_WEAK_PASSWORD,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.views.bundle.mixins.challenge import DecisionSource
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
)
from passport.backend.core.builders.messenger_api import MessengerApiTemporaryError
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.builders.tensornet.exceptions import TensorNetTemporaryError
from passport.backend.core.builders.tensornet.faker.tensornet import tensornet_eval_response
from passport.backend.core.builders.tensornet.tensornet import build_eval_protobuf
from passport.backend.core.builders.ufo_api import UfoApiTemporaryError
from passport.backend.core.builders.ufo_api.faker import (
    ufo_api_profile_item,
    ufo_api_profile_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.counters.profile_fails import get_counter
from passport.backend.core.dbmanager.manager import DBError
from passport.backend.core.env_profile.metric import EnvDistance
from passport.backend.core.historydb.entry import AuthEntry
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_url_contains_params,
    iterdiff,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.login.login import normalize_login
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import Weekday
from six.moves.urllib.parse import (
    parse_qs,
    urlparse,
)


eq_ = iterdiff(eq_)


DEFAULT_TEST_SETTINGS = dict(
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    ALLOWED_PDD_HOSTS=TEST_ALLOWED_PDD_HOSTS,
    DISABLE_FAILED_CAPTCHA_LOGGING=False,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    TENSORNET_API_URL='http://tensornet:80/',
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    FORCED_CHALLENGE_CHANCE=0.0,
    FORCED_CHALLENGE_PERIOD_LENGTH=3600,
    YDB_PERCENTAGE=50,
    TRY_USE_YDB=False,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,   # Не включаем флаг, потому что эту ручку будем вырезать
    ALLOW_PROFILE_CHECK_FOR_WEB=True,       # Флаг выключаем, чтобы работала старая логика
    EMAIL_CODE_CHALLENGE_ENABLED=False,
)


class BaseSubmitAuthViewTestCase(BaseBundleTestViews, EmailTestMixin, ProfileTestMixin):
    """
    Набор общих функций
    """

    def get_headers(self, host=None, user_ip=None, cookie=None):
        return mock_headers(
            host=host or TEST_HOST,
            user_agent=TEST_USER_AGENT,
            cookie=cookie or 'Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            user_ip=user_ip or TEST_IP,
            referer=TEST_REFERER,
        )

    def get_base_query_params(self):
        return {
            'login': TEST_ENTERED_LOGIN,
            'password': TEST_PASSWORD,

            'retpath': TEST_RETPATH,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
        }

    def query_params(self, exclude=None, **kwargs):
        base_params = self.get_base_query_params()
        if exclude:
            for key in exclude:
                if key in base_params:
                    del base_params[key]
        return merge_dicts(base_params, kwargs)

    def make_request(self, data, headers):
        return self.env.client.post(
            self.default_url,
            data=data,
            headers=headers,
        )

    def request_track(self):
        return dict(
            user_entered_login=TEST_ENTERED_LOGIN,
            retpath=TEST_RETPATH,
            origin=TEST_ORIGIN,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
            fretpath=TEST_FRETPATH,
            clean='yes',
        )

    def base_track(self):
        """Поля в треке и их нормальные значения"""
        request_data = self.request_track()
        account_data = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            language=TEST_USER_LANGUAGE,
            # Всякое специфичное
            is_strong_password_policy_required=False,
        )
        return merge_dicts(request_data, account_data)

    def base_auth_log_entries(self):
        return {
            'login': TEST_ENTERED_LOGIN,
            'type': authtypes.AUTH_TYPE_WEB,
            'status': 'ses_create',
            'uid': str(TEST_UID),
            'useragent': TEST_USER_AGENT,
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'comment': AuthEntry.format_comment_dict({
                'aid': TEST_AUTH_ID,
                'ttl': 5,
            }),
            'retpath': TEST_RETPATH,
            'ip_from': TEST_IP,
            'client_name': 'passport',
        }

    def build_auth_log_entries(self, **kwargs):
        entries = self.base_auth_log_entries()
        entries.update(kwargs)
        return entries.items()

    def assert_track_ok(self, exclude=None, **kwargs):
        """Трек заполнен полностью и корректно"""
        params = self.base_track()
        params.update(kwargs)
        for field in exclude or []:
            del params[field]
        track = self.track_manager.read(self.track_id)
        d1 = {attr_name: getattr(track, attr_name) for attr_name in params}
        d2 = {attr_name: str(value) if type(value) == int else value for attr_name, value in params.items()}
        iterdiff(eq_)(d1, d2)

    def assert_track_empty(self):
        """Трек пуст в случае какой-либо ошибки"""
        track = self.track_manager.read(self.track_id)
        for attr_name in self.base_track().keys():
            self.assertIsNone(getattr(track, attr_name))

    def assert_request_data_saved_in_track(self):
        """В трек пишется только информация о запросе в случае ошибки"""
        track = self.track_manager.read(self.track_id)
        for attr_name, expected_value in self.request_track().items():
            actual_value = getattr(track, attr_name)
            eq_(actual_value, expected_value, [attr_name, actual_value, expected_value])

    def assert_failed_auth_recorded_to_statbox(
        self, bruteforce,
        login_status, password_status,
        uid=None, with_check_cookies=True, **kwargs
    ):
        submitted_entry = self.env.statbox.entry('submitted')
        failed_auth_entry = self.env.statbox.entry(
            'failed_auth',
            login_status=login_status,
            password_status=password_status,
            origin=TEST_ORIGIN,
            **kwargs
        )
        if bruteforce:
            failed_auth_entry['bruteforce'] = bruteforce
        if uid is not None:
            failed_auth_entry['uid'] = str(uid)

        entries = [
            submitted_entry,
            failed_auth_entry
        ]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def assert_failed_captcha_recorded_to_statbox(self):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('captcha_failed'),
        ])

    def assert_successful_auth_recorded_to_statbox(self, ttl=5, captcha_passed=False,
                                                   bruteforce=None, exclude=None, auth_args=None,
                                                   profile_kwargs=None, submitted_kwargs=None, skip_profile_check=False,
                                                   ydb=True, ufo_profile_items=None,
                                                   ufo_profile_compared_args=None, with_check_cookies=True,
                                                   **kwargs):
        submitted_entry = self.env.statbox.entry(
            'submitted',
            _exclude=exclude,
            **merge_dicts(submitted_kwargs or {}, kwargs)
        )
        ufo_checked_entry = self.env.statbox.entry(
            'ufo_profile_checked',
            _exclude=exclude,
            **kwargs
        )
        ufo_profile_compared = self.env.statbox.entry(
            'ufo_profile_compared',
            _exclude=exclude,
            **kwargs
        )

        check_cookies_entry = self.env.statbox.entry('check_cookies')

        auth_entry = self.env.statbox.entry(
            'cookie_set',
            _exclude=exclude,
            captcha_passed=tskv_bool(captcha_passed),
            ttl=str(ttl),
            person_country='ru',
            ip_country='us',
            authid=TEST_AUTH_ID,
            uid=str(TEST_UID),
            input_login=TEST_ENTERED_LOGIN,
            session_method='create',
            uids_count='1',
            **kwargs
        )

        if profile_kwargs:
            ufo_checked_entry.update(profile_kwargs)
        if auth_args:
            auth_entry.update(auth_args)
        if bruteforce:
            auth_entry.update(bruteforce=bruteforce)
        if ufo_profile_compared_args:
            ufo_profile_compared.update(ufo_profile_compared_args)
        if ydb and with_check_cookies:
            expected_entries = [
                submitted_entry,
                ufo_profile_compared,
                ufo_checked_entry,
                check_cookies_entry,
                auth_entry,
            ]
        elif ydb:
            expected_entries = [
                submitted_entry,
                ufo_profile_compared,
                ufo_checked_entry,
                auth_entry,
            ]
        else:
            expected_entries = [
                submitted_entry,
                ufo_checked_entry,
                check_cookies_entry,
                auth_entry,
            ]
        if skip_profile_check and with_check_cookies:
            expected_entries = [
                submitted_entry,
                check_cookies_entry,
                auth_entry,
            ]
        elif skip_profile_check:
            expected_entries = [
                submitted_entry,
                auth_entry,
            ]

        self.env.statbox.assert_has_written(expected_entries)
        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ["auth_password.rps"],
            {"auth_password.rps.total_dmmm": 1}
        )

    def assert_threshold_exceeded_recorded_to_statbox(
            self,
            is_password_change_required=False,
            decision_source=DecisionSource.UFO,
            captcha_reason=None,
            is_email_sent=True,
            ufo_check=False,
            input_login=TEST_ENTERED_LOGIN,
            tensornet_estimate=TEST_PROFILE_GOOD_ESTIMATE,
            is_model_passed='1',
            was_online_sec_ago_key_exist=False,
            messenger_api_error=False,
    ):
        expected_entries = [
            self.env.statbox.entry(
                'submitted',
                input_login=input_login,
            ),
        ]

        if ufo_check:
            expected_entries.append(
                self.env.statbox.entry(
                    'ufo_profile_compared',
                    input_login=input_login,
                    is_mobile='0',
                ),
            )
            expected_entries.append(
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    input_login=input_login,
                    tensornet_estimate=str(tensornet_estimate),
                    captcha_reason=captcha_reason,
                    decision_source=decision_source,
                    is_challenge_required='1',
                    is_model_passed=is_model_passed,
                    is_mobile='0',
                ),
            )
        if messenger_api_error:
            expected_entries.append(
                self.env.statbox.entry(
                    'messenger_api_error',
                     input_login=input_login,
                ),
            )

        expected_entries.append(
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required=tskv_bool(is_password_change_required),
                decision_source=decision_source,
                email_sent=str(int(is_email_sent)),
                input_login=input_login,
                is_mobile='0',
                **({'was_online_sec_ago': TimeSpan(0)} if was_online_sec_ago_key_exist else {})
            ),
        )

        self.env.statbox.assert_has_written(expected_entries)

    def assert_validation_method_recorded_to_statbox(self, uid=TEST_UID, validation_method='captcha_and_phone'):
        self.env.statbox.assert_equals(
            self.env.statbox.entry(
                'defined_validation_method',
                uid=str(uid),
                validation_method=validation_method,
            ),
            offset=-1,
        )

    def get_expected_cookies(self, with_lah=True, yandex_login=TEST_LOGIN):
        specific = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE_TEMPLATE % yandex_login,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]

        cookies = [
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
        ]
        if with_lah:
            cookies.append(EXPECTED_LAH_COOKIE)
        return sorted(specific + cookies)

    def _get_expected_response(self, status='ok', cookies=None, retpath=TEST_RETPATH, uid=TEST_UID,
                               domain=None, login=TEST_LOGIN, accounts=None, display_login=None,
                               **kwargs):

        expected = {
            'status': status,
            'track_id': self.track_id,
            'account': {
                'uid': uid,
                'login': login,
                # Этот хардкод отсылает нас к `passport.test.blackbox.py:_blackbox_userinfo`
                'display_name': {'name': '', 'default_avatar': ''},
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'birthday': '1963-05-15',
                    'gender': 1,
                    'language': 'ru',
                    'country': 'ru',
                },
                'display_login': login if display_login is None else display_login,
            },
            'retpath': retpath,
        }
        if cookies:
            expected.update(
                cookies=cookies,
                default_uid=uid,
            )
        if domain:
            expected['account']['domain'] = domain
        if accounts:
            expected['accounts'] = accounts
        expected.update(kwargs)
        return expected

    def get_account_info(self, login=TEST_LOGIN, uid=TEST_UID, display_name=None, display_login=None):
        info = {
            'uid': uid,
            'login': login,
            'display_name': {'name': '', 'default_avatar': ''},
            'display_login': login if display_login is None else display_login,
        }
        if display_name:
            info['display_name'] = display_name
        return info

    def get_expected_response(self, *args, **kwargs):
        return self._get_expected_response(*args, **kwargs)

    def assert_response_ok(self, response, **kwargs):
        eq_(response.status_code, 200, [response.status_code, response.data])
        expected_response = self.get_expected_response(**kwargs)
        actual_response = json.loads(response.data)
        if 'cookies' in actual_response:
            actual_response['cookies'] = sorted(actual_response['cookies'])
        eq_(actual_response, expected_response)

    def not_authorized(self):
        """Логгер авторизации не вызывался - пользователю не создавалась новая сессия"""
        eq_(self.env.auth_handle_mock.call_count, 0)

    def has_new_session(self, **kwargs):
        """Произошел один вызов логгера авторизации - создание новой сессии"""
        eq_(self.env.auth_handle_mock.call_count, 1)
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    **kwargs
                ),
            ],
        )

    def has_updated_session(self):
        """Произошел один вызов логгера авторизации - обновление сессии пользователя"""
        eq_(self.env.auth_handle_mock.call_count, 1)
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_update',
                    login=TEST_LOGIN,
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

    def setup_env(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.default_url = '/1/bundle/auth/password/submit/?consumer=dev'

    def setup_trackid_generator(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.append(self.track_id_generator)

    def setup_cookie_mocks(self):
        self.build_cookies_yx = mock.Mock(return_value=[EXPECTED_YP_COOKIE, EXPECTED_YS_COOKIE])
        self.build_cookie_l = mock.Mock(return_value=EXPECTED_L_COOKIE)
        self.build_cookie_lah = mock.Mock(return_value=EXPECTED_LAH_COOKIE)

        self.patches.extend([
            mock.patch(
                'passport.backend.api.common.authorization.build_cookies_yx',
                self.build_cookies_yx,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                self.build_cookie_l,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_lah',
                self.build_cookie_lah,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ])

    def setup_messenger_api_responses(self):
        self.env.messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_UID))

    def setup_blackbox_responses(self, env):
        self.setup_login_response()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

        createsession_response = blackbox_createsession_response(
            authid=TEST_AUTH_ID,
            ip=TEST_IP,
            time=TEST_COOKIE_TIMESTAMP,
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            createsession_response,
        )
        self.env.blackbox.set_response_side_effect('sign', [blackbox_sign_response()])

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def setup_login_response(self, uid=TEST_UID, login=TEST_LOGIN,
                             crypt_password='1:pwd', emails=None,
                             attributes=None, dbfields=None, phone=None):
        """
        Формируем болванку ответа от ЧЯ на запрос входа в систему.
        """
        account_info = {
            'uid': uid,
            'login': login,
            'crypt_password': crypt_password,
            'emails': emails if emails is not None else [
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        }

        if dbfields:
            account_info['dbfields'] = dbfields

        if attributes:
            account_info['attributes'] = attributes

        if phone:
            account_info = deep_merge(account_info, phone)

        login_response = blackbox_login_response(**account_info)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

    def assert_blackbox_createsesion_call(self):
        for call in self.env.blackbox._mock.request.call_args_list:
            url = call[0][1]
            qs = parse_qs(urlparse(url).query)
            if qs.get('method') != ['createsession']:
                continue
            expected = {
                'have_password': ['1'],
                'password_check_time': [TimeNow()],
            }

            self.assertDictContainsSubset(expected, qs)
            return

        raise AssertionError('Blackbox createsession method was not called')

    def assert_blackbox_editsession_call(self):
        for call in self.env.blackbox._mock.request.call_args_list:
            url = call[0][1]
            qs = parse_qs(urlparse(url).query)
            if qs.get('method') != ['editsession']:
                continue
            expected = {
                'have_password': ['1'],
                'password_check_time': [TimeNow()],
            }

            self.assertDictContainsSubset(expected, qs)
            return

        raise AssertionError('Blackbox editsession method was not called')

    def assert_blackbox_sign_sessguard_called(self):
        request = self.env.blackbox.get_requests_by_method('sign')[1]
        sessguard_cookie = 'sessguard=1.sessguard; Domain=.%s; Secure; HttpOnly; Path=/' % TEST_RETPATH_HOST
        request.assert_query_equals(
            {
                'format': 'json',
                'method': 'sign',
                'sign_space': 'sessguard_container',
                'ttl': '60',
                'value': json.dumps({
                    'cookies': [sessguard_cookie],
                    'retpath': TEST_RETPATH,
                }),
            },
        )

    def start_patches(self):
        """Запускаем mocks"""
        for patch in self.patches:
            patch.start()

    def stop_patches(self):
        """
        Здесь мы останавливаем все зарегистрированные ранее mocks
        """
        for patch in reversed(self.patches):
            patch.stop()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            input_login=TEST_ENTERED_LOGIN,
            yandexuid=TEST_YANDEXUID_COOKIE,
            origin=TEST_ORIGIN,
            track_id=self.track_id,
            mode='any_auth',
        )

        self.env.statbox.bind_entry(
            'failed_auth',
            _inherit_from='local_base',
            _exclude=('origin',),
            action='failed_auth',
        )
        self.env.statbox.bind_entry(
            'captcha_failed',
            _inherit_from='local_base',
            _exclude=('origin',),
            action='captcha_failed',
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _inherit_from='local_base',
            action='ufo_profile_checked',
            current=self.make_user_profile(raw_env=TEST_RAW_ENV_FOR_PROFILE).as_json,
            ufo_status='1',
            ufo_distance='100',
            tensornet_status='1',
            tensornet_model='-'.join(TEST_PROFILE_MODEL),
            tensornet_estimate=str(TEST_PROFILE_GOOD_ESTIMATE),
            is_fresh_profile_passed='0',
            is_model_passed='1',
            is_fresh_account='0',
            is_challenge_required='0',
            is_mobile='0',
            decision_source=DecisionSource.UFO,
            uid=str(TEST_UID),
            kind='ufo',
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _inherit_from='local_base',
            action='cookie_set',
            cookie_version=str(settings.BLACKBOX_SESSION_VERSION),
            ttl=None,
            person_country='ru',
            ip_country='us',
            captcha_passed=None,
            uid=str(TEST_UID),
            session_method='create',
            uids_count='1',
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
            referer=TEST_REFERER,
            retpath=TEST_RETPATH,
            type='password',
        )
        self.env.statbox.bind_entry(
            'loaded_secure_number',
            _inherit_from='local_base',
            action='loaded_secure_number',
            uid=str(TEST_UID),
            error=None,
        )
        self.env.statbox.bind_entry(
            'defined_validation_method',
            _inherit_from='base',
            validation_method='captcha',
            track_id=self.track_id,
            uid=str(TEST_UID),
            mode='change_password_force',
            action='defined_validation_method',
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            _inherit_from='local_base',
            uid=str(TEST_UID),
            action='profile_threshold_exceeded',
            is_password_change_required='0',
            is_mobile='0',
            email_sent='1',
            kind='ufo',
        )
        self.env.statbox.bind_entry(
            'ufo_profile_compared',
            _inherit_from='local_base',
            action='ufo_profile_compared',
            uid=str(TEST_UID),
            is_mobile='0',
            ydb_profile_items='[]',
            ufo_profile_items='[]',
        )
        self.env.statbox.bind_entry(
            'auth_notification',
            _inherit_from='local_base',
            action='auth_notification',
            counter_exceeded='0',
            email_sent='1',
            is_challenged='1',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'messenger_api_error',
            _inherit_from='local_base',
            status='error',
            error='messenger_api.request_failed',
            uid=str(TEST_UID),
        )

    def setUp(self):
        self.patches = []
        # Мокаем сборку некоторых кук - ДО старта ViewTestEnvironment
        # Иначе придется переписывать пути для применения патчей, поскольку модули уже проимпортируются
        self.setup_cookie_mocks()

        self.start_patches()

        self.setup_env()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.default_headers = self.get_headers()

        self.setup_trackid_generator()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()

        self.setup_blackbox_responses(self.env)
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()

        self.setup_messenger_api_responses()

    def tearDown(self):
        self.teardown_profile_patches()
        self.env.stop()
        self.stop_patches()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches
        for attr in 'build_cookies_yx', 'build_cookie_l', 'build_cookie_lah':
            if hasattr(self, attr):
                delattr(self, attr)

    def assert_blackbox_login_called(self, excluded=None, **login_data):
        excluded = excluded or set()
        expected_data = merge_dicts({'method': 'login'}, login_data)
        self.env.blackbox.requests[0].assert_post_data_contains(expected_data)
        ok_(not set(excluded).intersection(set(self.env.blackbox.requests[0].post_args.keys())))


@with_settings_hosts(
    **dict(DEFAULT_TEST_SETTINGS, FORCED_CHALLENGE_CHANCE=0.0, FORCED_CHALLENGE_PERIOD_LENGTH=3600)
)
class NoForcedChallengeTestCase(BaseSubmitAuthViewTestCase):
    def test_no_forced_challenge(self):
        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_track_ok(
            is_captcha_required=False,
        )
        self.assert_response_ok(
            resp,
            accounts=[
                {
                    'login': TEST_LOGIN,
                    'display_name': {
                        'default_avatar': '',
                        'name': '',
                    },
                    'uid': TEST_UID,
                    'display_login': TEST_LOGIN,
                },
            ],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )


@with_settings_hosts(
    **dict(DEFAULT_TEST_SETTINGS, FORCED_CHALLENGE_CHANCE=0.0, FORCED_CHALLENGE_PERIOD_LENGTH=3600)
)
class ForcedChallengeForTestLoginTestCase(BaseSubmitAuthViewTestCase):
    def get_base_query_params(self):
        return {
            'login': 'yndx.force-challenge.' + TEST_ENTERED_LOGIN,
            'password': TEST_PASSWORD,
            'retpath': TEST_RETPATH,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
        }

    def request_track(self):
        return dict(
            user_entered_login='yndx.force-challenge.' + TEST_ENTERED_LOGIN,
            retpath=TEST_RETPATH,
            origin=TEST_ORIGIN,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
            fretpath=TEST_FRETPATH,
            clean='yes',
        )

    def base_track(self):
        """Поля в треке и их нормальные значения"""
        request_data = self.request_track()
        account_data = dict(
            uid=TEST_UID,
            login='yndx-force-challenge-' + TEST_LOGIN,
            language=TEST_USER_LANGUAGE,
            # Всякое специфичное
            is_strong_password_policy_required=False,
        )
        return merge_dicts(request_data, account_data)

    def test_forced_challenge_for_test_login(self):
        self.setup_login_response(login='yndx.force-challenge.' + TEST_LOGIN, emails=[])

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = False
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_track_ok(
            is_captcha_required=True,
            is_captcha_recognized=False,
        )
        self.assert_error_response_with_track_id(
            resp,
            ['captcha.required'],
        )
        self.assert_threshold_exceeded_recorded_to_statbox(
            captcha_reason=DecisionSource.RANDOM,
            decision_source=DecisionSource.RANDOM,
            ufo_check=True,
            is_email_sent=False,
            input_login='yndx.force-challenge.' + TEST_ENTERED_LOGIN,
            was_online_sec_ago_key_exist=True,
        )

    def test_challenge_for_test_login_is_ok_if_messenger_api_unavailable(self):
        """Время последнего пребывания онлайн не логируется если не доступен messenger_api, но это не ломает вход"""
        self.setup_login_response(login='yndx.force-challenge.' + TEST_LOGIN, emails=[])
        self.env.messenger_api.set_response_side_effect(
            'check_user_lastseen',
            MessengerApiTemporaryError,
        )

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_track_ok(
            is_captcha_required=True,
            is_captcha_recognized=False,
        )
        self.assert_error_response_with_track_id(
            resp,
            ['captcha.required'],
        )
        self.assert_threshold_exceeded_recorded_to_statbox(
            captcha_reason=DecisionSource.RANDOM,
            decision_source=DecisionSource.RANDOM,
            ufo_check=True,
            is_email_sent=False,
            input_login='yndx.force-challenge.' + TEST_ENTERED_LOGIN,
            was_online_sec_ago_key_exist=False,
            messenger_api_error=True,
        )

    def test_forced_challenge_for_test_login_if_distance_above_threshold(self):
        # Если сработала ufo и требуется показать пользователю челлендж,
        # а логин - тестовый, всё равно надо показать каптчу
        self.setup_login_response(login='yndx.force-challenge.' + TEST_LOGIN, emails=[])
        self.setup_profile_responses(ufo_items=[], estimate=TEST_THRESHOLD + 0.1)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = False
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_track_ok(
            is_captcha_required=True,
            is_captcha_recognized=False,
        )
        self.assert_error_response_with_track_id(
            resp,
            ['captcha.required'],
        )
        self.assert_threshold_exceeded_recorded_to_statbox(
            captcha_reason=DecisionSource.RANDOM,
            decision_source=DecisionSource.RANDOM,
            ufo_check=True,
            is_email_sent=False,
            input_login='yndx.force-challenge.' + TEST_ENTERED_LOGIN,
            tensornet_estimate=str(TEST_THRESHOLD + 0.1),
            is_model_passed='0',
            was_online_sec_ago_key_exist=True,
        )

    def test_forced_challenge_for_test_login_can_pass_captcha_with_new_challenge_available(self):
        # Если у пользователя есть новый челлендж и он уже прошёл каптчу, то не надо показывать её вновь
        test_login = 'yndx.force-challenge.' + TEST_LOGIN
        self.setup_login_response(
            login=test_login,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),  # новый челлендж
            ],
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            # каптча разгадана
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_response_ok(
            resp,
            account=self.get_expected_response(login=normalize_login(test_login), display_login=test_login)['account'],
            accounts=[
                {
                    'login': normalize_login(test_login),
                    'display_name': {
                        'default_avatar': '',
                        'name': '',
                    },
                    'uid': TEST_UID,
                    'display_login': test_login,
                },
            ],
            cookies=self.get_expected_cookies(yandex_login=test_login),
            default_uid=TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_forced_challenge_for_test_login_can_pass_captcha(self):
        # Если пользователь уже прошёл каптчу, то не надо показывать её вновь
        test_login = 'yndx.force-challenge.' + TEST_LOGIN
        self.setup_login_response(login=test_login, emails=[])

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            # каптча разгадана
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_response_ok(
            resp,
            account=self.get_expected_response(login=normalize_login(test_login), display_login=test_login)['account'],
            accounts=[
                {
                    'login': normalize_login(test_login),
                    'display_name': {
                        'default_avatar': '',
                        'name': '',
                    },
                    'uid': TEST_UID,
                    'display_login': test_login,
                },
            ],
            cookies=self.get_expected_cookies(yandex_login=test_login),
            default_uid=TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )


@with_settings_hosts(
    **dict(DEFAULT_TEST_SETTINGS, FORCED_CHALLENGE_CHANCE=1.0)
)
class ForcedChallengeTestCase(BaseSubmitAuthViewTestCase):
    def test_forced_challenge_submit(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = False
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_track_ok(
            is_captcha_required=True,
            is_captcha_recognized=False,
        )
        self.assert_error_response_with_track_id(
            resp,
            ['captcha.required'],
        )
        self.assert_threshold_exceeded_recorded_to_statbox(
            captcha_reason=DecisionSource.RANDOM,
            decision_source=DecisionSource.RANDOM,
            ufo_check=True,
            is_email_sent=False,
        )


@with_settings_hosts(
    **dict(DEFAULT_TEST_SETTINGS, FORCED_CHALLENGE_CHANCE=0.5)
)
class ForcedChallengeUidSplitTestCase(BaseSubmitAuthViewTestCase):
    pass


@with_settings_hosts(
    **dict(DEFAULT_TEST_SETTINGS, YDB_PERCENTAGE=0)
)
class ProfileTestWithNoYdbTestCase(BaseSubmitAuthViewTestCase, ProfileTestMixin):
    def test_env_all_facts_logged_on_successful_login(self):
        """
        Проверяем, что без YDB нет записи
        """

        # Проставляем факт показа challenge
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = True

        self.setup_login_response()
        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=True)
        self.assert_successful_auth_recorded_to_statbox(
            ydb=False,
            auth_args={
                'is_auth_challenge_shown': '1',
                'old_session_uids': '1',
                'retpath': TEST_RETPATH,
                'session_method': 'edit',
            },
        )


@with_settings_hosts(
    **dict(DEFAULT_TEST_SETTINGS, YDB_PERCENTAGE=0)
)
class ProfileTestWithNoYdbAndForceTestCase(BaseSubmitAuthViewTestCase, ProfileTestMixin):
    def get_base_query_params(self):
        return {
            'login': 'yndx.ydb-profile-test.' + TEST_ENTERED_LOGIN,
            'password': TEST_PASSWORD,
            'retpath': TEST_RETPATH,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
        }

    def request_track(self):
        return dict(
            user_entered_login='yndx.ydb-profile-test.' + TEST_ENTERED_LOGIN,
            retpath=TEST_RETPATH,
            origin=TEST_ORIGIN,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
            fretpath=TEST_FRETPATH,
            clean='yes',
        )

    def base_track(self):
        """Поля в треке и их нормальные значения"""
        request_data = self.request_track()
        account_data = dict(
            uid=TEST_UID,
            login='yndx.ydb-profile-test.' + TEST_LOGIN,
            language=TEST_USER_LANGUAGE,
            # Всякое специфичное
            is_strong_password_policy_required=False,
        )
        return merge_dicts(request_data, account_data)

    def test_env_all_facts_logged_on_successful_login(self):
        """
        Проверяем, что без YDB есть запись для тестовых логинов
        """
        self.setup_login_response(login='yndx.ydb-profile-test.' + TEST_LOGIN, emails=[])
        self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_successful_auth_recorded_to_statbox(
            ydb=True,
            auth_args={
                'input_login': 'yndx.ydb-profile-test.' + TEST_ENTERED_LOGIN,
                'old_session_uids': '1',
                'retpath': TEST_RETPATH,
                'session_method': 'edit',
            },
            ufo_profile_compared_args={
                'input_login': 'yndx.ydb-profile-test.' + TEST_ENTERED_LOGIN,
            },
            submitted_kwargs={
                'input_login': 'yndx.ydb-profile-test.' + TEST_ENTERED_LOGIN,
            },
            profile_kwargs={
                'input_login': 'yndx.ydb-profile-test.' + TEST_ENTERED_LOGIN,
                'kind': 'ydb',
            },
            exclude=['ufo_profile_items'],
        )


@with_settings_hosts(
    PROFILE_TRIAL_PERIOD=14 * 24 * 3600,
    **DEFAULT_TEST_SETTINGS
)
class ProfileDistanceTestCase(BaseSubmitAuthViewTestCase, ProfileTestMixin):

    def setUp(self):
        super(ProfileDistanceTestCase, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

    def assert_ufo_profile_check_recorded_to_statbox(self, **kwargs):
        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox.entry(
                'ufo_profile_checked',
                **kwargs
            ),
            entry_index=2,
        )

    def assert_tensornet_called(self, is_mobile=True):
        eq_(len(self.env.tensornet.requests), 1)

        request = self.env.tensornet.requests[0]
        request.assert_properties_equal(
            url='http://tensornet:80/%s/%s/eval' % TEST_PROFILE_MODEL,
        )
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        # Этот protobuf используем только для проверки того, что данные передаются в API
        expected_protobufs = []
        # Если тест выполняется на границе смены часов, то возможно расхождение между запросом в api
        # и построением данного протобуфа для сравнения.
        for date in [now, hour_ago]:
            expected_protobuf = build_eval_protobuf(
                {
                    'hour': date.hour,
                    'ip_prob_1d': 0,
                    'ip_prob_1m': 0,
                    'ip_prob_1w': 0,
                    'is_mobile': int(is_mobile),
                    'is_weekend': int(date.isoweekday() in {Weekday.SATURDAY, Weekday.SUNDAY}),
                },
                TEST_FEATURES_DESCRIPTION,
            )
            expected_protobufs.append(expected_protobuf)
        assert request.post_args in expected_protobufs

    def get_expected_cookies(self, with_lah=True):
        specific = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]

        cookies = [
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
        ]
        if with_lah:
            cookies.append(EXPECTED_LAH_COOKIE)
        return sorted(specific + cookies)

    def test_no_profile_check_for_shared_account(self):
        self.setup_profile_responses(ufo_items=[], estimate=TEST_PROFILE_BAD_ESTIMATE)
        self.setup_login_response(
            attributes={
                'account.is_shared': True,
            },
        )

        # Выставляем поля в треке, чтобы не закоротило по другой причине
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = False
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_response_ok(
            resp,
            accounts=[
                {
                    'login': TEST_LOGIN,
                    'display_name': {
                        'default_avatar': '',
                        'name': '',
                    },
                    'uid': TEST_UID,
                    'display_login': TEST_LOGIN,
                },
            ],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

    def test_no_profile_check_for_forced_password_change(self):
        """На принуд. смене не делаем проверку профиля"""
        self.setup_profile_responses(ufo_items=[], estimate=TEST_PROFILE_BAD_ESTIMATE)
        self.setup_login_response(
            dbfields={'subscription.login_rule.8': 4},  # ТБВС
            attributes={
                'password.forced_changing_reason': '1',
            },
            phone=build_phone_secured(
                phone_id=TEST_PHONE_ID,
                phone_number=TEST_PHONE_NUMBER.e164,
            ),
        )

        # Выставляем поля в треке, чтобы не закоротило по другой причине
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = False
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )

        expected_response = self.get_expected_response(
            state='change_password',
            change_password_reason='account_hacked',
            validation_method='captcha_and_phone',
            number=TEST_PHONE_NUMBER_DUMP,
        )
        expected_response['account'].update(
            is_yandexoid=False,
            is_2fa_enabled=False,
            is_rfc_2fa_enabled=False,
            is_workspace_user=False,
        )
        expected_response.pop('retpath')
        self.assert_ok_response(
            resp,
            **expected_response
        )
        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_captcha_required=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            can_use_secure_number_for_password_validation=True,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            has_secure_phone_number=True,
        )
        self.assert_validation_method_recorded_to_statbox()

    def test_env_all_facts_logged_on_successful_login(self):
        """
        Проверяем, что факт запроса "challenge-response" остается в логах
        после успешной авторизации.
        """

        # Проставляем факт показа challenge
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = True

        self.setup_login_response()
        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=True)
        self.assert_successful_auth_recorded_to_statbox(
            auth_args={
                'is_auth_challenge_shown': '1',
                'old_session_uids': '1',
                'retpath': TEST_RETPATH,
                'session_method': 'edit',
            },
        )

    def test_env_profile_recently_registered_ok(self):
        """
        Проверяем, что даже при несовпадении профилей не показываем
        капчу для недавно зарегистрированного аккаунта.
        """
        self.setup_profile_responses(ufo_items=[], estimate=TEST_PROFILE_BAD_ESTIMATE)
        reg_time = datetime.now() - timedelta(seconds=settings.PROFILE_TRIAL_PERIOD - 5)
        self.setup_login_response(
            dbfields={
                'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)

    def test_env_profile_no_captcha_after_captcha(self):
        """
        Проверяем, что если пользователю уже показывалась капча, то
        мы ничего не делаем.
        """
        self.setup_login_response(emails=[])
        self.setup_profile_responses(ufo_items=[], estimate=TEST_PROFILE_BAD_ESTIMATE)

        # Проверка расстояния пропускается, если проставлены
        # флаги is_captcha_recognized и is_captcha_checked.
        # Они могут быть выставлены как нами, так и кем-то
        # запросившим показ капчи до нас.
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = True
            track.is_captcha_recognized = True
            track.is_captcha_checked = True

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok()
        self.assert_successful_auth_recorded_to_statbox(
            auth_args={
                'is_auth_challenge_shown': '1',
                'captcha_passed': '1',
                'old_session_uids': '1',
                'retpath': TEST_RETPATH,
                'session_method': 'edit',
            },
            skip_profile_check=True,
        )

    def test_profile_ufo_api_failed(self):
        """
        UfoApi вернуло ошибку.
        """
        reg_time = datetime.now() - timedelta(seconds=settings.PROFILE_TRIAL_PERIOD - 5)
        self.setup_login_response(
            dbfields={
                'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )
        self.env.ufo_api.set_response_side_effect(
            'profile',
            UfoApiTemporaryError,
        )

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        # Здесь два вызова, несмотря на то, что ретрай один:
        # - первый вызов для проверки профиля
        # - второй для обновления профиля
        self.assert_ufo_api_called(call_count=2)
        self.assert_ufo_profile_check_recorded_to_statbox(
            ufo_distance=str(EnvDistance.Max),
            ufo_status='0',
            decision_source=DecisionSource.UFO_FAILED,
            is_challenge_required='1',
            is_fresh_account='1',
        )

    def test_profile_fresh_below_threshold(self):
        """
        Профиль с минимальным возможным расстоянием до fresh-данных не вызывает
        показ капчи.
        """
        self.setup_login_response()
        ufo_fresh_item = ufo_api_profile_item(
            timeuuid=str(TEST_UFO_TIMEUUID),
            data=TEST_RAW_ENV_FOR_PROFILE,
        )
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_fresh_item],
                ),
            ),
        )

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        self.assert_ufo_api_called()
        self.assert_ufo_profile_check_recorded_to_statbox(
            ufo_closest=self.make_existing_fresh_profile(ufo_fresh_item).as_json,
            ufo_distance=str(EnvDistance.Min),
            is_fresh_profile_passed='1',
        )

    def test_profile_user_passed_ok(self):
        """
        Пользователь прошел проверку модели профиля.
        """
        self.setup_login_response()
        ufo_fresh_item = ufo_api_profile_item(
            timeuuid=str(TEST_UFO_TIMEUUID),
            data=TEST_RAW_ENV_FOR_PROFILE,
        )
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_fresh_item],
                ),
            ),
        )
        self.env.tensornet.set_tensornet_response_value(tensornet_eval_response(0.3))

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        self.assert_ufo_api_called()
        self.assert_ufo_profile_check_recorded_to_statbox(
            tensornet_estimate='0.3',
            tensornet_status='1',
            tensornet_model='-'.join(TEST_PROFILE_MODEL),
            ufo_closest=self.make_existing_fresh_profile(ufo_fresh_item).as_json,
            ufo_distance=str(EnvDistance.Low),
            is_fresh_profile_passed='1',
        )
        self.assert_tensornet_called()

    def test_profile_tensornet_api_failed_ok(self):
        """
        API TensorNet ответило ошибкой.
        """
        self.setup_login_response()
        ufo_fresh_item = ufo_api_profile_item(
            timeuuid=str(TEST_UFO_TIMEUUID),
            data=TEST_RAW_ENV_FOR_PROFILE,
        )
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_fresh_item],
                ),
            ),
        )
        self.env.tensornet.set_tensornet_response_side_effect(TensorNetTemporaryError)

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        self.assert_ufo_api_called()
        self.assert_ufo_profile_check_recorded_to_statbox(
            tensornet_status='0',
            tensornet_model='-'.join(TEST_PROFILE_MODEL),
            ufo_closest=self.make_existing_fresh_profile(ufo_fresh_item).as_json,
            ufo_distance=str(EnvDistance.Min),
            is_fresh_profile_passed='1',
            is_model_passed='0',
            _exclude=['tensornet_estimate'],
        )
        self.assert_tensornet_called()

    def test_profile_fresh_check_passed_model_fails_ok(self):
        """
        Челлендж не показан из-за близкого fresh-профиля. Поход в модель неуспешен, но это не
        влияет на результат.
        """
        self.setup_login_response()
        ufo_fresh_item = ufo_api_profile_item(
            timeuuid=str(TEST_UFO_TIMEUUID),
            data=TEST_RAW_ENV_FOR_PROFILE,
        )
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_fresh_item],
                ),
            ),
        )
        self.env.tensornet.set_tensornet_response_side_effect(TensorNetTemporaryError)

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        self.assert_ufo_api_called()
        self.assert_ufo_profile_check_recorded_to_statbox(
            tensornet_status='0',
            tensornet_model='-'.join(TEST_PROFILE_MODEL),
            ufo_closest=self.make_existing_fresh_profile(ufo_fresh_item).as_json,
            ufo_distance=str(EnvDistance.Min),
            is_fresh_profile_passed='1',
            is_model_passed='0',
            _exclude=['tensornet_estimate'],
        )
        self.assert_tensornet_called()

    def test_profile_ufo_api_fails_check_not_passed(self):
        """
        Произошла ошибка при походе в ufo, показываем челлендж вне зависимости от результата модели.
        """
        self.setup_login_response(emails=[])
        self.env.ufo_api.set_response_side_effect(
            'profile',
            UfoApiTemporaryError,
        )
        self.env.tensornet.set_tensornet_response_value(tensornet_eval_response(0.1))

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['captcha.required'], track_id=self.track_id)
        self.assert_track_ok(
            is_auth_challenge_shown=True,
            is_captcha_required=True,
        )
        self.assert_ufo_api_called()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('ufo_profile_compared', _exclude=['ufo_profile_items']),
            self.env.statbox.entry(
                'ufo_profile_checked',
                tensornet_status='1',
                tensornet_estimate='0.1',
                tensornet_model='-'.join(TEST_PROFILE_MODEL),
                ufo_distance=str(EnvDistance.Max),
                ufo_status='0',
                decision_source=DecisionSource.UFO_FAILED,
                is_challenge_required='1',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.UFO_FAILED,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_tensornet_called()

    def test_profile_ufo_api_fails_with_counter_overflow_challenge_disabled(self):
        """
        Произошла ошибка при походе в ufo, не показываем челлендж из-за переполнения счетчика сбоев.
        """
        self.setup_login_response(emails=[])
        self.env.ufo_api.set_response_side_effect(
            'profile',
            UfoApiTemporaryError,
        )
        self.env.tensornet.set_tensornet_response_value(tensornet_eval_response(0.1))
        counter = get_counter()
        for _ in range(counter.limit - 1):
            counter.incr()

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        self.assert_ufo_api_called(call_count=2)
        self.assert_ufo_profile_check_recorded_to_statbox(
            tensornet_status='1',
            tensornet_estimate='0.1',
            tensornet_model='-'.join(TEST_PROFILE_MODEL),
            ufo_distance=str(EnvDistance.Max),
            ufo_status='0',
            decision_source=DecisionSource.UFO_FAILED,
        )
        self.assert_tensornet_called()

    def test_profile_model_check_passed_ok(self):
        """
        Челлендж не показан из-за того, что оценка модели меньше порога.
        """
        self.setup_login_response()
        self.setup_profile_responses(ufo_items=[], estimate=TEST_THRESHOLD - 0.1)

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        self.assert_ufo_api_called()
        self.assert_ufo_profile_check_recorded_to_statbox(
            tensornet_status='1',
            tensornet_estimate=str(TEST_THRESHOLD - 0.1),
            tensornet_model='-'.join(TEST_PROFILE_MODEL),
            ufo_distance=str(EnvDistance.Max),
        )
        self.assert_tensornet_called()

    def test_profile_model_check_passed_for_test_login(self):
        """
        Оценка модели меньше порога, но пользователь тестовый - всегда показываем челлендж.
        """
        self.setup_login_response(login=TEST_PROFILE_USER_LOGIN, emails=[])
        self.setup_profile_responses(ufo_items=[], estimate=TEST_THRESHOLD - 0.1)

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['captcha.required'], track_id=self.track_id)
        self.assert_track_ok(
            is_auth_challenge_shown=True,
            is_captcha_required=True,
            login=TEST_PROFILE_USER_LOGIN,
        )
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('ufo_profile_compared'),
            self.env.statbox.entry(
                'ufo_profile_checked',
                tensornet_status='1',
                tensornet_estimate=str(TEST_THRESHOLD - 0.1),
                tensornet_model='-'.join(TEST_PROFILE_MODEL),
                ufo_distance=str(EnvDistance.Max),
                decision_source=DecisionSource.TEST_LOGIN,
                is_challenge_required='1',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.TEST_LOGIN,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_tensornet_called()

    def test_profile_model_check_not_passed(self):
        """
        Челлендж показан из-за того, что оценка модели больше порога.
        """
        self.setup_login_response(emails=[])
        self.setup_profile_responses(ufo_items=[], estimate=TEST_THRESHOLD + 0.1)

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['captcha.required'], track_id=self.track_id)
        self.assert_track_ok(
            is_auth_challenge_shown=True,
            is_captcha_required=True,
        )
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('ufo_profile_compared'),
            self.env.statbox.entry(
                'ufo_profile_checked',
                tensornet_status='1',
                tensornet_estimate=str(TEST_THRESHOLD + 0.1),
                tensornet_model='-'.join(TEST_PROFILE_MODEL),
                ufo_distance=str(EnvDistance.Max),
                is_challenge_required='1',
                is_model_passed='0',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.UFO,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_tensornet_called()

    def test_profile_model_check_failed_challenge_required(self):
        """
        Поход в модель неуспешен, показываем челлендж.
        """
        self.setup_login_response(emails=[])
        self.setup_profile_responses(ufo_items=[])
        self.env.tensornet.set_tensornet_response_side_effect(TensorNetTemporaryError)

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['captcha.required'], track_id=self.track_id)
        self.assert_track_ok(
            is_auth_challenge_shown=True,
            is_captcha_required=True,
        )
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('ufo_profile_compared'),
            self.env.statbox.entry(
                'ufo_profile_checked',
                tensornet_status='0',
                tensornet_model='-'.join(TEST_PROFILE_MODEL),
                ufo_distance=str(EnvDistance.Max),
                decision_source=DecisionSource.UFO_FAILED,
                is_challenge_required='1',
                is_model_passed='0',
                _exclude=['tensornet_estimate'],
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.UFO_FAILED,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_tensornet_called()

    def test_profile_model_check_failed_with_counter_overflow_challenge_disabled(self):
        """
        Поход в модель неуспешен, не показываем челлендж из-за переполнения счетчика сбоев.
        """
        self.setup_login_response(emails=[])
        self.setup_profile_responses(ufo_items=[])
        self.env.tensornet.set_tensornet_response_side_effect(TensorNetTemporaryError)
        counter = get_counter()
        for _ in range(counter.limit - 1):
            counter.incr()

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        self.assert_ufo_api_called()
        self.assert_ufo_profile_check_recorded_to_statbox(
            tensornet_status='0',
            tensornet_model='-'.join(TEST_PROFILE_MODEL),
            ufo_distance=str(EnvDistance.Max),
            is_model_passed='0',
            decision_source=DecisionSource.UFO_FAILED,
            _exclude=['tensornet_estimate'],
        )
        self.assert_tensornet_called()

    def test_profile_no_challenge_for_2fa(self):
        """
        Проверяем, что профиль с 2FA никогда не вызывает показ челленджа.
        """
        self.setup_profile_responses(ufo_items=[], estimate=TEST_PROFILE_BAD_ESTIMATE)
        self.setup_login_response(
            attributes={
                'account.2fa_on': '1',
            },
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)

    def test_profile_disabled(self):
        """Профиль выключен в настройках"""
        self.setup_login_response()
        with settings_context(
            BLACKBOX_URL='localhost',
            AUTH_PROFILE_ENABLED=False,
            FORCED_CHALLENGE_CHANCE=0.0,
            FORCED_CHALLENGE_PERIOD_LENGTH=3600,
            PASSPORT_SUBDOMAIN='passport-test',
            ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request(
                self.query_params(),
                self.get_headers(),
            )
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_auth_challenge_shown=None)
        eq_(len(self.env.ufo_api.requests), 0)
        eq_(self.env.auth_challenge_handle_mock.call_count, 0)


@with_settings_hosts(
    LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=1,
    **DEFAULT_TEST_SETTINGS
)
class SubmitAuthTestCase(BaseSubmitAuthViewTestCase):
    """
    Проверим как работает вьюха инициализации авторизации
    """

    @parameterized.expand([
        (True,),
        (False,),
    ])
    def test_auth__by_passwd__ok(self, with_origin):
        # Все проходит без ошибок по пути с именем пользователя и паролем и валидной сессионной кукой
        # Пользователю сообщают "все ОК" и устанавливают свежие куки: сессионные, контейнеры

        exclude_origin = ('origin',) if not with_origin else None

        resp = self.make_request(self.query_params(exclude=exclude_origin), self.default_headers)

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        self.assert_track_ok(
            exclude=exclude_origin,
            old_session_create_timestamp=TEST_COOKIE_TIMESTAMP,
            old_session_ip=TEST_IP,
            old_session_age=TEST_COOKIE_AGE,
        )

        track = self.track_manager.read(self.track_id)

        eq_(
            track.submit_response_cache,
            self.get_expected_response(accounts=[self.get_account_info()], default_uid=TEST_UID),
        )
        ok_('cookies' not in track.submit_response_cache)
        eq_(track.auth_method, 'password')

        assert len(self.env.blackbox.requests) == 3
        # method=login
        login_data = {
            'authtype': authtypes.AUTH_TYPE_WEB,
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'from': 'passport',
            'xretpath': TEST_RETPATH,
            'userip': TEST_IP,
            'login': TEST_ENTERED_LOGIN,
            'password': TEST_PASSWORD,
        }
        self.assert_blackbox_login_called(**login_data)

        # method=sessionid
        calls = self.env.blackbox.get_requests_by_method('sessionid')
        assert len(calls) == 1
        calls[0].assert_query_contains({
            'sessionid': '0:old-session',
        })

        # method=editsesession - т.к. была валидная сессионная кука
        assert len(self.env.blackbox.requests) == 3
        calls = self.env.blackbox.get_requests_by_method('editsession')
        assert len(calls) == 1
        calls[0].assert_query_contains({
            'method': 'editsession',
            'uid': str(TEST_UID),
            'lang': '1',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'format': 'json',
            'keyspace': 'yandex.ru',
            'userip': TEST_IP,
            'sessionid': '0:old-session',
            'new_default': str(TEST_UID),
            'host': 'passport-test.yandex.ru',
            'op': 'add',
            'create_time': TimeNow(),
            'guard_hosts': 'passport-test.yandex.ru,test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        })
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                old_session_uids='1',
                retpath=TEST_RETPATH,
                session_method='edit',
            ),
            exclude=exclude_origin,
        )
        self.has_updated_session()

        self.env.credentials_logger.assert_has_written([
            self.env.credentials_logger.entry(
                'auth',
                auth_id=TEST_AUTH_ID,
                login=TEST_ENTERED_LOGIN,
                ip=TEST_IP,
                track_id=self.track_id,
                uids_count='1',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                region_id='102630',
                is_new='0',
                surface='web_password',
            )
        ])

    def test_lite_auth_by_passwd__ok(self):
        """
        Лайт-пользователя отправляем на дорегистрацию
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                aliases={
                    'lite': TEST_LITE_LOGIN,
                },
                subscribed_to=[33],
                crypt_password='1:pwd',
            ),
        )
        expected_account = self.get_expected_response(
            **self.get_account_info(login=TEST_LITE_LOGIN)
        )['account']
        expected_account.update(
            is_2fa_enabled=False,
            is_rfc_2fa_enabled=False,
            is_yandexoid=False,
            is_workspace_user=False,
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        self.assert_ok_response(
            resp,
            state='force_complete_lite',
            account=expected_account,
            track_id=self.track_id,
            has_recovery_method=False,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.is_force_complete_lite, True)
        eq_(track.is_password_passed, True)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        eq_(self.env.blackbox._mock.request.call_count, 1)
        self.assert_blackbox_login_called()
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_lite_auth_by_passwd_with_phone__ok(self):
        """
        Лайт-пользователя отправляем на дорегистрацию
        """

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                **merge_dicts(
                    dict(
                        uid=TEST_UID,
                        login=TEST_LITE_LOGIN,
                        aliases={
                            'lite': TEST_LITE_LOGIN,
                        },
                        subscribed_to=[33],
                        crypt_password='1:pwd',
                    ),
                    build_phone_secured(
                        TEST_PHONE_ID,
                        TEST_PHONE_NUMBER.e164,
                    ),
                )
            ),
        )
        expected_account = self.get_expected_response(
            **self.get_account_info(login=TEST_LITE_LOGIN)
        )['account']
        expected_account.update(
            is_2fa_enabled=False,
            is_rfc_2fa_enabled=False,
            is_yandexoid=False,
            is_workspace_user=False,
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        self.assert_ok_response(
            resp,
            state='force_complete_lite',
            account=expected_account,
            track_id=self.track_id,
            has_recovery_method=True,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.is_force_complete_lite, True)
        eq_(track.is_password_passed, True)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        eq_(self.env.blackbox._mock.request.call_count, 1)
        self.assert_blackbox_login_called()
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_auth__short_session__ok(self):
        resp = self.make_request(
            self.query_params(policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL),
            self.get_headers(cookie='Session_id=;yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL,
        )

        # method=createsession
        assert len(self.env.blackbox.requests) == 2
        calls = self.env.blackbox.get_requests_by_method('createsession')
        assert len(calls) == 1
        calls[0].assert_query_contains({'ttl': '0'})
        # TODO: Специфицировать вызов auth_log
        eq_(self.env.auth_handle_mock.call_count, 1)
        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(
                retpath=TEST_RETPATH,
            ),
            with_check_cookies=False,
        )

    def test_phone_logged(self):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:pwd',
            **build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(
            self.query_params(policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
        )

        self.env.phone_logger.assert_has_written([
            self.env.phone_logger.get_log_entry(
                TEST_UID,
                TEST_PHONE_NUMBER.e164,
                TEST_YANDEXUID_COOKIE,
            ),
        ])

    def test_auth__without_optional_params_and_no_sessional_cookie__ok(self):
        resp = self.make_request(
            self.query_params(exclude=['origin', 'retpath', 'fretpath', 'clean']),
            self.get_headers(cookie='Session_id='),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            retpath=None,
        )
        self.assert_track_ok(origin=None, retpath=None, fretpath=None, clean=None)

        # method=login
        login_data = {
            'authtype': authtypes.AUTH_TYPE_WEB,
            'from': 'passport',
            'userip': TEST_IP,
            'login': TEST_ENTERED_LOGIN,
            'password': TEST_PASSWORD,
        }
        excluded = ['yandexuid', 'xretpath']
        self.assert_blackbox_login_called(excluded=excluded, **login_data)

        # method=createsession
        assert len(self.env.blackbox.requests) == 2
        calls = self.env.blackbox.get_requests_by_method('createsession')
        assert len(calls) == 1
        calls[0].assert_query_contains({'ttl': '5', 'is_lite': '0'})

        self.has_new_session(yandexuid='-', retpath='-')
        raw_env = dict(TEST_RAW_ENV_FOR_PROFILE, yandexuid=None)
        self.assert_successful_auth_recorded_to_statbox(
            exclude=['yandexuid', 'origin', 'retpath'],
            profile_kwargs=dict(
                current=self.make_user_profile(raw_env=raw_env).as_json,
            ),
            with_check_cookies=False,
        )

    def test_auth__with_empty_headers__ok(self):
        resp = self.make_request(
            self.query_params(),
            mock_headers(
                host=TEST_HOST,
                user_agent='',
                cookie='',
                user_ip=TEST_IP,
                referer='',
            ),
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok()

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['method'], 'login')
        ok_('useragent' not in login_data)
        ok_('referer' not in login_data)
        ok_('yandexuid' not in login_data)

        self.has_new_session(useragent='-', yandexuid='-')
        self.assert_successful_auth_recorded_to_statbox(
            exclude=['yandexuid'],
            user_agent='',
            submitted_kwargs=dict(referer=''),
            auth_args=dict(retpath=TEST_RETPATH),
            profile_kwargs=dict(
                current=self.make_user_profile(
                    raw_env=dict(TEST_RAW_ENV_FOR_PROFILE, user_agent_info={}, yandexuid=None),
                ).as_json,
            ),
            with_check_cookies=False,
        )

    def test_auth__by_passwd_without_retpath__use_retpath_from_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        resp = self.make_request(
            self.query_params(track_id=self.track_id, exclude=['retpath']),
            self.default_headers,
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            retpath=TEST_RETPATH,
        )
        self.assert_track_ok(retpath=TEST_RETPATH)
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='edit',
                old_session_uids='1',
                retpath=TEST_RETPATH,
            ),
        )

    def test_auth__without_user_cookies__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя и паролем и БЕЗ сессионной куки
        Пользователю сообщают "все ОК" и устанавливают свежие куки: сессионные, контейнеры
        """
        resp = self.make_request(self.query_params(), self.get_headers(cookie='Session_id='))
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.has_new_session(yandexuid='-')
        raw_env = dict(TEST_RAW_ENV_FOR_PROFILE, yandexuid=None)
        self.assert_successful_auth_recorded_to_statbox(
            exclude=['yandexuid'],
            auth_args=dict(retpath=TEST_RETPATH),
            profile_kwargs=dict(
                current=self.make_user_profile(raw_env=raw_env).as_json,
            ),
            with_check_cookies=False,
        )

    def test_auth__ok__set_special_cookie_fields(self):
        """
        Передаем флажки бетатестера и яндексоида в createsession
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                aliases={  # Яндексоид
                    'portal': TEST_LOGIN,
                    'yandexoid': 'yastaff_login',
                },
                dbfields={
                    'subscription.suid.668': '1',  # Бетатестер
                    'subscription.login.668': 'yastaff_login',
                },
            ),
        )
        resp = self.make_request(self.query_params(), self.get_headers(cookie='Session_id='))

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        assert len(self.env.blackbox.requests) == 2
        calls = self.env.blackbox.get_requests_by_method('createsession')
        assert len(calls) == 1
        calls[0].assert_query_contains({
            'is_yastaff': '1',
            'is_betatester': '1',
        })

    def test_auth__wrong_host__error(self):
        resp = self.make_request(
            self.query_params(),
            self.get_headers(host='google.com'),
        )

        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['host.invalid'],
            },
        )

    def test_auth_by_cookie__wrong_host__error(self):
        resp = self.make_request(
            self.query_params(exclude=['password', 'login']),
            self.get_headers(host='google.com'),
        )

        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['host.invalid'],
            },
        )

    def test_auth__with_login_and_without_password__error(self):
        resp = self.make_request(self.query_params(exclude=['password']), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['password.empty'],
            },
        )

    def test_auth__with_password_and_without_login__error(self):
        resp = self.make_request(self.query_params(exclude=['login']), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['login.empty'],
            },
        )

    def test_auth__by_cookie__ok(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой без пароля и логина
        Пользователю сообщают "все ОК" и никаких кук не устанавливают
        """
        # Запрос без логина и пароля в теле
        resp = self.make_request(self.query_params(exclude=['login', 'password']), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['retpath'], TEST_RETPATH)
        eq_(resp['fretpath'], TEST_FRETPATH)
        eq_(resp['clean'], 'yes')
        # Новая сессия не создается
        self.not_authorized()

        check_url_contains_params(self.env.blackbox._mock.request.call_args_list[0][0][1], {
            'host': TEST_HOST,
            'method': 'sessionid',
        })

    def test_auth__by_cookie_with_empty_login_and_password__ok(self):
        """Все проходит без ошибок по пути с валидной сессионной кукой с пустым логином и паролем
        Пользователю сообщают "все ОК" и никаких кук не устанавливают
        """
        # Запрос без логина и пароля в теле
        resp = self.make_request(self.query_params(login='', password=''), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['retpath'], TEST_RETPATH)
        eq_(resp['fretpath'], TEST_FRETPATH)
        eq_(resp['clean'], 'yes')
        self.not_authorized()

        check_url_contains_params(self.env.blackbox._mock.request.call_args_list[0][0][1], {
            'host': TEST_HOST,
            'method': 'sessionid',
        })

        track = self.track_manager.read(self.track_id)
        ok_(track.submit_response_cache is None)

    def test_auth__by_cookie_with_disabled_account__failed(self):
        """Если происходит авторизация по куке, и ЧЯ сообщил что аккаунт заблокирован, не проходить авторизацию"""
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            authid=TEST_OLD_AUTH_ID,
            status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        # Запрос без логина и пароля в теле
        resp = self.make_request(self.query_params(login='', password=''), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled'])

        self.not_authorized()

    def test_auth__invalid_password_with_valid_foreign_cookie__failed(self):
        """Пришли с валидной кукой, но авторизация плохому пользователю"""
        login_response = blackbox_login_response(
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        sessionid_response = blackbox_sessionid_multi_response(
            uid='42',
            login='smith',
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(
            self.query_params(password=TEST_INVALID_PASSWORD),
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['password.not_matched'])

        self.assert_request_data_saved_in_track()

    def test_auth__by_password_and_user_cookies_need_reset__ok(self):
        """При авторизации по паролю получено сообщение, что сессионную куку нужно продлить"""
        sessionid_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_NEED_RESET_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
            ttl=5,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        self.has_updated_session()
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                old_session_uids='1',
                retpath=TEST_RETPATH,
                session_method='edit',
            ),
        )

    def test_auth__by_cookies_and_cookies_need_reset__ok(self):
        """ЧЯ вернул статус NEED_RESET - все хорошо, считаем авторизованным"""
        sessionid_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_NEED_RESET_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(self.query_params(exclude=['login', 'password']), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['clean'], 'yes')
        eq_(resp['retpath'], TEST_RETPATH)
        eq_(resp['fretpath'], TEST_FRETPATH)
        self.not_authorized()

    def test_auth__already_passed__error(self):
        """В треке указано, что авторизация уже пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = SESSION['session']['value']

        resp = self.make_request(self.query_params(track_id=self.track_id), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.auth_passed'])

        self.assert_track_empty()
        self.not_authorized()

    def test_auth__by_cookie_with_invalid_retpath__retpath_not_in_response(self):
        """Если переданный параметр retpath не прошел валидацию - не бросаем ошибку - пропускаем его"""
        resp = self.make_request(
            self.query_params(exclude=['login', 'password'], retpath='invalid_retpath!@#$%'),
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        self.assertIsNone(resp['retpath'])
        eq_(resp['fretpath'], TEST_FRETPATH)
        eq_(resp['clean'], 'yes')
        self.not_authorized()

    def test_auth__by_cookie_empty_retpath__retpath_not_in_response(self):
        """Если переданный параметр retpath пустой - пропускаем его"""
        resp = self.make_request(
            self.query_params(exclude=['login', 'password'], retpath=''),
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        self.assertIsNone(resp['retpath'])
        eq_(resp['fretpath'], TEST_FRETPATH)
        eq_(resp['clean'], 'yes')
        self.not_authorized()

    def test_auth__captcha_is_required_in_track__error(self):
        """В треке записано что нужна капча, но она не была пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.user_entered_login = TEST_ENTERED_LOGIN
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = False
            track.bruteforce_status = 'captcha'

        resp = self.make_request(self.query_params(track_id=self.track_id), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['captcha.required'])

        self.not_authorized()
        self.assert_failed_captcha_recorded_to_statbox()

    def test_auth__invalid_session_cookie__error(self):
        """Пришла только сессионная кука, которая оказалась невалидной"""
        sessionid_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_EXPIRED_STATUS,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(self.query_params(exclude=['login', 'password']), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['sessionid.invalid'])

        self.assert_track_empty()

    def blackbox_login_error(self, error_code, uid=None, with_check_cookies=True, **kwargs):
        login_response = blackbox_login_response(**kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], [error_code])

        self.assert_request_data_saved_in_track()
        statbox_params = dict(
            bruteforce=None,
            login_status=kwargs.get('login_status', blackbox.BLACKBOX_LOGIN_VALID_STATUS),
            password_status=kwargs.get('password_status', blackbox.BLACKBOX_PASSWORD_VALID_STATUS),
        )
        if uid:
            statbox_params['uid'] = uid
        self.assert_failed_auth_recorded_to_statbox(with_check_cookies=with_check_cookies, **statbox_params)

    def test_auth__blackbox_bad_password__error(self):
        self.blackbox_login_error(
            'password.not_matched',
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            uid=TEST_UID,
            with_check_cookies=False,
        )

    def test_auth__blackbox_bad_password_for_account_not_found__error(self):
        """
        Пришли на авторизацию с аккаунтом, про который ЧЯ говорит что не найден,
        при этом возвращая password_status='BAD'. Отловили такую ошибку в проде,
        ЧЯ действительно такое мог возвратить!
        """
        self.blackbox_login_error(
            'account.not_found',
            login_status=blackbox.BLACKBOX_LOGIN_NOT_FOUND_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            with_check_cookies=False,
        )

    def test_auth__blackbox_unexpected_response__error(self):
        """
        ЧЯ вернул что-то странное при запросе в метод login,
        то, чего возвращать он никак не должен. Проверим, что корректно
        отработаем данную ситуацию.
        """

        self.env.blackbox.set_blackbox_response_value(
            'login',
            json.dumps(
                {
                    'error': 'ok',
                    'login_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                    'password_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                },
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['backend.blackbox_permanent_error'])

    def test_auth__blackbox_bad_password_with_2fa__error(self):
        """
        Пришли на авторизацию с включенной 2fa и неверным паролем
        Покажем ошибку "нужен ввод одноразового пароля"
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                totp_check_time=TEST_TOTP_CHECK_TIME,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    authid=TEST_OLD_AUTH_ID,
                    ip=TEST_IP,
                    age=TEST_COOKIE_AGE,
                    time=TEST_COOKIE_TIMESTAMP,
                ),
                uid=1234,
                login='other_login',
            ),
        )

        resp = self.make_request(
            self.query_params(password='password'),  # Пароль похож на OTP
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['password.not_matched'])
        expected_account = self.get_expected_response()['account']
        expected_account.update(
            is_2fa_enabled=True,
            is_rfc_2fa_enabled=False,
            is_yandexoid=False,
            is_workspace_user=False,
        )
        eq_(resp['account'], expected_account)
        eq_(resp['password_like_otp'], True)

        self.assert_request_data_saved_in_track()
        self.assert_failed_auth_recorded_to_statbox(
            uid=TEST_UID,
            bruteforce=None,
            login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            is_2fa_enabled='1',
            password_like_otp='1',
        )
        eq_(
            resp['accounts'],
            [
                self.get_account_info(),
                self.get_account_info(uid=1234, login='other_login'),
            ],
        )

    def test_auth__bad_password_with_2fa_doesnt_looks_like_otp__error_and_message(self):
        """
        Пришли на авторизацию с включенной 2fa и неверным паролем
        Кроме того, пароль не похож на одноразовый пароль
        API покажет ошибку неверный пароль и сообщит, что пароль не похож на одноразовый.
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                totp_check_time=TEST_TOTP_CHECK_TIME,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

        resp = self.make_request(self.query_params(), self.default_headers)  # пароль не похож на одноразовый
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['password.not_matched'])
        expected_account = self.get_expected_response()['account']
        expected_account.update(
            is_2fa_enabled=True,
            is_rfc_2fa_enabled=False,
            is_yandexoid=False,
            is_workspace_user=False,
        )
        eq_(resp['account'], expected_account)
        eq_(resp['password_like_otp'], False)

        self.assert_request_data_saved_in_track()
        self.assert_failed_auth_recorded_to_statbox(
            uid=TEST_UID,
            bruteforce=None,
            login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            is_2fa_enabled='1',
            password_like_otp='0',
        )
        eq_(
            resp['accounts'],
            [self.get_account_info()],
        )

    def test_auth__bad_password_with_2fa_looks_like_otp__error_and_message(self):
        """
        Пришли на авторизацию с включенной 2fa и неверным паролем
        Кроме того, пароль похож на одноразовый пароль (проверяем с пробелами)
        API покажет ошибку неверный пароль и сообщит, что пароль похож на одноразовый.
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                totp_check_time=TEST_TOTP_CHECK_TIME,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

        # пароль похож на одноразовый
        resp = self.make_request(self.query_params(password='abcd  abcd'), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['password.not_matched'])
        expected_account = self.get_expected_response()['account']
        expected_account.update(
            is_2fa_enabled=True,
            is_rfc_2fa_enabled=False,
            is_yandexoid=False,
            is_workspace_user=False,
        )
        eq_(resp['account'], expected_account)
        eq_(resp['password_like_otp'], True)

        self.assert_request_data_saved_in_track()
        self.assert_failed_auth_recorded_to_statbox(
            uid=TEST_UID,
            bruteforce=None,
            login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            is_2fa_enabled='1',
            password_like_otp='1',
        )
        eq_(
            resp['accounts'],
            [self.get_account_info()],
        )

    def test_auth__blackbox_password_unknown_status__error(self):
        self.blackbox_login_error('backend.blackbox_failed',
                                  password_status=blackbox.BLACKBOX_PASSWORD_UNKNOWN_STATUS,
                                  with_check_cookies=False,
                                  )

    def test_auth__blackbox_account_disabled__error(self):
        self.blackbox_login_error(
            'account.disabled',
            login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
            uid=TEST_UID,
            with_check_cookies=False,
        )

    def test_auth__blackbox_account_disabled_on_deletion__error(self):
        self.blackbox_login_error(
            'account.disabled_on_deletion',
            login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
            uid=TEST_UID,
            attributes={
                'account.is_disabled': '2',
            },
            with_check_cookies=False,
        )

    def test_auth__blackbox_account_not_found__error(self):
        self.blackbox_login_error('account.not_found',
                                  login_status=blackbox.BLACKBOX_LOGIN_NOT_FOUND_STATUS,
                                  with_check_cookies=False,
                                  )

    def test_auth__blackbox_account_unknown_status__error(self):
        self.blackbox_login_error('backend.blackbox_failed',
                                  login_status=blackbox.BLACKBOX_LOGIN_UNKNOWN_STATUS,
                                  with_check_cookies=False,
                                  )

    def test_auth__blackbox_captcha_is_required__error(self):
        """ЧЯ сказал, что нужна капча при неправильном пароле"""
        login_response = blackbox_login_response(
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['captcha.required'])

        self.assert_request_data_saved_in_track()
        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)

        self.assert_failed_auth_recorded_to_statbox(
            uid=TEST_UID,
            bruteforce=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            with_check_cookies=False,
        )
        self.not_authorized()

    def test_auth__blackbox_captcha_is_required_for_valid_password__error(self):
        """ЧЯ сказал, что нужна капча при правильном пароле, капча еще не вводилась"""
        login_response = blackbox_login_response(
            bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['captcha.required'])

        self.assert_request_data_saved_in_track()
        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)

        self.assert_failed_auth_recorded_to_statbox(
            uid=TEST_UID,
            bruteforce=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_VALID_STATUS,
            with_check_cookies=False,
        )
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_auth__blackbox_captcha_is_required_and_passed__ok(self):
        """Хороший пароль и ЧЯ просит капчу, но она уже была пройдена успешно"""
        login_response = blackbox_login_response(
            bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:pwd',
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.default_headers,
        )

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(
            # Флажок требования капчи сброшен
            is_captcha_required=False,
            is_captcha_checked=True,
            is_captcha_recognized=True,
        )
        self.assert_successful_auth_recorded_to_statbox(
            bruteforce='captcha',
            captcha_passed=True,
            auth_args=dict(
                session_method='edit',
                old_session_uids='1',
                retpath=TEST_RETPATH,
            ),
            skip_profile_check=True,
        )

    def test_auth__blackbox_captcha_is_required_again__error(self):
        """После неправильного пароля просим капчу ещё раз"""
        login_response = blackbox_login_response(
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        resp = self.make_request(self.query_params(track_id=self.track_id), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['captcha.required', 'password.not_matched'])

        self.assert_request_data_saved_in_track()
        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)

        self.assert_failed_auth_recorded_to_statbox(
            uid=TEST_UID,
            bruteforce=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            with_check_cookies=False,
        )
        self.not_authorized()

    def test_auth__blackbox_captcha_is_not_required_without_bruteforce_with_invalid_password__error(self):
        """Если ЧЯ не отдает bruteforce, то капчу не просим даже при неправильном пароле"""
        login_response = blackbox_login_response(
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        resp = self.make_request(self.query_params(track_id=self.track_id), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['password.not_matched'])

        self.assert_request_data_saved_in_track()
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)
        ok_(track.is_captcha_checked)
        ok_(track.is_captcha_recognized)

        self.assert_failed_auth_recorded_to_statbox(
            uid=TEST_UID,
            bruteforce=None,
            login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
            password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            with_check_cookies=False,
        )
        self.not_authorized()

    def test_auth__blackbox_password_is_expired__change_password_state(self):
        """Пароль требует смены при политике сильного пароля (sid=67)"""
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
            subscribed_to=[67],
            dbfields={
                'password_quality.quality.uid': 90,
            },
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'password_expired')
        ok_(not resp['account']['is_yandexoid'])
        self.assertIsNone(resp['validation_method'])

        self.assert_request_data_saved_in_track()
        track = self.track_manager.read(self.track_id)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        ok_(track.is_strong_password_policy_required)
        eq_(track.change_password_reason, 'password_expired')

    def test_auth__blackbox_password_change_is_required__change_password_state(self):
        """Нужна смена пароля, поскольку установлен "третий бит восьмого сида"
        Пароль был отмечен как скомпрометированный службой поддержки, например
        """
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'account_hacked')
        ok_(not resp['account']['is_yandexoid'])
        eq_(resp['validation_method'], 'captcha_and_phone')
        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_captcha_required=True,
            is_captcha_checked=None,
            is_captcha_recognized=None,
            can_use_secure_number_for_password_validation=True,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            has_secure_phone_number=True,
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.password_hash)
        eq_(
            track.submit_response_cache,
            resp,
        )

        self.assert_validation_method_recorded_to_statbox()

        self.env.blackbox.requests[0].assert_post_data_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
            'method': 'login',
        })
        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def test_auth__blackbox_password_change_required_with_captcha_required_and_passed__change_password_state(self):
        """Нужна смена пароля, поскольку установлен "третий бит восьмого сида".
        Пароль был отмечен как скомпрометированный службой поддержки, например.
        Капча уже вводилась
        """
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        resp = self.make_request(self.query_params(track_id=self.track_id), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'account_hacked')
        ok_(not resp['account']['is_yandexoid'])
        eq_(resp['validation_method'], 'captcha_and_phone')
        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_captcha_required=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            change_password_reason='account_hacked',
        )
        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            resp,
        )

        self.assert_validation_method_recorded_to_statbox()

    def test_auth__user_password_is_too_weak_with_strong_password_policy__change_password_state(self):
        """Установлен слишком слабый пароль при политике сильного пароля (sid=67)"""
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[67],
            dbfields={
                'password_quality.quality.uid': 10,
            },
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        with settings_context(
            PWNED_PASSWORD_CHANGE_DENOMINATOR=1,
        ):
            resp = self.make_request(self.query_params(password=TEST_WEAK_PASSWORD), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        self.assertIsNone(resp['validation_method'])
        eq_(resp['change_password_reason'], 'password_weak')
        ok_(not resp['account']['is_yandexoid'])

        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_strong_password_policy_required=True,
            change_password_reason='password_weak',
        )

    def test_auth__user_password_is_too_short_with_strong_password_policy__change_password_state(self):
        """Установлен слишком короткий пароль при политике сильного пароля (sid=67)"""
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[67],
            dbfields={
                'password_quality.quality.uid': 90,
            },
            crypt_password='1:pass',
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        with settings_context(
            PWNED_PASSWORD_CHANGE_DENOMINATOR=1,
        ):
            resp = self.make_request(self.query_params(password=TEST_WEAK_PASSWORD), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        self.assertIsNone(resp['validation_method'])
        eq_(resp['change_password_reason'], 'password_weak')
        ok_(not resp['account']['is_yandexoid'])

        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_strong_password_policy_required=True,
            change_password_reason='password_weak',
        )

    def test_auth__password_need_change_with_strong_password_policy__change_password_state(self):
        """Назначена смена пароля(ТБВС) при политике сильного пароля (sid=67)"""
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            subscribed_to=[67],
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'account_hacked')
        ok_(not resp['account']['is_yandexoid'])
        eq_(resp['validation_method'], 'captcha_and_phone')

        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_strong_password_policy_required=True,
            is_captcha_required=True,
            is_captcha_checked=None,
            is_captcha_recognized=None,
            change_password_reason='account_hacked',
        )

        self.assert_validation_method_recorded_to_statbox()

    def test_auth__password_need_change_with_strong_passwd_policy_with_captcha_required_and_recognized__change_password_state(self):
        """Назначена смена пароля при политике сильного пароля (sid=67). Капча уже вводилась"""
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            subscribed_to=[67],
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        resp = self.make_request(self.query_params(track_id=self.track_id, password=TEST_PASSWORD), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'account_hacked')
        ok_(not resp['account']['is_yandexoid'])
        eq_(resp['validation_method'], 'captcha_and_phone')

        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_strong_password_policy_required=True,
            is_captcha_required=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            change_password_reason='account_hacked',
        )
        self.assert_validation_method_recorded_to_statbox()

    def test_auth__blackbox_password_change_is_required__change_password_state_for_yandexoids(self):
        """Назначена смена пароля(ТБВС) для яндексоида"""
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            aliases={
                'portal': TEST_LOGIN,
                'yandexoid': 'yastaff_login',
            },
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.get_headers(cookie='Session_id='))
        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'account_hacked')
        ok_(resp['account']['is_yandexoid'])
        eq_(resp['validation_method'], 'captcha_and_phone')
        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_captcha_required=True,
            is_captcha_checked=None,
            is_captcha_recognized=None,
            can_use_secure_number_for_password_validation=True,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            has_secure_phone_number=True,
        )

    def test_auth__incompleted_autoregistered_account__complete_autoregistered_state(self):
        """Автозарегистрированный пользователь будет отправлен на страницу завершения регистрации"""
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.100': 1,
                'subscription.suid.100': 1,
            },
            subscribed_to=[67],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'complete_autoregistered')
        ok_(not resp['account']['is_yandexoid'])

        self.assert_track_ok(
            is_complete_autoregistered=True,
            is_strong_password_policy_required=True,
        )

    def test_auth__by_passwd_user_cookies_are_expired__create_new_session(self):
        """При проверке кук получено сообщение, что сессионная кука протухла - создается новая сессия"""
        sessionid_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_EXPIRED_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok()
        self.has_new_session()
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(retpath=TEST_RETPATH),
        )

    def test_auth__by_passwd_with_invalid_cookie__create_new_session(self):
        """При проверке кук, получено сообщение что сессионная кука протухла"""
        sessionid_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok()
        self.has_new_session()
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(retpath=TEST_RETPATH),
        )

    def test_auth__by_passwd_with_wrong_guard__create_new_session(self):
        """При проверке кук, получено сообщение что sessguard неверен"""
        sessionid_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok()
        self.has_new_session()
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(retpath=TEST_RETPATH),
        )

    def test_auth__successful_with_new_service__subscribe_user_to_this_service(self):
        resp = self.make_request(self.query_params(service='lenta'), self.default_headers)
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.23', '1', uid=TEST_UID, db='passportdbshard1')

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'lenta')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'lenta')

    def test_auth__dberror_when_subscribe_user_to_service__pass_silently(self):
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)
        resp = self.make_request(self.query_params(service='lenta'), self.default_headers)
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        self.env.db.check_missing('attributes', 'subscription.23', uid=TEST_UID, db='passportdbshard1')

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'lenta')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'lenta')

    def test_auth__user_already_has_subscription_to_service__do_not_subscribe_this_user(self):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[23],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        resp = self.make_request(self.query_params(service='lenta'), self.default_headers)
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'lenta')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'lenta')

    def test_auth__user_from_service_galatasaray__is_subscribed_to_this_service(self):
        resp = self.make_request(self.query_params(service='galatasaray'), self.default_headers)
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('aliases', 'altdomain', '1/%s' % TEST_LOGIN, uid=TEST_UID, db='passportdbcentral')

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'galatasaray')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'galatasaray')

    def test_auth__user_already_has_subscription_to_galatasaray_do_not_subscribe_this_user(self):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            aliases={
                'portal': TEST_LOGIN,
                'altdomain': TEST_GALATASARAY_ALIAS,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        resp = self.make_request(self.query_params(service='galatasaray'), self.default_headers)
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'galatasaray')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'galatasaray')

    def test_auth__lite_user_from_service_galatasaray__is_not_subscribed(self):
        login_response = blackbox_login_response(
            login='user@okna.ru',
            aliases={
                'lite': 'user@okna.ru',
            },
            subscribed_to=[33],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        with settings_context(
            LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=0,
            FORCED_CHALLENGE_CHANCE=0.0,
            FORCED_CHALLENGE_PERIOD_LENGTH=3600,
            TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
            ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request(self.query_params(service='galatasaray'), self.default_headers)
        eq_(json.loads(resp.data)['status'], 'ok')

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('aliases', 'altdomain', uid=TEST_UID, db='passportdbcentral')

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'galatasaray')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'galatasaray')

    def test_auth__lite_user_from_requres_login_service__is_not_subscribed(self):
        login_response = blackbox_login_response(
            login='user@okna.ru',
            aliases={
                'lite': 'user@okna.ru',
            },
            subscribed_to=[33],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        with settings_context(
            LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=0,
            FORCED_CHALLENGE_CHANCE=0.0,
            FORCED_CHALLENGE_PERIOD_LENGTH=3600,
            TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
            ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request(self.query_params(service='mail'), self.default_headers)
        eq_(json.loads(resp.data)['status'], 'ok')

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('aliases', 'mail', uid=TEST_UID, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.host_id', uid=TEST_UID, db='passportdbshard1')

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'mail')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'mail')

    def test_auth__social_user_from_requres_login_service__is_not_subscribed(self):
        login_response = blackbox_login_response(
            login='uid-aasjf375',
            aliases={
                'social': 'uid-aasjf375',
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        resp = self.make_request(self.query_params(service='mail'), self.default_headers)
        eq_(json.loads(resp.data)['status'], 'ok')

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('aliases', 'mail', uid=TEST_UID, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.host_id', uid=TEST_UID, db='passportdbshard1')

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'mail')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'mail')

    def test_auth__user_from_requires_password_service__is_not_subscribed(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        resp = self.make_request(self.query_params(service='jabber'), self.default_headers)
        eq_(json.loads(resp.data)['status'], 'ok')

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('aliases', 'mail', uid=TEST_UID, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.host_id', uid=TEST_UID, db='passportdbshard1')

        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'jabber')

        # method=login
        login_data = self.env.blackbox._mock.request.call_args_list[0][0][2]
        eq_(login_data['from'], 'jabber')

    def test_auth__by_passwd_with_restricted_session__external_session_created(self):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            restricted_session=True,
            crypt_password='1:pwd',
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        with settings_context(
            IS_INTRANET=True,
            PASSPORT_SUBDOMAIN='passport-test',
            ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request(self.query_params(), self.get_headers(cookie='Session_id='))
        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_track_ok(is_session_restricted=True)
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                    yandexuid='-',
                ),
            ],
        )
        check_url_contains_params(
            self.env.blackbox._mock.request.call_args[0][1],
            {
                'method': 'createsession',
                'ttl': '5',
                'yateam_auth': '0',
            },
        )

    def test_auth__by_passwd__user_country_invalid(self):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            attributes={'person.country': 'USSR'},
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        resp = self.make_request(self.query_params(), self.get_headers())
        response = json.loads(resp.data)
        eq_(response['status'], 'ok')
        ok_('country' not in response['account']['person'], response)

    def test_auth_2fa_password_change_nonsense(self):
        """
        Поскольку включена 2FA, то установленный флаг принудительной смены
        пароля не приводит к перенаправлению на соответствующую страничку.
        """
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'account.2fa_on': '1',
            },
            emails=[
                self.create_native_email(TEST_LOGIN, TEST_DOMAIN),
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            accounts=[self.get_account_info()],
            default_uid=TEST_UID,
        )
        self.assert_track_ok(
            old_session_create_timestamp=TEST_COOKIE_TIMESTAMP,
            old_session_ip=TEST_IP,
            old_session_age=TEST_COOKIE_AGE,
        )
        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            self.get_expected_response(accounts=[self.get_account_info()], default_uid=TEST_UID),
        )
        ok_('cookies' not in track.submit_response_cache)
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                old_session_uids='1',
                retpath=TEST_RETPATH,
                session_method='edit',
                is_2fa_enabled='1',
            ),
            skip_profile_check=True,
        )
        self.has_updated_session()

    def test_account_global_logout_after_track_created_ok(self):
        """
        Пришли в ручку, на пользователя поставили глобал логаут после того,
        как был создан авторизационный трек. Пускаем его, т.к. это первый шаг
        авторизации по логину-паролю
        """
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'account.2fa_on': '1',
                'account.global_logout_datetime': str(int(time.time()) + 1),
            },
            emails=[
                self.create_native_email(TEST_LOGIN, TEST_DOMAIN),
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            accounts=[self.get_account_info()],
            default_uid=TEST_UID,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.auth_method, 'otp')


@with_settings_hosts(
    DISABLE_CHANGE_PASSWORD_PHONE_EXPERIMENT=False,
    **DEFAULT_TEST_SETTINGS
)
class RobotSuspectedSubmitAuthTestCase(BaseSubmitAuthViewTestCase):

    def test_auth__password_change_is_required_and_user_has_secure_phone__change_password_state_with_phone_number(self):
        """Нужна смена пароля, причем пользователь подозревается на "роботность" - ответе есть номер защищенного телефона"""
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:pwd',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        headers = self.get_headers()

        resp = self.make_request(self.query_params(), headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'account_hacked')
        eq_(resp['validation_method'], 'captcha_and_phone')
        eq_(resp['number'], TEST_PHONE_NUMBER_DUMP)
        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_captcha_required=True,
            is_captcha_checked=None,
            is_captcha_recognized=None,
            can_use_secure_number_for_password_validation=True,
            has_secure_phone_number=True,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            is_change_password_sms_validation_required=True,
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.password_hash)

        self.assert_validation_method_recorded_to_statbox(validation_method='captcha_and_phone')

    def test_auth__password_change_is_required_and_user_has_secure_phone__disable_experiment(self):
        """Нужна смена пароля, причем пользователь подозревается на "роботность", есть номер защищенного телефона, но эксперимент с телефонами выключен"""
        with settings_context(
            DISABLE_CHANGE_PASSWORD_PHONE_EXPERIMENT=True,
            ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
        ):
            phone_secured = build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
            )
            account_kwargs = dict(
                uid=TEST_UID,
                login=TEST_LOGIN,
                dbfields={
                    'subscription.login_rule.8': 4,
                },
                attributes={
                    'password.forced_changing_reason': '1',
                },
                crypt_password='1:pwd',
            )
            account_kwargs = deep_merge(account_kwargs, phone_secured)

            login_response = blackbox_login_response(**account_kwargs)

            self.env.blackbox.set_blackbox_response_value(
                'login',
                login_response,
            )

            headers = self.get_headers()

            resp = self.make_request(self.query_params(), headers)
            eq_(resp.status_code, 200)

            resp = json.loads(resp.data)
            eq_(resp['status'], 'ok')
            eq_(resp['state'], 'change_password')
            eq_(resp['change_password_reason'], 'account_hacked')
            eq_(resp['validation_method'], 'captcha')
            self.assert_track_ok(
                is_password_change=True,
                is_force_change_password=True,
                is_captcha_required=True,
                is_captcha_checked=None,
                is_captcha_recognized=None,
                can_use_secure_number_for_password_validation=True,
                has_secure_phone_number=None,
                secure_phone_number=TEST_PHONE_NUMBER.e164,
                is_change_password_sms_validation_required=False,
            )
            track = self.track_manager.read(self.track_id)
            ok_(track.password_hash)

            self.assert_validation_method_recorded_to_statbox(validation_method='captcha')

    def test_auth__password_change_is_required_and_user_has_no_secure_phone__change_password_state(self):
        """Нужна смена пароля, причем пользователь подозревается на "роботность" - просим верификацию по телефону, который надо привязать"""
        phone_bound = build_phone_bound(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:pwd',
        )
        account_kwargs = deep_merge(account_kwargs, phone_bound)

        login_response = blackbox_login_response(**account_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        headers = self.get_headers()

        resp = self.make_request(self.query_params(), headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'change_password')
        eq_(resp['change_password_reason'], 'account_hacked')
        eq_(resp['validation_method'], 'captcha_and_phone')
        self.assertNotIn('number', resp)
        self.assert_track_ok(
            is_password_change=True,
            is_force_change_password=True,
            is_captcha_required=True,
            is_captcha_checked=None,
            is_captcha_recognized=None,
            has_secure_phone_number=None,
            can_use_secure_number_for_password_validation=False,
            secure_phone_number=None,
            is_change_password_sms_validation_required=True,
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.password_hash)

        self.assert_validation_method_recorded_to_statbox(validation_method='captcha_and_phone')


@with_settings_hosts(
    **DEFAULT_TEST_SETTINGS
)
class SubmitAuthIntegrationalTestCase(BaseSubmitAuthViewTestCase):
    """Проверим авторизацию в самом общем смысле - для обычного пользователя"""

    def setup_blackbox_responses(self, env):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:pwd',
        )
        env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        lrandoms_response = blackbox_lrandoms_response()
        env.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)

        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            ttl=5,
        )
        env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        createsession_response = blackbox_createsession_response()
        env.blackbox.set_blackbox_response_value(
            'createsession',
            createsession_response,
        )
        env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(),
        )

        self.env.blackbox.set_blackbox_response_value('sign', blackbox_sign_response())

    def setUp(self):
        self.patches = []
        self.setup_env()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.default_headers = self.get_headers()

        self.setup_trackid_generator()

        self.setup_blackbox_responses(self.env)
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()

        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()

    def test_auth__by_passwd__ok(self):
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        cookies = sorted(resp.pop('cookies', []))

        eq_(resp, self.get_expected_response(accounts=[self.get_account_info()], default_uid=TEST_UID))

        eq_(
            len(cookies),
            8,
            'After auth, there should be these cookies: sessionid, sessionid2, L, lah, yp, ys, yandexlogin, mda2_beacon. '
            'But presented: %s' % cookies,
        )
        # Все куки в комплекте - проверим их содержимое
        l_cookie, sessionid_cookie, lah_cookie, mda2_beacon, sessionid2, yandexlogin_cookie, yp_cookie, ys_cookie = cookies
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

        self.assert_track_ok()

    def test_auth__cookie_info_logged_to_stabox__ok(self):
        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='yp=%s; ys=%s; %s' % (
                    COOKIE_YP_VALUE,
                    COOKIE_YS_VALUE,
                    TEST_USER_COOKIES,
                ),
            ),
        )
        eq_(resp.status_code, 200)
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                retpath=TEST_RETPATH,
            ),
            submitted_kwargs=dict(
                retpath=TEST_RETPATH,
                cookie_my=TEST_COOKIE_MY,
                cookie_yp=COOKIE_YP_VALUE,
                cookie_ys=COOKIE_YS_VALUE,
                l_login=TEST_LOGIN,
                l_uid=str(TEST_UID),
            ),
            with_check_cookies=False,
        )

    def test_auth__invalid_l_cookie_to_statbox(self):
        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='yandexuid=%s; yp=%s; ys=%s; L=invalid; my=%s' % (
                    TEST_YANDEXUID_COOKIE,
                    COOKIE_YP_VALUE,
                    COOKIE_YS_VALUE,
                    TEST_COOKIE_MY,
                ),
            ),
        )
        eq_(resp.status_code, 200)
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                retpath=TEST_RETPATH,
            ),
            submitted_kwargs=dict(
                yandexuid=TEST_YANDEXUID_COOKIE,
                retpath=TEST_RETPATH,
                cookie_yp=COOKIE_YP_VALUE,
                cookie_ys=COOKIE_YS_VALUE,
                cookie_my=TEST_COOKIE_MY,
            ),
            with_check_cookies=False,
        )

    def test_auth__no_l_cookie(self):
        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='yandexuid=%s; yp=%s; ys=%s; my=%s' % (
                    TEST_YANDEXUID_COOKIE,
                    COOKIE_YP_VALUE,
                    COOKIE_YS_VALUE,
                    TEST_COOKIE_MY,
                ),
            ),
        )
        eq_(resp.status_code, 200)
        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                retpath=TEST_RETPATH,
            ),
            submitted_kwargs=dict(
                yandexuid=TEST_YANDEXUID_COOKIE,
                retpath=TEST_RETPATH,
                cookie_yp=COOKIE_YP_VALUE,
                cookie_ys=COOKIE_YS_VALUE,
                cookie_my=TEST_COOKIE_MY,
            ),
            with_check_cookies=False,
        )

    def test_auth__by_passwd__ok__with_extra_sessguard(self):
        """ Проверка авторизации с дополнительным sessguard для поддомена """
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_createsession_response(
                sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
            ),
        )
        self.env.blackbox.set_response_side_effect(
            'sign',
            [
                blackbox_sign_response(),
                blackbox_sign_response(),
            ]
        )

        resp = self.make_request(self.query_params(), self.default_headers)

        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        cookies = sorted(resp.pop('cookies', []))

        eq_(
            resp,
            self.get_expected_response(
                accounts=[self.get_account_info()],
                default_uid=TEST_UID,
                service_guard_container='123.abc',
            ),
        )

        eq_(
            len(cookies),
            9,
            'After auth with sessguard, there should be these cookies: sessionid, sessionid2, sessguard, L, lah, yp, ys, yandexlogin, mda2_beacon. '
            'But presented: %s' % cookies,
        )
        # Все куки в комплекте - проверим их содержимое
        l_cookie, sessionid_cookie, lah_cookie, mda2_beacon, sessguard, sessionid2, yandexlogin_cookie, yp_cookie, ys_cookie = cookies
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)
        self.assert_cookie_ok(sessguard, 'sessguard', expires=None, domain='.passport-test.yandex.ru', secure=True, http_only=True)

        self.assert_blackbox_sign_sessguard_called()

        self.assert_track_ok()


@with_settings_hosts(
    LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=0,
    **DEFAULT_TEST_SETTINGS
)
class SubmitAuthLITEIntegrationalTestCase(BaseSubmitAuthViewTestCase):
    """Проверим авторизацию в самом общем смысле - для lite-пользователя"""

    def get_base_query_params(self):
        return {
            'login': TEST_ENTERED_LITE_LOGIN,
            'password': TEST_PASSWORD,

            'retpath': TEST_RETPATH,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
        }

    def request_track(self):
        return dict(
            user_entered_login=TEST_ENTERED_LITE_LOGIN,
            retpath=TEST_RETPATH,
            origin=TEST_ORIGIN,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
            fretpath=TEST_FRETPATH,
            clean='yes',
        )

    def base_track(self):
        """Поля в треке и их нормальные значения"""
        request_data = self.request_track()
        account_data = dict(
            uid=TEST_UID,
            login=TEST_LITE_LOGIN,
            language=TEST_USER_LANGUAGE,
            # Всякое специфичное
            is_strong_password_policy_required=False,
        )
        return merge_dicts(request_data, account_data)

    def setup_blackbox_responses(self, env):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LITE_LOGIN,
            crypt_password='1:pwd',
        )
        env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        lrandoms_response = blackbox_lrandoms_response()
        env.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)

        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LITE_LOGIN,
            ttl=5,
        )
        env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_createsession_response(),
        )

        self.env.blackbox.set_response_side_effect('sign', [blackbox_sign_response()])

    def setUp(self):
        self.patches = []
        self.setup_env()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.default_headers = self.get_headers()

        self.setup_trackid_generator()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_blackbox_responses(self.env)
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()

    def test_auth__by_passwd__ok(self):
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        cookies = sorted(resp.pop('cookies', []))

        eq_(
            resp,
            self.get_expected_response(
                login=TEST_LITE_LOGIN,
                accounts=[self.get_account_info(login=TEST_LITE_LOGIN)],
                default_uid=TEST_UID,
            ),
        )

        eq_(
            len(cookies),
            8,
            'After auth, there should be these cookies: sessionid, sessionid2, L, lah, yp, ys, yandexlogin, mda2_beacon. '
            'But presented: %s' % cookies,
        )
        # Все куки в комплекте - проверим их содержимое
        l_cookie, sessionid_cookie, lah_cookie, mda2_beacon, sessionid2_cookie, yandexlogin_cookie, yp_cookie, ys_cookie = cookies
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2_cookie, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

        self.assert_blackbox_editsession_call()

        self.assert_track_ok()


@with_settings_hosts(
    FORCE_ISSUE_PORTAL_COOKIE_TO_LITE_USERS=False,
    LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=1,
    **DEFAULT_TEST_SETTINGS
)
class SubmitMultiAuthTestCase(BaseSubmitAuthViewTestCase):

    def setUp(self):
        super(SubmitMultiAuthTestCase, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

    def get_expected_response(self, **kwargs):
        expected = super(SubmitMultiAuthTestCase, self).get_expected_response(**kwargs)
        expected.update(kwargs)
        return expected

    def assert_create_session_called(self):
        calls = self.env.blackbox.get_requests_by_method('createsession')
        assert len(calls) == 1
        calls[0].assert_query_contains(
            {
                'uid': str(TEST_UID),
                'lang': '1',
                'password_check_time': TimeNow(),
                'have_password': '1',
                'ver': '3',
                'format': 'json',
                'keyspace': 'yandex.ru',
                'is_lite': '0',
                'ttl': '5',
                'userip': TEST_IP,
                'host_id': '7f',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport-test.yandex.ru,test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def assert_edit_session_called(self, is_lite=False, ssl_session=None):
        calls = self.env.blackbox.get_requests_by_method('editsession')
        assert len(calls) == 1
        args = {
            'sessionid': '0:old-session',
            'op': 'add',
            'uid': str(TEST_UID),
            'lang': '1',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'format': 'json',
            'keyspace': 'yandex.ru',
            'host': TEST_HOST,
            'userip': TEST_IP,
            'new_default': str(TEST_UID),
            'create_time': TimeNow(),
            'guard_hosts': 'passport-test.yandex.ru,test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }
        if is_lite:
            args['is_lite'] = '1'
        if ssl_session:
            args['sslsessionid'] = ssl_session
        calls[0].assert_query_contains(args)

    def assert_sessionid_called(self, ssl_session=None):
        calls = self.env.blackbox.get_requests_by_method('sessionid')
        assert len(calls) == 1
        expected_args = {
            'sessionid': '0:old-session',
            'multisession': 'yes',
        }
        if ssl_session:
            expected_args['sslsessionid'] = ssl_session
        calls[0].assert_query_contains(expected_args)

    def assert_authlog_records(self, expected_records):
        """Произошел один вызов логгера авторизации - обновление сессии пользователя"""
        eq_(self.env.auth_handle_mock.call_count, len(expected_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_records,
        )

    def test_auth_by_passwd_with_cookies__overflow_error(self):
        """
        Приходим с логином-паролем на авторизацию с мультикукой.
        ЧЯ говорит, что в куку больше нельзя дописать пользователей
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
                allow_more_users=False,
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        actual_response = json.loads(resp.data)
        eq_(
            actual_response,
            {
                'status': 'error',
                'errors': [u'sessionid.overflow'],
                'track_id': self.track_id,
            },
        )

    def test_auth_by_passwd_with_cookies__no_overflow_for_same_account(self):
        """
        Приходим с логином-паролем на авторизацию с мультикукой.
        ЧЯ говорит, что в куку больше нельзя дописать пользователей,
        но мы пришли тем же, кто уже есть в куке, а значит нас пропускают далее
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
                allow_more_users=False,
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
        )
        self.assert_track_ok(
            old_session_create_timestamp=TEST_COOKIE_TIMESTAMP,
            old_session_ip=TEST_IP,
            old_session_age=TEST_COOKIE_AGE,
        )
        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            self.get_expected_response(accounts=[self.get_account_info()], default_uid=TEST_UID),
        )
        ok_('cookies' not in track.submit_response_cache)

        assert len(self.env.blackbox.requests) == 3
        self.assert_blackbox_login_called()
        self.assert_sessionid_called()
        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='edit',
                uids_count='1',
                old_session_uids='1',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    login=TEST_LOGIN,
                    status='ses_update',
                    comment='aid=%s;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_auth_by_passwd_with_cookies__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя и паролем и валидной сессионной кукой
        Для выдачи сессионных кук вызывается editsession op=add
        """
        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
        )
        self.assert_track_ok(
            old_session_create_timestamp=TEST_COOKIE_TIMESTAMP,
            old_session_ip=TEST_IP,
            old_session_age=TEST_COOKIE_AGE,
        )
        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            self.get_expected_response(accounts=[self.get_account_info()], default_uid=TEST_UID),
        )
        ok_('cookies' not in track.submit_response_cache)

        assert len(self.env.blackbox.requests) == 3
        self.assert_blackbox_login_called()
        self.assert_sessionid_called()
        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='edit',
                uids_count='1',
                old_session_uids='1',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    login=TEST_LOGIN,
                    status='ses_update',
                    comment='aid=%s;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_auth_by_passwd_with_foreign_cookies__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя и паролем
        и валидной сессионной кукой ДРУГОГО пользователя. Проверим ответ с информацией о всех пользователях.
        Для выдачи сессионных кук вызывается editsession op=add
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=1234,
                login='other_login',
                authid=TEST_OLD_AUTH_ID,
                ttl=5,
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(uid=1234, login='other_login'),
                self.get_account_info(),
            ],
        )

        assert len(self.env.blackbox.requests) == 3
        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='edit',
                uids_count='2',
                old_session_uids='1234',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    status='ses_update',
                    login='other_login',
                    comment='aid=%s;ttl=5' % TEST_AUTH_ID,
                    uid='1234',
                ),
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

    def test_auth_by_passwd_with_foreign_cookies_with_invalid_default_session__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя и паролем,
        и валидной сессионной кукой ДРУГОГО пользователя, сессия которого невалидна
        Проверим ответ с информацией о всех пользователях.
        Для выдачи сессионных кук вызывается editsession op=add
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=1234,
                login='other_login',
                authid=TEST_OLD_AUTH_ID,
                default_user_status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                ttl=5,
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(uid=1234, login='other_login'),
                self.get_account_info(),
            ],
        )

        assert len(self.env.blackbox.requests) == 3
        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='edit',
                uids_count='2',
                old_session_uids='1234',
                retpath=TEST_RETPATH,
            ),
        )
        # Сессия предыдущего дефолта невалидна - не пишем на него update
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

    def test_lite_auth_by_passwd_with_foreign_cookies__ok(self):
        """
        ЛАЙТ-пользователя с именем пользователя, паролем и валидной сессионной кукой
        ДРУГОГО пользователя тоже отправляем на дорегистрацию.
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                aliases={
                    'lite': TEST_LITE_LOGIN,
                },
                subscribed_to=[33],
                crypt_password='1:pwd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=1234,
                login='other_login',
                authid=TEST_OLD_AUTH_ID,
                ttl=5,
            ),
        )
        expected_account = self.get_expected_response(
            **self.get_account_info(login=TEST_LITE_LOGIN)
        )['account']
        expected_account.update(
            is_2fa_enabled=False,
            is_rfc_2fa_enabled=False,
            is_yandexoid=False,
            is_workspace_user=False,
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        self.assert_ok_response(
            resp,
            state='force_complete_lite',
            account=expected_account,
            track_id=self.track_id,
            has_recovery_method=False,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.is_force_complete_lite, True)
        eq_(track.is_password_passed, True)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        eq_(self.env.blackbox._mock.request.call_count, 1)
        self.assert_blackbox_login_called()
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_auth_by_passwd_with_multi_cookies__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя, паролем
        и валидной сессионной мультикукой с дефолтным тем же пользователем
        и другим пользователем. Проверим ответ с информацией о всех пользователях.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    authid=TEST_OLD_AUTH_ID,
                    ttl=5,
                ),
                uid=1234,
                login='other_login',
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(),
                self.get_account_info(uid=1234, login='other_login'),
            ],
        )

        assert len(self.env.blackbox.requests) == 3
        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='edit',
                uids_count='2',
                old_session_uids='1,1234',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    login=TEST_LOGIN,
                    status='ses_update',
                    comment='aid=%s;ttl=5' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    status='ses_update',
                    login='other_login',
                    comment='aid=%s;ttl=5' % TEST_AUTH_ID,
                    uid='1234',
                ),
            ],
        )

    def test_auth_by_passwd_with_multi_cookies_by_https__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя, паролем,
        валидной сессионной мультикукой с дефолтным тем же пользователем
        и другим пользователем по хттпс.
        Проверим ответ с информацией о всех пользователях и факт вызова ЧЯ
        с правильными флагами
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=1234,
                login='other_login',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(),
                self.get_account_info(uid=1234, login='other_login'),
            ],
        )
        assert len(self.env.blackbox.requests) == 3
        self.assert_sessionid_called(ssl_session='0:old-sslsession')

        self.assert_edit_session_called(ssl_session='0:old-sslsession')

        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(
                session_method='edit',
                uids_count='2',
                old_session_uids='1,1234',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    login=TEST_LOGIN,
                    status='ses_update',
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    status='ses_update',
                    login='other_login',
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                    uid='1234',
                ),
            ],
        )

    def test_auth_by_passwd_upgrade_session_to_safe_https__ok(self):
        """
        Пользователь логинется в мультикуку с логином-паролем по хттпс,
        в которой он и другой были несекьюрные.
        Тот кто авторизовывался получит секьюрную куку.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=1234,
                login='other_login',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(),
                self.get_account_info(uid=1234, login='other_login'),
            ],
        )
        assert len(self.env.blackbox.requests) == 3
        self.assert_sessionid_called()

        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(
                session_method='edit',
                uids_count='2',
                old_session_uids='1,1234',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    login=TEST_LOGIN,
                    status='ses_update',
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    status='ses_update',
                    login='other_login',
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                    uid='1234',
                ),
            ],
        )

    def test_auth_by_passwd_with_multi_cookies_invalid_user_session__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя, паролем
        и валидной сессионной мультикукой, в которой сессия этого пользователя не валидна.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=1234,
                    login='other_login',
                    authid=TEST_OLD_AUTH_ID,
                ),
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
                login='',
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(),
                self.get_account_info(uid=1234, login='other_login'),
            ],
        )

        assert len(self.env.blackbox.requests) == 3
        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(
                session_method='edit',
                uids_count='2',
                old_session_uids='1,1234',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    uid='1234',
                    login='other_login',
                    status='ses_update',
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 0,
                    }),
                ),
            ],
        )

    def test_auth_by_passwd_with_multi_cookies_unknown_uid__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя, паролем
        и валидной сессионной мультикукой, в которой есть пользователь с пустым uid.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=1234,
                    login='other_login',
                    authid=TEST_OLD_AUTH_ID,
                ),
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=None,
                item_id=9999,
            ),
        )

        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(uid=1234, login='other_login'),
                self.get_account_info(),
            ],
        )
        assert len(self.env.blackbox.requests) == 3
        self.assert_edit_session_called()
        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(
                session_method='edit',
                uids_count='3',
                old_session_uids='1234,9999',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    uid='1234',
                    login='other_login',
                    status='ses_update',
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 0,
                    }),
                ),
            ],
        )

    def test_auth_by_passwd_with_invalid_cookie__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя и паролем и невалидной сессионной кукой
        Создаем сессию через createsession
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
        )
        self.assert_track_ok()
        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            self.get_expected_response(accounts=[self.get_account_info()], default_uid=TEST_UID),
        )
        ok_('cookies' not in track.submit_response_cache)

        assert len(self.env.blackbox.requests) == 3
        self.assert_blackbox_login_called()
        self.assert_sessionid_called()
        self.assert_create_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='create',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

    def test_auth_by_passwd_with_invalid_and_empty_user_in_cookie__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя, паролем
        и валидной сессионной мультикукой, в которой есть невалидная и без информации о пользователе сессия.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_invalid_session(
                blackbox_sessionid_multi_response(
                    uid=1234,
                    login='other_login',
                    authid=TEST_OLD_AUTH_ID,
                ),
                item_id='123',
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(uid=1234, login='other_login'),
                self.get_account_info(),
            ],
        )
        assert len(self.env.blackbox.requests) == 3
        self.assert_blackbox_login_called()
        self.assert_sessionid_called()
        self.assert_edit_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(
                session_method='edit',
                uids_count='3',
                old_session_uids='1234,123',
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    uid='1234',
                    login='other_login',
                    status='ses_update',
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 0,
                    }),
                ),
            ],
        )

    def test_auth_by_passwd_without_cookie__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя и паролем и БЕЗ сессионной кукой
        Создаем сессию через createsession
        """
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
        )
        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            self.get_expected_response(accounts=[self.get_account_info()], default_uid=TEST_UID),
        )
        ok_('cookies' not in track.submit_response_cache)

        assert len(self.env.blackbox.requests) == 2
        self.assert_blackbox_login_called()
        self.assert_create_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='create',
                retpath=TEST_RETPATH,
            ),
            with_check_cookies=False,
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

    def test_auth_by_passwd_without_cookie_with_social_user__ok(self):
        """
        Все проходит без ошибок по пути с именем пользователя и паролем,
        без куки изначально. Пользователь имеет привязанный социальный профиль.
        Создаем сессию через createsession. Социальный профиль не передаем.
        """
        expected_display_name = {
            'name': 'Some User',
            'social': {
                'provider': 'fb',
                'profile_id': 123456,
            },
            'default_avatar': '',
        }

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=expected_display_name,
                crypt_password='1:pwd',
            ),
        )
        response = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        eq_(response.status_code, 200, [response.status_code, response.data])
        expected_response = self.get_expected_response(
            accounts=[self.get_account_info(display_name=expected_display_name)],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        expected_response['account']['display_name'] = expected_display_name
        actual_response = json.loads(response.data)
        actual_response['cookies'] = sorted(actual_response['cookies'])
        eq_(actual_response, expected_response)
        expected_cached_response = self.get_expected_response(
            accounts=[self.get_account_info(display_name=expected_display_name)],
        )
        expected_cached_response['account']['display_name'] = expected_display_name
        expected_cached_response['default_uid'] = TEST_UID

        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            expected_cached_response,
        )
        ok_('cookies' not in track.submit_response_cache)

        assert len(self.env.blackbox.requests) == 2
        self.assert_blackbox_login_called()
        self.assert_create_session_called()

        self.assert_successful_auth_recorded_to_statbox(
            auth_args=dict(
                session_method='create',
                retpath=TEST_RETPATH,
            ),
            with_check_cookies=False,
        )
        self.assert_authlog_records(
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

    def test_auth_by_passwd__editsession_raises_blackbox_invalid_params__error(self):
        """
        При проверке куки по методу sessionid не возникло ошибок, но
        при вызове метода editsession возникла ошибка ЧЯ из-за того, что сессия недействительна
        """
        other_login, other_uid = 'other_login', 1234
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=other_uid,
                login=other_login,
            ),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'editsession',
            blackbox.BlackboxInvalidParamsError(blackbox.BLACKBOX_ERROR_SESSION_LOGGED_OUT),
        )

        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )

        self.assert_error_response(
            resp,
            ['sessionid.expired'],
            track_id=self.track_id,
            accounts=[self.get_account_info(), self.get_account_info(other_login, other_uid)],
        )

        assert len(self.env.blackbox.requests) == 3
        self.assert_sessionid_called(ssl_session='0:old-sslsession')
        self.assert_edit_session_called(ssl_session='0:old-sslsession')

        self.assert_events_are_empty(self.env.auth_handle_mock)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_auth_by_passwd__editsession_raises_blackbox_invalid_params_with_unknown_message__error(self):
        """
        При проверке куки по методу sessionid не возникло ошибок, но
        при вызове метода editsession возникла ошибка InvalidParams ЧЯ с неизвестным сообщением
        """
        other_login, other_uid = 'other_login', 1234
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=other_uid,
                login=other_login,
            ),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'editsession',
            blackbox.BlackboxInvalidParamsError(),
        )

        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )

        self.assert_error_response(
            resp,
            ['exception.unhandled'],
            track_id=self.track_id,
            accounts=[self.get_account_info(), self.get_account_info(other_login, other_uid)],
        )

        assert len(self.env.blackbox.requests) == 3
        self.assert_sessionid_called(ssl_session='0:old-sslsession')
        self.assert_edit_session_called(ssl_session='0:old-sslsession')

        self.assert_events_are_empty(self.env.auth_handle_mock)
        self.assert_events_are_empty(self.env.handle_mock)


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
)
class ForcedChallengeAccountAttributeTestCase(BaseSubmitAuthViewTestCase):
    def test_forced_challenge_for_account_with_force_challenge_attribute(self):
        self.setup_login_response(attributes={'account.force_challenge': '1'})

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = False
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_track_ok(is_auth_challenge_shown=True)
        self.assert_ok_response(resp, check_all=False, state='auth_challenge')

    def test_no_skip_challenge_for_account_with_force_challenge_attribute(self):
        self.setup_login_response(attributes={'account.force_challenge': '1', 'account.is_shared': '1'})

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_auth_challenge_shown = False
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(
            self.query_params(track_id=self.track_id),
            self.get_headers(),
        )
        self.assert_track_ok(is_auth_challenge_shown=True)
        self.assert_ok_response(resp, check_all=False, state='auth_challenge')


@with_settings_hosts(
    **dict(
        DEFAULT_TEST_SETTINGS,
        ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    )
)
class AntifraudSubmitAuthTestCase(BaseSubmitAuthViewTestCase):
    def setUp(self):
        super(AntifraudSubmitAuthTestCase, self).setUp()
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])

    def assert_ok_antifraud_score_request(self, request):
        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.default()
        params.populate_from_headers(self.get_headers())
        params.external_id = 'track-' + self.track_id
        params.input_login = TEST_ENTERED_LOGIN
        params.retpath = TEST_RETPATH
        params.uid = TEST_UID
        params.available_challenges = ['email_hint']
        params.surface = 'auth_password_submit_old'
        eq_(request_data, params.as_dict())

        request.assert_query_contains(dict(consumer='passport'))

    def test(self):
        resp = self.make_request(self.query_params(), self.default_headers)

        self.assert_response_ok(
            resp,
            accounts=[self.get_account_info()],
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )

        self.assert_track_ok(
            old_session_create_timestamp=TEST_COOKIE_TIMESTAMP,
            old_session_ip=TEST_IP,
            old_session_age=TEST_COOKIE_AGE,
        )

        eq_(len(self.env.antifraud_api.requests), 1)
        self.assert_ok_antifraud_score_request(self.env.antifraud_api.requests[0])
