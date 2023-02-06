# -*- coding: utf-8 -*-
import json
from time import time

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.common.authorization import AUTHORIZATION_SESSION_POLICY_SESSIONAL
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import ViewsTestEnvironment
from passport.backend.api.tests.views.bundle.complete.base.base import (
    BaseCompleteTest,
    build_canonical_social,
    build_complete,
    build_headers,
    build_lite,
    build_neophonish,
    build_social_with_custom_login,
    CompleteCommitTestCaseBase,
    enable_2fa,
    get_account_info,
)
from passport.backend.api.tests.views.bundle.complete.base.base_test_data import (
    FRODO_RESPONSE_BAD_USER,
    FRODO_RESPONSE_SPAM_USER,
    SESSION,
    TEST_ANOTHER_UID,
    TEST_APP_ID,
    TEST_DEFAULT_COMPLETION_URL,
    TEST_IP,
    TEST_LITE_DISPLAY_NAME,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_LOGIN_FOR_NORMALIZATION,
    TEST_NEOPHONISH_DISPLAY_NAME,
    TEST_NEOPHONISH_LOGIN,
    TEST_NOT_STRONG_PASSWORD,
    TEST_OPERATION_TTL,
    TEST_PASSWORD,
    TEST_PASSWORD_LIKE_NORMALIZED_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_OBJECT,
    TEST_RETPATH,
    TEST_SESSIONID_COOKIE,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_SOCIAL_LOGIN,
    TEST_UID,
    TEST_USER_COOKIES,
    TEST_USER_LOGIN,
    TEST_WEAK_PASSWORD,
    TEST_WEAK_PASSWORD_IS_SEQUENCE,
    TEST_WEAK_PASSWORD_IS_WORD,
    TEST_WEAK_PASSWORD_LENGTH,
    TEST_WEAK_PASSWORD_QUALITY,
    TEST_WEAK_PASSWORD_SEQUENCES_NUMBER,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_LOGIN2,
    TEST_PHONE_ID1,
    TEST_PHONISH_LOGIN1,
    TEST_PUBLIC_ID,
    TEST_UID2,
)
from passport.backend.api.views.bundle.constants import (
    PDD_PARTNER_OAUTH_TOKEN_SCOPE,
    X_TOKEN_OAUTH_SCOPE,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
    BLACKBOX_PASSWORD_BAD_STATUS,
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NOAUTH_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.counters import (
    registration_karma,
    sms_per_ip,
)
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.password import (
    get_sha256_hash,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
)
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    build_phone_secured,
)
from passport.backend.core.services import Service
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.types.bit_vector import PhoneBindingsFlags
from passport.backend.utils.common import deep_merge


class CommitTestMixin(object):
    """
    Базовый набор тестов, проверяющий общий код, не зависящий от типа аккаунта.
    """
    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        self.setup_account()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER_OBJECT.e164
            track.phone_confirmation_is_confirmed = True
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_IP)
        for i in range(counter.limit):
            counter.incr(TEST_IP)

        rv = self.make_request(
            **{
                field: u'Заходи дорогой, гостем будешь диваны.рф.',
                'validation_method': 'phone',
            }
        )
        self.assert_error_response(rv, ['{}.invalid'.format(field)], check_content=False)

    def test_registration_sms_limit_reached_error(self):
        self.setup_account()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER_OBJECT.e164
            track.phone_confirmation_is_confirmed = True
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_IP)
        for i in range(counter.limit):
            counter.incr(TEST_IP)

        rv = self.make_request(validation_method='phone')

        self.check_response_error(
            rv,
            ['account.registration_limited'],
            statbox_call_count=2,
        )

        self.assert_statbox_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'registration_with_sms_error',
                counter_current_value=str(counter.limit),
                counter_limit_value=str(counter.limit),
            ),
        ])

    def test_basic_ok_without_optional_params(self):
        self.setup_account()

        rv = self.make_request(
            exclude=['language', 'country', 'gender', 'birthday', 'timezone', 'firstname', 'lastname'],
        )

        self.check_ok(rv, with_optional_params=False)

    def test_ok_with_env_profile_modification(self):
        self.setup_account()

        rv = self.make_request()

        self.check_ok(rv)
        profile = self.make_user_profile(
            raw_env={'ip': TEST_IP, 'yandexuid': TEST_YANDEXUID_COOKIE, 'user_agent_info': {}},
        )
        self.assert_profile_written_to_auth_challenge_log(profile)

    def test_karma_passed_to_frodo(self):
        account = self.build_account({'userinfo': {'karma': 85}})
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok(rv, account_karma=85)


class ChangePasswordTestMixin(object):
    def test_strong_password_is_too_weak(self):
        """
        При подписке на сильный пароль, пришел очень слабый пароль.
        """
        account = self.build_account({'userinfo': {'subscribed_to': [67]}})
        self.setup_account(account)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER

        # Пароль с качеством 50
        rv = self.make_request(password=TEST_NOT_STRONG_PASSWORD)

        self.check_response_error(rv, ['password.weak'], statbox_call_count=2)
        self.assert_statbox_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('password_validation_error'),
        ])

    def test_password_is_too_weak(self):
        """
        Пароль слишком слабый.
        """
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER

        # Пароль с качеством 0
        rv = self.make_request(password=TEST_WEAK_PASSWORD)
        self.check_response_error(rv, ['password.weak'], statbox_call_count=2)

        self.assert_statbox_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'password_validation_error',
                policy='basic',
                is_sequence=tskv_bool(TEST_WEAK_PASSWORD_IS_SEQUENCE),
                sequences_number=str(TEST_WEAK_PASSWORD_SEQUENCES_NUMBER),
                is_word=tskv_bool(TEST_WEAK_PASSWORD_IS_WORD),
                length=str(TEST_WEAK_PASSWORD_LENGTH),
                password_quality=str(TEST_WEAK_PASSWORD_QUALITY),
            ),
        ])


class CommitBindPhoneTestMixin(object):
    # Тесты для ручек в которых телефон ещё не привязан к аккаунту, а
    # привязывается в течение дорегистрации.

    def test_ok_with_phone(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER
            track.is_captcha_recognized = False

        rv = self.make_request(validation_method='phone')

        self.check_ok(
            rv,
            captcha_passed=False,
            phone_validated=True,
            secure_phone_bound=True,
            account_karma='6000',
        )
        self.assert_no_emails_sent()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(-3)

    def test_ok_with_phone_and_strong_policy(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER
            track.is_captcha_recognized = False
            track.is_strong_password_policy_required = True

        rv = self.make_request(validation_method='phone')

        self.check_ok(
            rv,
            captcha_passed=False,
            phone_validated=True,
            secure_phone_bound=True,
            account_karma='6000',
        )
        self.assert_no_emails_sent()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(-3)

    def test_ok_with_frodo_spam_user(self):
        self.setup_account()
        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_SPAM_USER)
        self.env.frodo.set_response_value(u'confirm', u'')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        response = self.make_request(validation_method='phone')

        self.check_ok(
            response,
            bad_user_karma=85,
            captcha_passed=False,
            phone_validated=True,
            secure_phone_bound=True,
            account_karma=6000,
        )
        self.env.db.check('attributes', 'karma.value', '85', uid=1, db='passportdbshard1')

    def test_ok_with_frodo_bad_user(self):
        self.setup_account()
        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_BAD_USER)
        self.env.frodo.set_response_value(u'confirm', u'')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

        response = self.make_request(validation_method='phone')

        self.check_ok(
            response,
            bad_user_karma=100,
            account_karma=6000,
            captcha_passed=False,
            phone_validated=True,
            secure_phone_bound=True,
        )

        self.env.db.check('attributes', 'karma.value', '100', uid=1, db='passportdbshard1')

        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 1)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

    def test_ok_with_binding_phonish(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER
            track.is_captcha_recognized = False
            track.device_application = TEST_APP_ID

        rv = self.make_request(validation_method='phone')

        self.check_ok(
            rv,
            check_db=False,
            check_track=False,
            check_statbox=False,
            check_event_log=False,
            check_frodo=False,
        )
        self.env.social_binding_logger.assert_has_written([
            self.env.social_binding_logger.entry(
                'bind_phonish_account_by_track',
                uid=str(TEST_UID),
                track_id=self.track_id,
                ip=TEST_IP,
            ),
        ])

    def test_user_not_verified_by_phone_error(self):
        self.setup_account()

        rv = self.make_request(validation_method='phone')

        self.check_response_error(rv, ['user.not_verified'])

    def test_phone_not_confirmed(self):
        self.setup_account()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER_OBJECT.e164
            track.phone_confirmation_is_confirmed = False

        rv = self.make_request(validation_method='phone')

        self.check_response_error(rv, ['user.not_verified'])


class CommitQuestionTestMixin(object):
    def test_user_not_verified_by_captcha_error(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False

        rv = self.make_request(validation_method='captcha')

        self.check_response_error(rv, ['user.not_verified'])

    def test_user_verified_by_phone_but_captcha_required_error(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = False
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER

        rv = self.make_request(validation_method='captcha')

        self.check_response_error(rv, ['user.not_verified'])

    def test_no_control_question_args(self):
        rv = self.make_request(question='', question_id='', answer='answer')

        self.check_response_error(
            rv,
            ['question.empty', 'question_id.empty'],
            with_account=False,
            statbox_call_count=0,
        )

    def test_too_many_control_question_args(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        rv = self.make_request(
            validation_method='captcha',
            question='question',
            question_id=1,
            answer='answer',
        )

        self.check_response_error(rv, ['question.inconsistent'])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)


class CommitSessionTestMixin(object):
    def test_with_invalid_session__expired(self):
        self._test_with_invalid_session(
            status=BLACKBOX_SESSIONID_EXPIRED_STATUS,
            expected_error='sessionid.invalid',
        )

    def test_with_invalid_session__noauth(self):
        self._test_with_invalid_session(
            status=BLACKBOX_SESSIONID_NOAUTH_STATUS,
            expected_error='sessionid.invalid',
        )

    def test_with_invalid_session__invalid(self):
        self._test_with_invalid_session(
            status=BLACKBOX_SESSIONID_INVALID_STATUS,
            expected_error='sessionid.invalid',
        )

    def test_with_invalid_session__account_disabled(self):
        self._test_with_invalid_session(
            status=BLACKBOX_SESSIONID_DISABLED_STATUS,
            expected_error='account.disabled',
        )

    def _test_with_invalid_session(self, status, expected_error):
        """
        Пришел пользователь с невалидной авторизацией.
        """
        account = self.build_account({'sessionid': {'status': status}})
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(rv, [expected_error], with_account=False)

    def test_with_invalid_session_disabled_on_deletion(self):
        """
        Пришел пользователь с невалидной авторизацией.
        """
        account = self.build_account({
            'userinfo': {'attributes': {'account.is_disabled': '2'}},
            'sessionid': {
                'enabled': False,
                'status': BLACKBOX_SESSIONID_DISABLED_STATUS,
            },
        })
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['account.disabled_on_deletion'],
            with_account=False,
        )

    def test_blackbox_user_is_disabled_on_deletion_error(self):
        """
        Пользователь с этим uid "выкл" (disabled), и он подписан на блокирующий
        сид -- ошибка обрабатывается.
        """
        account = self.build_account({
            'userinfo': {'attributes': {'account.is_disabled': '2'}},
            'sessionid': {'enabled': False},
        })
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['account.disabled_on_deletion'],
            with_account=False,
        )

    def test_without_sessionid(self):
        """
        Пришел пользователь без куки Session_id.
        """
        self.setup_account()

        rv = self.make_request(headers=build_headers(cookie=''))

        self.check_response_error(rv, ['sessionid.invalid'], with_account=False, statbox_call_count=0)

    def test_wrong_host__error(self):
        rv = self.make_request(
            headers=mock_headers(
                host='google.com',
                user_ip=TEST_IP,
                user_agent='',
                cookie=TEST_USER_COOKIES,
                accept_language='',
            ),
        )

        self.check_response_error(
            rv,
            ['host.invalid'],
            with_retpath=False,
            with_account=False,
            with_track_id=False,
            statbox_call_count=0,
        )

    def test_error_authorization_already_passed(self):
        """
        В треке указано, что авторизация уже пройдена.
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = SESSION['session']['value']

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['account.auth_passed'],
            with_account=False,
            statbox_call_count=0,
        )

    def test_ok_with_empty_optional_headers(self):
        # Отсутствие некоторых заголовком не отражается негативно на работе
        # ручки.
        self.setup_account()

        headers = self.build_headers(
            user_agent='',
            referer='',
            accept_language='',
            cookie=TEST_SESSIONID_COOKIE,
        )
        rv = self.make_request(headers=headers)

        eq_(json.loads(rv.data)['status'], 'ok')
        self.check_frodo(
            multi=True,
            frodo_kwargs={
                'useragent': '',
                'v2_accept_language': '',
                'valkey': '0000000100',
                'fuid': '',
                'v2_yandex_gid': '',
                'v2_has_cookie_my': '0',
                'v2_has_cookie_l': '0',
                'v2_cookie_my_block_count': '',
                'v2_cookie_my_language': '',
                'v2_cookie_l_uid': '',
                'v2_cookie_l_login': '',
                'v2_cookie_l_timestamp': '',
                'yandexuid': '',
            },
        )

    def test_ok_with_short_session(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER
            track.is_captcha_recognized = False
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_SESSIONAL

        rv = self.make_request(validation_method='phone')

        self.check_ok(
            rv,
            captcha_passed=False,
            phone_validated=True,
            secure_phone_bound=True,
            account_karma='6000',
        )
        self.assert_no_emails_sent()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(-3)

    def test_with_another_user(self):
        """
        Пришел пользователь с другим uid.
        """
        account = self.build_account({'userinfo': {'uid': TEST_ANOTHER_UID}})
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['track.invalid_state'],
            with_account=False,
        )

    def test_simple_multisession(self):
        self.setup_account()

        rv = self.make_request()

        self.check_ok(rv)

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called()

    def test_multisession_with_another_default_user(self):
        account1 = self.build_account()
        account2 = build_complete({
            'userinfo': {
                'login': TEST_LOGIN2,
                'uid': TEST_UID2,
                'aliases': {'portal': TEST_LOGIN2},
            },
        })
        self.setup_multi_accounts(
            incomplete_account=account1,
            default_account=account2,
            extra_accounts=[account1],
        )

        rv = self.make_request()

        additional_account = {
            'login': TEST_LOGIN2,
            'uid': TEST_UID2,
            'display_login': TEST_LOGIN2,
            'display_name': {u'default_avatar': u'', u'name': u''},
        }
        self.check_ok(rv, additional_account=additional_account)

    def test_session_valid__user_session_invalid__default(self):
        """
        Пользователь все еще дефолтный и у него невалидная сессия.
        """
        account = self.build_account({
            'sessionid': {
                'default_user_status': BLACKBOX_SESSIONID_INVALID_STATUS,
            },
        })
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(rv, ['sessionid.invalid'], with_account=False)

    def test_session_valid__user_session_invalid__not_default(self):
        """
        Пользователь перестал быть дефолтным и у него невалидная сессия.
        """
        account1 = self.build_account({
            'sessionid': {'status': BLACKBOX_SESSIONID_INVALID_STATUS},
        })
        account2 = build_complete({
            'userinfo': {
                'uid': TEST_UID2,
                'login': TEST_LOGIN2,
                'aliases': {'portal': TEST_LOGIN2},
            },
        })
        self.setup_multi_accounts(
            incomplete_account=account1,
            default_account=account2,
            extra_accounts=[account1],
        )

        rv = self.make_request()

        self.check_response_error(rv, ['sessionid.invalid'], with_account=False)

    def test_normal_account__lite_session(self):
        """
        Пришел пользователь с дорегистрированным аккаунтом, но с lite сессией.
        """
        account = self.build_account(
            account={'sessionid': {'is_lite_session': True}},
            registration_is_complete=True,
        )
        self.setup_account(account)

        rv = self.make_request()

        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(response['state'], 'upgrade_cookies')

    def test_action_not_required_complete_account_with_normal_session(self):
        """
        Пользователя не нужно дорегистрировать, у него полноценная сессия,
        у соседнего пользователя lite сессия.
        """
        account1 = self.build_account(registration_is_complete=True)
        account2 = build_complete({
            'userinfo': {
                'uid': TEST_UID2,
                'login': TEST_LOGIN2,
                'aliases': {'portal': TEST_LOGIN2},
            },
            'sessionid': {'is_lite_session': True},
        })
        self.setup_multi_accounts(
            incomplete_account=None,
            default_account=account1,
            extra_accounts=[account2],
        )

        rv = self.make_request()

        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('state' not in response)

    def test_ok_with_auth_by_key_with_no_session(self):
        account = self.build_account()
        self.setup_multi_accounts(
            incomplete_account=account,
            extra_accounts=[],
            authentication_media='key',
        )
        self.setup_track_for_auth_by_key()

        rv = self.make_request(
            headers=build_headers(cookie='yandexuid=yandexuid;'),
        )

        self.check_ok(rv, check_frodo=False, check_statbox=False, with_lah=True)
        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'cookie_set',
                    input_login=TEST_LOGIN,
                    captcha_passed='1',
                    person_country='tr',
                    uids_count='1',
                ),
            ],
            offset=-1,
        )

    def test_ok_with_auth_by_key_with_another_uid_in_session(self):
        """
        Пользователь считывается из трека, в сессии валидный другой
        пользователь, в результате в сессии становится два пользователя.
        """
        account1 = self.build_account()
        account2 = build_complete({
            'userinfo': {
                'uid': TEST_UID2,
                'login': TEST_LOGIN2,
                'aliases': {'portal': TEST_LOGIN2},
            },
        })
        self.setup_multi_accounts(
            incomplete_account=account1,
            default_account=account2,
            extra_accounts=[],
            authentication_media='key',
        )
        self.setup_track_for_auth_by_key()

        rv = self.make_request(headers=build_headers())

        additional_account = {
            'login': TEST_LOGIN2,
            'uid': TEST_UID2,
            'display_login': TEST_LOGIN2,
            'display_name': {u'default_avatar': u'', u'name': u''},
        }
        self.check_ok(
            rv,
            check_frodo=False,
            check_statbox=False,
            additional_account=additional_account,
            additional_account_index=0,
        )
        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'cookie_set',
                    input_login=TEST_LOGIN,
                    captcha_passed='1',
                    person_country='tr',
                    uids_count='2',
                    old_session_uids=str(TEST_UID2),
                    session_method='edit',
                ),
            ],
            offset=-2,
        )


CleanWebTestMixin = make_clean_web_test_mixin(
    'test_basic_ok',
    ['firstname', 'lastname'],
    statbox_filter={'mode': 'complete'},
)


@with_settings_hosts(
    COMPLETION_URL_TEMPLATE='https:/passport.yandex.%(tld)s/profile/upgrade',
)
class CompleteStatusTestCase(BaseCompleteTest):
    default_url = '/1/bundle/complete/status/'
    consumer = 'dev'
    http_headers = {
        'user_ip': TEST_IP,
        'authorization': 'OAuth xxx',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['completion_status']}))

    def tearDown(self):
        self.env.stop()

    def test_portal(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_LOGIN,
                    crypt_password='1:pwd',
                )
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=True,
            is_completion_available=False,
            is_completion_recommended=False,
            is_completion_required=False,
        )

    def test_phonish(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_PHONISH_LOGIN1,
                    alias_type='phonish',
                    secure=False,
                )
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=False,
            is_completion_recommended=False,
            is_completion_required=False,
        )

    def test_social(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                subscribed_to=[Service.by_slug('social')],
                **self.get_account_kwargs(
                    login=TEST_SOCIAL_LOGIN,
                    alias_type='social',
                    phone=None,
                )
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=False,
            is_completion_required=False,
            completion_url=TEST_DEFAULT_COMPLETION_URL,
        )

    def test_social_with_login(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                subscribed_to=[Service.by_slug('social')],
                **self.get_account_kwargs(
                    login=TEST_LOGIN,
                )
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=False,
            is_completion_required=False,
            completion_url=TEST_DEFAULT_COMPLETION_URL,
        )

    def test_lite(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_LITE_LOGIN,
                    alias_type='lite',
                )
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=False,
            is_completion_required=False,
            completion_url=TEST_DEFAULT_COMPLETION_URL,
        )

    def test_neophonish(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_NEOPHONISH_LOGIN,
                    alias_type='neophonish',
                )
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=False,
            is_completion_required=False,
            completion_url=TEST_DEFAULT_COMPLETION_URL,
        )

    def test_neophonish_without_fio(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_NEOPHONISH_LOGIN,
                    alias_type='neophonish',
                    firstname=None,
                    lastname=None,
                )
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=True,
            is_completion_required=False,
            completion_url=TEST_DEFAULT_COMPLETION_URL,
        )

    def test_completion_postponed_recently(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_NEOPHONISH_LOGIN,
                    alias_type='neophonish',
                    firstname=None,
                    lastname=None,
                )
            ),
        )

        rv = self.make_request(query_args=dict(completion_postponed_at=int(time() - 60)))
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=False,
            is_completion_required=False,
            completion_url=TEST_DEFAULT_COMPLETION_URL,
        )

    def test_custom_tld(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_NEOPHONISH_LOGIN,
                    alias_type='neophonish',
                    firstname=None,
                    lastname=None,
                )
            ),
        )

        rv = self.make_request(query_args=dict(language='en'))
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=True,
            is_completion_required=False,
            completion_url='https:/passport.yandex.com/profile/upgrade',
        )

    def test_ok_for_am(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                **self.get_account_kwargs(
                    login=TEST_NEOPHONISH_LOGIN,
                    alias_type='neophonish',
                    firstname=None,
                    lastname=None,
                )
            ),
        )

        with settings_context(
            MOBILEPROXY_CONSUMER='dev',
            COMPLETION_URL_AM_TEMPLATE='https:/passport.yandex.%(tld)s/am?mode=upgrade',
        ):
            rv = self.make_request()
        self.assert_ok_response(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=True,
            is_completion_required=False,
            completion_url='https:/passport.yandex.ru/am?mode=upgrade',
        )

    def test_both_session_and_token_error(self):
        rv = self.make_request(
            headers=dict(
                authorization=TEST_AUTH_HEADER,
                cookie=TEST_USER_COOKIES,
            ),
        )

        self.assert_error_response(rv, ['request.credentials_several_present'])

    def test_not_xtoken(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                aliases={'phonish': TEST_PHONISH_LOGIN1},
                scope=PDD_PARTNER_OAUTH_TOKEN_SCOPE,
                public_id=TEST_PUBLIC_ID,
            ),
        )

        rv = self.make_request(
            headers=dict(authorization=TEST_AUTH_HEADER, cookie=None),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'])


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
)
class CompleteSubmitTestCase(BaseCompleteTest):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['complete']}))
        self.track_manager = self.env.track_manager.get_manager()

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
                have_password=False,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def make_request(self, headers=None, retpath=TEST_RETPATH, **kwargs):
        data = dict(kwargs, retpath=retpath)

        headers = build_headers() if headers is None else headers
        return self.env.client.post(
            '/1/bundle/complete/submit/?consumer=dev',
            data=data,
            headers=headers,
        )

    def check_ok(self, response, login=TEST_SOCIAL_LOGIN, display_login='', state=None,
                 with_retpath=True, has_recovery_method=None,
                 display_name=None, phone_needs_validation=None,
                 completion_started=None):
        response_data = json.loads(response.data)
        eq_(response_data['status'], 'ok')
        self.track_id = response_data['track_id']

        expected_response = {
            'status': 'ok',
            'account': get_account_info(
                login=login,
                display_login=display_login,
                display_name=display_name,
            ),
            'track_id': self.track_id,
        }
        if with_retpath:
            expected_response['retpath'] = TEST_RETPATH
        if state:
            expected_response['state'] = state
        if has_recovery_method is not None:
            expected_response['has_recovery_method'] = has_recovery_method
        if phone_needs_validation is not None:
            expected_response['phone_needs_validation'] = phone_needs_validation
        if completion_started is not None:
            expected_response['completion_started'] = completion_started

        eq_(response.status_code, 200)

        iterdiff(eq_)(
            response_data,
            expected_response,
        )

        assert_builder_requested(self.env.blackbox)

    def check_response_error(self, response, errors):
        response_data = json.loads(response.data)

        expected_response = {
            'status': 'error',
            'errors': errors,
        }

        eq_(response.status_code, 200)

        for key in expected_response:
            eq_(response_data[key], expected_response[key])

    def check_track(self, retpath=TEST_RETPATH, track_type='complete'):
        track = self.track_manager.read(self.track_id)
        eq_(track.track_type, track_type)
        eq_(track.retpath, retpath)
        eq_(track.uid, str(TEST_UID))

    def test_basic_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=False,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                **self.get_account_kwargs(
                    login=TEST_SOCIAL_LOGIN,
                    alias_type='social',
                    secure=False,
                )
            ),
        )
        rv = self.make_request()
        self.check_ok(
            rv,
            state='complete_social_with_login',
            has_recovery_method=False,
        )
        self.check_track()
        self.assert_blackbox_sessionid_called()

    def test_ok_social_with_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=False,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                **self.get_account_kwargs(
                    login=TEST_LOGIN,
                    secure=False,
                )
            ),
        )

        rv = self.make_request()
        self.check_ok(
            rv,
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
            state='complete_social',
            has_recovery_method=False,
        )
        self.check_track()
        self.assert_blackbox_sessionid_called()

    def test_ok_social_with_login_authorized_by_key(self):
        self.setup_track_for_auth_by_key()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                **self.get_account_kwargs(
                    login=TEST_LOGIN,
                    secure=False,
                )
            ),
        )

        rv = self.make_request(track_id=self.track_id)
        self.check_ok(
            rv,
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
            state='complete_social',
            has_recovery_method=False,
        )
        self.check_track()
        self.assert_blackbox_userinfo_called()

    def test_ok_neophonish(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=False,
                display_name=TEST_NEOPHONISH_DISPLAY_NAME,
                **self.get_account_kwargs(
                    login=TEST_NEOPHONISH_LOGIN,
                    alias_type='neophonish',
                )
            ),
        )

        rv = self.make_request()
        self.check_ok(
            rv,
            login=TEST_NEOPHONISH_LOGIN,
            display_login='',
            display_name=TEST_NEOPHONISH_DISPLAY_NAME,
            state='complete_neophonish',
            has_recovery_method=True,
        )
        self.check_track()
        self.assert_blackbox_sessionid_called()

    def test_ok_unsupported_neophonish(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=False,
                display_name=TEST_NEOPHONISH_DISPLAY_NAME,
                **self.get_account_kwargs(
                    login=TEST_NEOPHONISH_LOGIN,
                    alias_type='neophonish',
                )
            ),
        )

        rv = self.make_request(can_handle_neophonish=False)
        self.check_ok(
            rv,
            login=TEST_NEOPHONISH_LOGIN,
            display_login='',
            display_name=TEST_NEOPHONISH_DISPLAY_NAME,
            state='complete_lite',
            has_recovery_method=True,
        )
        self.check_track()
        self.assert_blackbox_sessionid_called()

    def test_ok_lite(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=True,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                **self.get_account_kwargs(
                    login=TEST_LITE_LOGIN,
                    alias_type='lite',
                    secure=False,
                )
            ),
        )

        rv = self.make_request()
        self.check_ok(
            rv,
            login=TEST_LITE_LOGIN,
            display_login=TEST_LITE_LOGIN,
            state='complete_lite',
            has_recovery_method=False,
        )
        self.check_track()
        self.assert_blackbox_sessionid_called()

    def test_ok_forced_lite_completion(self):
        """Состояние трека после прохождения лайтом восстановления"""
        self.track_id = self.env.track_manager.create_test_track(self.track_manager, 'authorize')
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.is_force_complete_lite = True
            track.uid = TEST_UID
            track.login = TEST_LITE_LOGIN
            track.have_password = True
            track.is_password_passed = True
            track.retpath = TEST_RETPATH

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                **self.get_account_kwargs(
                    login=TEST_LITE_LOGIN,
                    alias_type='lite',
                    phone=None,
                )
            ),
        )

        rv = self.make_request(retpath=None, track_id=self.track_id)
        self.check_ok(
            rv,
            login=TEST_LITE_LOGIN,
            display_login=TEST_LITE_LOGIN,
            state='force_complete_lite',
            has_recovery_method=False,
            with_retpath=False,
        )
        self.check_track(track_type='authorize')
        self.assert_blackbox_userinfo_called()

    def test_ok_user_has_hint_question(self):
        """
        Дорегистрируем lite пользователя с КВ/КО, не требуя
        заводить средства восстановления.
        """
        account_kwargs = self.get_account_kwargs(
            login=TEST_LITE_LOGIN,
            alias_type='lite',
            secure=False,
        )
        account_kwargs = deep_merge(
            account_kwargs,
            {
                'dbfields': {
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=True,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                **account_kwargs
            ),
        )
        rv = self.make_request()
        self.check_ok(
            rv,
            login=TEST_LITE_LOGIN,
            display_login=TEST_LITE_LOGIN,
            state='complete_lite',
            has_recovery_method=True,
        )
        self.check_track()
        self.assert_blackbox_sessionid_called()

    def test_ok_user_has_secure_phone(self):
        """
        Дорегистрируем lite пользователя с защищённым номером телефона,
        не требуя заводить средства восстановления.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=True,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                **self.get_account_kwargs(
                    login=TEST_LITE_LOGIN,
                    alias_type='lite',
                )
            ),
        )
        rv = self.make_request()
        self.check_ok(
            rv,
            login=TEST_LITE_LOGIN,
            display_login=TEST_LITE_LOGIN,
            state='complete_lite',
            has_recovery_method=True,
        )
        self.check_track()
        self.assert_blackbox_sessionid_called()

    def test_2fa_no_password_social_with_login_ok(self):
        """
        Проверяем, что отсутствие пароля + включенный 2FA трактуются как
        наличие пароля и приводят к тому, что нам не надо дорегистрироваться.
        """
        account_kwargs = self.get_account_kwargs(
            login=TEST_LOGIN,
        )
        account_kwargs = deep_merge(
            account_kwargs,
            dict(
                attributes={
                    'account.2fa_on': '1',
                    'password.encrypted': '',
                },
                subscribed_to=[Service.by_slug('social')],
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                **account_kwargs
            ),
        )
        rv = self.make_request()
        self.check_ok(
            rv,
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
        )

    def test_both_session_and_token__error(self):
        rv = self.make_request(
            headers=build_headers(
                authorization=TEST_AUTH_HEADER,
                cookie=TEST_USER_COOKIES,
            ),
        )

        self.check_response_error(rv, ['request.credentials_several_present'])

    def test_socialist_with_token(self):
        """
        Других типов пользователей тоже можно дорегистрировать по токену.
        """
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=X_TOKEN_OAUTH_SCOPE,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                **self.get_account_kwargs(
                    login=TEST_SOCIAL_LOGIN,
                    alias_type='social',
                    phone=None,
                )
            ),
        )

        rv = self.make_request(
            headers=build_headers(authorization=TEST_AUTH_HEADER, cookie=None),
        )

        self.check_ok(
            rv,
            state='complete_social_with_login',
            has_recovery_method=False,
        )

    def test_not_xtoken(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                aliases={'phonish': TEST_PHONISH_LOGIN1},
                scope=PDD_PARTNER_OAUTH_TOKEN_SCOPE,
                public_id=TEST_PUBLIC_ID,
            ),
        )

        rv = self.make_request(
            headers=build_headers(authorization=TEST_AUTH_HEADER, cookie=None),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'])

    def test_without_retpath(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=False,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                **self.get_account_kwargs(
                    login=TEST_SOCIAL_LOGIN,
                    alias_type='social',
                    secure=False,
                )
            ),
        )
        rv = self.make_request(retpath='')
        self.check_ok(
            rv,
            with_retpath=False,
            state='complete_social_with_login',
            has_recovery_method=False,
        )
        self.check_track(retpath=None)
        self.assert_blackbox_sessionid_called()

    def test_without_auth(self):
        expected_error = {
            BLACKBOX_SESSIONID_EXPIRED_STATUS: 'sessionid.invalid',
            BLACKBOX_SESSIONID_NOAUTH_STATUS: 'sessionid.invalid',
            BLACKBOX_SESSIONID_INVALID_STATUS: 'sessionid.invalid',
            BLACKBOX_SESSIONID_DISABLED_STATUS: 'account.disabled',
        }
        for status in expected_error.keys():
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(
                    status=status,
                    have_password=False,
                    display_name=TEST_SOCIAL_DISPLAY_NAME,
                    **self.get_account_kwargs(
                        login=TEST_SOCIAL_LOGIN,
                        alias_type='social',
                        secure=False,
                    )
                ),
            )

            rv = self.make_request()
            self.check_response_error(rv, [expected_error[status]])
            self.assert_blackbox_sessionid_called()

    def test_blackbox_user_is_disabled_on_deletion_error(self):
        account_kwargs = self.get_account_kwargs(
            login=TEST_SOCIAL_LOGIN,
            alias_type='social',
            secure=False,
        )
        account_kwargs = deep_merge(
            account_kwargs,
            dict(
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=False,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                **account_kwargs
            ),
        )

        rv = self.make_request()
        self.check_response_error(rv, ['account.disabled_on_deletion'])
        self.assert_blackbox_sessionid_called()

    def test_action_not_required_complete_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=True,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                **self.get_account_kwargs(login=TEST_LOGIN)
            ),
        )

        rv = self.make_request()
        self.check_ok(rv, login=TEST_LOGIN, display_login=TEST_LOGIN)
        self.assert_blackbox_sessionid_called()

    def test_action_not_required_complete_account_with_lite_session(self):
        """
        Пользователь, не требующий дорегистрации, пришел с lite-кукой.
        Отправляем его на авторизацию с паролем.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                have_password=True,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                is_lite_session=True,
                **self.get_account_kwargs(login=TEST_LOGIN)
            ),
        )

        rv = self.make_request()
        self.check_ok(
            rv,
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
            state='upgrade_cookies',
        )
        self.assert_blackbox_sessionid_called()


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class CompleteSocialTestCase(CompleteCommitTestCaseBase, CommitTestMixin,
                             CommitQuestionTestMixin, ChangePasswordTestMixin,
                             CleanWebTestMixin,
                             CommitSessionTestMixin, CommitBindPhoneTestMixin):
    url_method_name = 'commit_social'
    statbox_type = 'social'

    def build_account(self, account=None, **kwargs):
        account = account or {}
        account = build_social_with_custom_login(account)
        return super(CompleteSocialTestCase, self).build_account(account=account, **kwargs)

    def check_ok(self, response, **kwargs):
        kwargs.setdefault('login', TEST_LOGIN)
        kwargs.setdefault('old_login', TEST_LOGIN)
        kwargs.setdefault('display_login', TEST_LOGIN)
        kwargs.setdefault('login_created', False)
        super(CompleteSocialTestCase, self).check_ok(response, **kwargs)

    def check_response_error(self, response, errors, statbox_call_count=1, **kwargs):
        kwargs.setdefault('login', TEST_LOGIN)
        kwargs.setdefault('display_login', TEST_LOGIN)
        super(CompleteSocialTestCase, self).check_response_error(
            response,
            errors,
            statbox_call_count=statbox_call_count,
            **kwargs
        )

    def test_basic_ok(self):
        self.setup_account()

        rv = self.make_request()

        self.check_ok(rv)

    def test_ok_completed_user(self):
        """
        В дорегистрацию соц пользователя с логином пришёл уже
        дорегистрированный пользователь.
        """
        account = self.build_account(registration_is_complete=True)
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok_action_not_required(
            rv,
            multi=False,
            firstname=u'\\u0414',
            lastname=u'\\u0424',
        )

    def test_ok_completed_user__by_token(self):
        account = self.build_account(registration_is_complete=True)
        self.setup_multi_accounts_by_token(account)

        headers = self.build_headers(
            authorization=TEST_AUTH_HEADER,
            cookie=None,
            host=None,
        )
        rv = self.make_request(headers=headers)

        self.check_ok_action_not_required(
            rv,
            multi=False,
            firstname=u'\\u0414',
            lastname=u'\\u0424',
        )

    def test_error_invalid_user__social_without_login(self):
        """
        В режим дорегистрации соц пользователя с логином нельзя отправить
        социального пользователя без логина и пароля.
        """
        account = build_canonical_social()
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['track.invalid_state'],
            login=TEST_SOCIAL_LOGIN,
            display_login='',
        )

    def test_error_invalid_user__lite(self):
        """
        В режим дорегистрации соц пользователя с логином нельзя отправить
        lite пользователя.
        """
        account = build_lite()
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['track.invalid_state'],
            display_login=TEST_LITE_LOGIN,
            display_name=TEST_LITE_DISPLAY_NAME,
            login=TEST_LITE_LOGIN,
        )

    def test_social_with_strong_password_policy(self):
        """
        Пришел пользователь с is_strong_password_policy_required.
        Проверим, что не получится установить слишком короткий пароль.
        """
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        rv = self.make_request(password='pass')

        self.check_response_error(
            rv,
            ['password.short'],
            display_login=TEST_LOGIN,
            login=TEST_LOGIN,
        )

    def test_2fa_no_password_error(self):
        """
        Проверяем, что отсутствие пароля + включенный 2FA трактуются как
        наличие пароля.
        """
        account = enable_2fa(self.build_account(registration_is_complete=True))
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok_action_not_required(
            rv,
            multi=False,
            firstname=u'\\u0414',
            lastname=u'\\u0424',
        )

    def test_67_sid_basic_ok(self):
        account = self.build_account({'userinfo': {'subscribed_to': [67]}})
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok(
            rv,
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
            login_created=False,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.is_strong_password_policy_required, True)

    def test_ok_social_completed_with_174_attribute(self):
        account = self.build_account()
        account['userinfo']['attributes'] = {
            'person.dont_use_displayname_as_public_name': '1',
        }
        self.setup_account(account)

        rv = self.make_request()
        expected_display_name = TEST_SOCIAL_DISPLAY_NAME.copy()
        expected_display_name['name'] = ''
        del expected_display_name['social']  # аккаунт дорегистрирован и более не социальный

        self.check_ok(
            rv,
            display_name=expected_display_name,
        )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class CompleteSocialWithLoginTestCase(CompleteCommitTestCaseBase,
                                      CommitTestMixin, CommitQuestionTestMixin,
                                      ChangePasswordTestMixin, CommitSessionTestMixin,
                                      CleanWebTestMixin,
                                      CommitBindPhoneTestMixin):
    url_method_name = 'commit_social_with_login'
    statbox_type = 'social-password'

    def build_account(self, account=None, **kwargs):
        account = account or {}
        account = build_canonical_social(account)

        super_object = super(CompleteSocialWithLoginTestCase, self)
        return super_object.build_account(account=account, **kwargs)

    def check_ok(self, response, **kwargs):
        kwargs.setdefault('old_login', TEST_SOCIAL_LOGIN)
        super(CompleteSocialWithLoginTestCase, self).check_ok(response, **kwargs)

    def test_basic_ok(self):
        self.setup_account()

        rv = self.make_request()

        self.check_ok(rv)

    def test_ok_user_defined_login(self):
        account = self.build_account({
            'loginoccupation': {'statuses': {TEST_USER_LOGIN: 'free'}},
        })
        self.setup_account(account)

        rv = self.make_request(login=TEST_USER_LOGIN)

        self.check_ok(rv, login=TEST_USER_LOGIN)

    def test_ok_completed_user(self):
        """
        В дорегистрацию соц пользователя без логина пришёл уже
        дорегистрированный пользователь.
        """
        account = self.build_account(registration_is_complete=True)
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok_action_not_required(
            rv,
            multi=False,
            firstname=u'\\u0414',
            lastname=u'\\u0424',
        )

    def test_error_invalid_user__social_with_login(self):
        """
        В режим дорегистрации соц пользователя без логина нельзя отправить
        социального пользователя с логином и без пароля.
        """
        account = build_social_with_custom_login()
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['track.invalid_state'],
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
        )

    def test_error_invalid_user__lite(self):
        """
        В режим дорегистрации соц пользователя без логина нельзя отправить,
        lite пользователя.
        """
        account = build_lite()
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['track.invalid_state'],
            display_login=TEST_LITE_LOGIN,
            login=TEST_LITE_LOGIN,
            display_name=TEST_LITE_DISPLAY_NAME,
        )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    BLACKBOX_ATTRIBUTES=tuple(),
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class CompleteLiteTestCase(CompleteCommitTestCaseBase, CommitTestMixin,
                           CommitQuestionTestMixin, CommitSessionTestMixin,
                           CleanWebTestMixin,
                           CommitBindPhoneTestMixin):
    url_method_name = 'commit_lite'
    statbox_type = 'lite'

    def setup_multi_accounts(self, incomplete_account, **kwargs):
        super_object = super(CompleteLiteTestCase, self)
        super_object.setup_multi_accounts(
            incomplete_account=incomplete_account,
            **kwargs
        )

        if incomplete_account is not None:
            login_args = deep_merge(
                incomplete_account['userinfo'],
                incomplete_account.get('login', {}),
            )
            self.env.blackbox.set_blackbox_response_value(
                'login',
                blackbox_login_response(**login_args),
            )

    def build_account(self, account=None, has_password=True, has_secure_phone=False, **kwargs):
        account = account or {}
        account = deep_merge(account, {'userinfo': {}})

        if has_secure_phone:
            account['userinfo'] = deep_merge(
                account['userinfo'],
                build_phone_secured(1, TEST_PHONE_NUMBER_OBJECT.e164),
            )

        account = build_lite(account, has_password=has_password)

        super_object = super(CompleteLiteTestCase, self)
        return super_object.build_account(account=account, **kwargs)

    def make_request(self, **kwargs):
        kwargs.setdefault('eula_accepted', True)
        return super(CompleteLiteTestCase, self).make_request(**kwargs)

    def check_ok(self, response, **kwargs):
        kwargs.setdefault('login', TEST_LOGIN)
        kwargs.setdefault('old_login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_name', TEST_LITE_DISPLAY_NAME)
        kwargs.setdefault('had_password', True)
        kwargs.setdefault('display_name_updated', False)
        super(CompleteLiteTestCase, self).check_ok(response, **kwargs)

    def check_response_error(self, response, errors, statbox_call_count=1, **kwargs):
        kwargs.setdefault('login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_name', TEST_LITE_DISPLAY_NAME)
        super(CompleteLiteTestCase, self).check_response_error(
            response,
            errors,
            statbox_call_count=statbox_call_count,
            **kwargs
        )

    def check_frodo(self, **kwargs):
        kwargs.setdefault('with_password', False)
        super(CompleteLiteTestCase, self).check_frodo(**kwargs)

    def test_basic_ok(self):
        self.setup_account()

        rv = self.make_request()

        self.check_ok(rv)

    def test_superlite_ok(self):
        account = self.build_account(has_password=False)
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok(rv, had_password=False)

    def test_ok_user_defined_login(self):
        account = self.build_account({
            'loginoccupation': {'statuses': {TEST_USER_LOGIN: 'free'}},
        })
        self.setup_account(account)

        rv = self.make_request(login=TEST_USER_LOGIN)

        self.check_ok(rv, login=TEST_USER_LOGIN)

    def test_error_no_recovery_method_and_no_validation_method(self):
        """
        У пользователя нет средства восстановления, и не пришло
        validation_method.
        """
        self.setup_account()

        rv = self.make_request(exclude=['validation_method'])

        self.check_response_error(rv, ['user.not_verified'])

    def test_validated_by_phone_is_bruteforce__error(self):
        """
        Пользователь был провалидирован по sms,
        При проверке пароля ЧЯ вернул bruteforce_policy=captcha
        Дополнительно требуем у пользователя ввести капчу, как того требует ЧЯ
        """
        account = self.build_account({
            'login': {'bruteforce_policy': BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS},
        })
        self.setup_account(account)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        rv = self.make_request(validation_method='phone')

        self.check_response_error(rv, ['captcha.required'])

    def test_validated_by_captcha_is_bruteforce__ok(self):
        """
        ЧЯ вернул bruteforce_policy=captcha
        Пользователь уже водил капчу при дорегистрации - пропускаем
        """
        account = self.build_account({
            'login': {'bruteforce_policy': BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS},
        })
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok(rv, captcha_passed=True)

    def test_ok_without_validation_method(self):
        """
        У пользователя есть средство восстановления, поэтому не заводим ему
        средство восстановления.
        """
        account = self.build_account(has_secure_phone=True)
        self.setup_account(account)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False

        rv = self.make_request(validation_method='')

        self.check_ok(rv, captcha_passed=False)

    def test_ok_with_recovery_method_and_validation_passed(self):
        """
        У пользователя есть средство восстановления,
        но по какой-то причине в ручку пришло validation_method=captcha.
        Нужно проигнорировать это и не обновлять КВ/КО.
        """
        account = self.build_account(has_secure_phone=True)
        self.setup_account(account)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False

        rv = self.make_request()

        self.check_ok(rv, captcha_passed=False)

    def test_error_user_has_recovery_method__bruteforce_policy_not(self):
        """
        У пользователя есть средство восстановления, ЧЯ вернул
        bruteforce_policy=captcha. Выбрасываем ошибку.
        """
        account = self.build_account(
            account={
                'login': {
                    'bruteforce_policy': BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
                },
            },
            has_secure_phone=True,
        )
        self.setup_account(account)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False

        rv = self.make_request(validation_method='')

        self.check_response_error(
            rv,
            ['captcha.required'],
        )

    def test_error_wrong_password(self):
        """
        При дорегистрации lite пользователь указал неправильный пароль.
        """
        account = self.build_account(
            account={
                'login': {
                    'password_status': BLACKBOX_PASSWORD_BAD_STATUS,
                },
            },
        )
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['password.not_matched'],
        )

    def test_login_like_password__error(self):
        """
        lite-пользователь хочет выбрать себе портальный логин, совпадающий
        с его действующим паролем -- ошибка.
        """
        self.setup_account()

        rv = self.make_request(login=TEST_LOGIN, password=TEST_LOGIN)

        self.check_response_error(rv, errors=['login.like_password'])

    def test_login_like_password_after_normalization__error(self):
        """
        При сравнении нового логина и действующего пароля происходит
        нормализация.
        """
        login_user_wants = 'test.password-1'
        password_user_have = 'test-password.1'
        account = self.build_account(
            account={
                'loginoccupation': {'statuses': {login_user_wants: 'free'}},
            },
        )
        self.setup_account(account)

        rv = self.make_request(
            login=login_user_wants,
            password=password_user_have,
        )

        self.check_response_error(rv, errors=['login.like_password'])

    def test_error_eula_not_accepted(self):
        """
        При дорегистрации lite пользователь не принял ПС.
        """
        self.setup_account()

        rv = self.make_request(eula_accepted=False)

        self.check_response_error(rv, ['eula_accepted.not_accepted'])

    def test_ok_completed_user(self):
        """
        В дорегистрацию lite пользователя пришёл уже дорегистрированный
        пользователь.
        """
        account = self.build_account(registration_is_complete=True)
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok_action_not_required(
            rv,
            multi=False,
            display_name=TEST_LITE_DISPLAY_NAME,
            firstname=u'\\u0414',
            lastname=u'\\u0424',
        )

    def test_error_invalid_user__social_without_login(self):
        """
        В дорегистрацию lite пользователя пришёл соц пользователь без логина.
        """
        account = build_canonical_social()
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['track.invalid_state'],
            login=TEST_SOCIAL_LOGIN,
            display_login='',
            display_name=TEST_SOCIAL_DISPLAY_NAME,
        )

    def test_error_invalid_user__social_with_login(self):
        """
        В дорегистрацию lite пользователя пришёл соц пользователь с логином.
        """
        account = build_social_with_custom_login()
        self.setup_account(account)

        rv = self.make_request()

        self.check_response_error(
            rv,
            ['track.invalid_state'],
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
            display_name=TEST_SOCIAL_DISPLAY_NAME,
        )

    def test_commit__blackbox_unexpected_response__error(self):
        """
        ЧЯ вернул что-то странное при запросе в метод login, то, чего
        возвращать он никак не должен. Проверим, что корректно отработаем
        данную ситуацию.
        """
        self.setup_account()
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

        rv = self.make_request()

        self.check_response_error(rv, ['backend.blackbox_permanent_error'])


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    BLACKBOX_ATTRIBUTES=tuple(),
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class ForceCompleteLiteTestCase(CompleteCommitTestCaseBase, CommitTestMixin,
                                CleanWebTestMixin,
                                CommitQuestionTestMixin, CommitBindPhoneTestMixin):
    url_method_name = 'force_commit_lite'
    statbox_type = 'lite'
    track_type = 'authorize'
    authentication_media = 'password'

    def setUp(self):
        super(ForceCompleteLiteTestCase, self).setUp()
        self.setup_track()
        self.setup_statbox_templates()

    def build_account(self, account=None, **kwargs):
        account = account or {}
        account = build_lite(account)
        super_object = super(ForceCompleteLiteTestCase, self)
        return super_object.build_account(account=account, **kwargs)

    def check_ok(self, response, **kwargs):
        kwargs.setdefault('login', TEST_LOGIN)
        kwargs.setdefault('old_login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_name', TEST_LITE_DISPLAY_NAME)
        kwargs.setdefault('had_password', True)
        kwargs.setdefault('password_sent', False)
        kwargs.setdefault('display_name_updated', False)
        super(ForceCompleteLiteTestCase, self).check_ok(response, **kwargs)

    def check_response_error(self, response, errors, **kwargs):
        kwargs.setdefault('login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_login', TEST_LITE_LOGIN)
        kwargs.setdefault('display_name', TEST_LITE_DISPLAY_NAME)
        super(ForceCompleteLiteTestCase, self).check_response_error(
            response,
            errors,
            **kwargs
        )

    def check_frodo(self, **kwargs):
        kwargs.setdefault('with_password', False)
        kwargs.setdefault('password_sent', False)
        super(ForceCompleteLiteTestCase, self).check_frodo(**kwargs)

    def make_request(self, **kwargs):
        kwargs.setdefault('eula_accepted', True)
        return super(ForceCompleteLiteTestCase, self).make_request(**kwargs)

    def initial_track_data(self):
        return dict(
            retpath=TEST_RETPATH,
            is_force_complete_lite=True,
            is_password_passed=True,
            password_hash=get_sha256_hash(TEST_PASSWORD),
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL,
            user_entered_login=TEST_LITE_LOGIN,
            uid=TEST_UID,
            login=TEST_LITE_LOGIN,
            have_password=True,
            human_readable_login=TEST_LITE_LOGIN,
            machine_readable_login=TEST_LITE_LOGIN,
            is_captcha_checked=True,
            is_captcha_recognized=True,
        )

    def setup_track(self, track_data=None):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        track_data = track_data or self.initial_track_data()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for field_name, value in track_data.items():
                setattr(track, field_name, value)

    def assert_blackbox_sessionid_called(self, **kwargs):
        kwargs.setdefault('sessionid_index', 1)
        kwargs.setdefault('with_sslsession', False)
        kwargs.setdefault('is_extended', False)
        super(ForceCompleteLiteTestCase, self).assert_blackbox_sessionid_called(**kwargs)

    def test_basic_ok(self):
        self.setup_account()

        rv = self.make_request()

        self.check_ok(rv)

    def test_invalid_track_state_error(self):
        """Пришел лайт, но непонятно откуда"""
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_force_complete_lite = False

        resp = self.make_request(with_password=False)
        self.assert_error_response(resp, ['track.invalid_state'], check_content=False)
        eq_(self.env.blackbox.request.call_count, 2)
        self.assert_blackbox_userinfo_called()
        self.assert_blackbox_sessionid_called()
        self.assert_statbox_has_written([self.env.statbox.entry('check_cookies')])

    def test_login_like_password(self):
        account = self.build_account({
            'loginoccupation': {'statuses': {TEST_PASSWORD: 'free'}},
        })
        self.setup_account(account)

        rv = self.make_request(login=TEST_PASSWORD)

        self.check_response_error(rv, errors=['login.like_password'])

    def test_normalized_login_like_password(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.password_hash = get_sha256_hash(TEST_PASSWORD_LIKE_NORMALIZED_LOGIN)

        account = self.build_account({
            'loginoccupation': {'statuses': {TEST_LOGIN_FOR_NORMALIZATION: 'free'}},
        })
        self.setup_account(account)

        rv = self.make_request(login=TEST_LOGIN_FOR_NORMALIZATION)

        self.check_response_error(rv, errors=['login.like_password'])

    def test_eula_not_accepted(self):
        self.setup_account()
        rv = self.make_request(eula_accepted=False)
        self.check_response_error(rv, ['eula_accepted.not_accepted'])

    def test_no_uid_in_track(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.uid = None

        self.setup_account()
        rv = self.make_request()
        self.check_response_error(rv, ['track.invalid_state'], with_account=False, statbox_call_count=0)

    def test_already_registered_with_invalid_session_ok(self):
        """
        В дорегистрацию lite пользователя пришёл уже дорегистрированный
        пользователь с невалидной кукой.
        """
        account = self.build_account(
            {'sessionid': {'status': BLACKBOX_SESSIONID_INVALID_STATUS}},
            registration_is_complete=True,
        )
        self.setup_account(account)

        rv = self.make_request()

        self.check_ok_action_not_required(
            rv,
            multi=False,
            display_name=TEST_LITE_DISPLAY_NAME,
            firstname=u'\\u0414',
            lastname=u'\\u0424',
        )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    BLACKBOX_ATTRIBUTES=tuple(),
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class CompleteNeophonishTestCase(CompleteCommitTestCaseBase, CommitTestMixin):
    url_method_name = 'commit_neophonish'
    statbox_type = 'neophonish'

    def setUp(self):
        super(CompleteNeophonishTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

    def build_account(self, account=None, **kwargs):
        account = build_neophonish(account)
        return super(CompleteNeophonishTestCase, self).build_account(account=account, **kwargs)

    def check_ok(self, response, **kwargs):
        kwargs.setdefault('login', TEST_LOGIN)
        kwargs.setdefault('old_login', TEST_NEOPHONISH_LOGIN)
        kwargs.setdefault('display_name', TEST_NEOPHONISH_DISPLAY_NAME)
        kwargs.setdefault('had_password', False)
        kwargs.setdefault('captcha_passed', False)
        kwargs.setdefault('validated_via', 'phone')
        kwargs.setdefault('display_name_updated', False)
        super(CompleteNeophonishTestCase, self).check_ok(response, **kwargs)

        # Проверим, что сняли с привязанного телефона флаг should_ignore_binding_limit
        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = False
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=TEST_UID,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': TEST_PHONE_NUMBER_OBJECT.e164,
            },
            binding_flags=binding_flags,
        )

    def check_response_error(self, response, errors, **kwargs):
        kwargs.setdefault('login', TEST_NEOPHONISH_LOGIN)
        kwargs.setdefault('display_name', TEST_NEOPHONISH_DISPLAY_NAME)
        super(CompleteNeophonishTestCase, self).check_response_error(
            response,
            errors,
            **kwargs
        )

    def test_basic_ok(self):
        self.setup_account()

        rv = self.make_request()

        self.check_ok(rv)

    def test_ok_user_defined_login(self):
        account = self.build_account({
            'loginoccupation': {'statuses': {TEST_USER_LOGIN: 'free'}},
        })
        self.setup_account(account)

        rv = self.make_request(login=TEST_USER_LOGIN)

        self.check_ok(rv, login=TEST_USER_LOGIN)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    BLACKBOX_ATTRIBUTES=tuple(),
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class CompleteNeophonishAsLiteTestCase(CompleteCommitTestCaseBase):
    """Неофонишным аккаунтом идём в лайтовый флоу (из старого АМ, не умеющего неофонишей)"""
    url_method_name = 'commit_lite'
    statbox_type = 'lite'

    def setUp(self):
        super(CompleteNeophonishAsLiteTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

    def make_request(self, **kwargs):
        kwargs.setdefault('eula_accepted', True)
        return super(CompleteNeophonishAsLiteTestCase, self).make_request(**kwargs)

    def build_account(self, account=None, **kwargs):
        account = build_neophonish(account)
        return super(CompleteNeophonishAsLiteTestCase, self).build_account(account=account, **kwargs)

    def check_ok(self, response, **kwargs):
        kwargs.setdefault('login', TEST_LOGIN)
        kwargs.setdefault('old_login', TEST_NEOPHONISH_LOGIN)
        kwargs.setdefault('display_login', '')
        kwargs.setdefault('display_name', TEST_NEOPHONISH_DISPLAY_NAME)
        kwargs.setdefault('had_password', False)
        kwargs.setdefault('captcha_passed', False)
        kwargs.setdefault('display_name_updated', False)
        return super(CompleteNeophonishAsLiteTestCase, self).check_ok(response, **kwargs)

    def test_ok(self):
        self.setup_account()
        rv = self.make_request()
        self.check_ok(rv)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class CompleteSocialTestCaseNoBlackboxHash(CompleteSocialTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class CompleteSocialWithLoginTestCaseNoBlackboxHash(CompleteSocialWithLoginTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class CompleteLiteTestCaseNoBlackboxHash(CompleteLiteTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class ForceCompleteLiteTestCaseNoBlackboxHash(ForceCompleteLiteTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
