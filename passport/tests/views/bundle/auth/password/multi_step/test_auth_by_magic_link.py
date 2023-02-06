# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.social_api.faker.social_api import get_profiles_response
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.counters import (
    magic_link_per_ip_counter,
    magic_link_per_uid_counter,
)
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import bytes_to_hex
from passport.backend.utils.time import datetime_to_integer_unixtime

from .base import BaseMultiStepTestcase
from .base_test_data import (
    COOKIE_L_VALUE,
    COOKIE_LAH_VALUE,
    COOKIE_YP_VALUE,
    COOKIE_YS_VALUE,
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    MDA2_BEACON_VALUE,
    TEST_ACCEPT_LANGUAGE,
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_DOMAIN,
    TEST_FRETPATH,
    TEST_HOST,
    TEST_IP,
    TEST_LANGUAGE,
    TEST_LOGIN,
    TEST_MODEL_CONFIGS,
    TEST_ORIGIN,
    TEST_OTHER_UID,
    TEST_PDD_LOGIN,
    TEST_PDD_RETPATH,
    TEST_PDD_UID,
    TEST_PROFILE_BAD_ESTIMATE,
    TEST_RAW_ENV_FOR_PROFILE,
    TEST_REFERER,
    TEST_RETPATH,
    TEST_RUSSIAN_IP,
    TEST_SERVICE,
    TEST_TRACK_ID,
    TEST_UID,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_YANDEXUID_COOKIE,
)


TEST_MAGIC_LINK_RANDOM_BYTES = b'1' * 10
TEST_UUID4_RANDOM_BYTES = b'1' * 16
TEST_MAGIC_LINK_SECRET_KEY = bytes_to_hex(TEST_MAGIC_LINK_RANDOM_BYTES)
TEST_MAGIC_LINK_SECRET = '%s%x' % (TEST_MAGIC_LINK_SECRET_KEY, TEST_UID)
TEST_AUTH_MAGIC_LINK_TEMPLATE = 'http://passport.{tld}/magic-link-confirm-auth/?{query_string}'
TEST_EMAIL = '@'.join([TEST_LOGIN, 'yandex.ru'])
TEST_BROWSER = u'ChromeMobile 48.0.2564 (Android Marshmallow)'
TEST_LOCATION = u'Яндекс (Москва)'
TEST_LOCATION_EN = u'Yandex (Moscow)'
TEST_MAGIC_LINK_CODE_LENGTH = 3
TEST_CODE = '3' * TEST_MAGIC_LINK_CODE_LENGTH
TEST_MESSAGE_ID = '123'


@with_settings_hosts(
    ALLOW_MAGIC_LINK=True,
    AUTH_MAGIC_LINK_CONFIRMS_LIMIT=2,
    AUTH_MAGIC_LINK_TTL=600,
    AUTH_MAGIC_LINK_TEMPLATE=TEST_AUTH_MAGIC_LINK_TEMPLATE,
    MAGIC_LINK_CODE_LENGTH=TEST_MAGIC_LINK_CODE_LENGTH,
    BOT_API_URL='http://bot-api/',
    BOT_API_TIMEOUT=1,
    BOT_API_RETRIES=2,
    BOT_API_TOKEN='test',
    **mock_counters()
)
class TestAuthByMagicLinkSendTestCase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/magic_link/submit/'
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_RUSSIAN_IP,
        'cookie': 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'referer': TEST_REFERER,
    }
    http_query_args = {
        'track_id': TEST_TRACK_ID,
    }
    statbox_type = 'multi_step_magic_link'

    def setUp(self):
        super(TestAuthByMagicLinkSendTestCase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.urandom_mock = mock.Mock(return_value=TEST_MAGIC_LINK_RANDOM_BYTES)
        self.urandom_patch = mock.patch('os.urandom', self.urandom_mock)
        self.patches.append(self.urandom_patch)
        self.urandom_patch.start()

        self.confirmation_code = TEST_CODE

        self._code_generator_faker = CodeGeneratorFaker()
        self._code_generator_faker.set_return_value(self.confirmation_code)
        self._code_generator_faker.start()
        self.setup_statbox_templates()

    def tearDown(self):
        self._code_generator_faker.stop()
        del self._code_generator_faker
        del self.urandom_patch
        del self.urandom_mock
        del self.track_id
        super(TestAuthByMagicLinkSendTestCase, self).tearDown()

    def setup_statbox_templates(self):
        super(TestAuthByMagicLinkSendTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'magic_link_sent',
            _exclude=['origin', 'input_login'],
            mode='any_auth',
            action='send_magic_link_email',
            input_login=TEST_LOGIN,
            address=mask_email_for_statbox(TEST_EMAIL),
            magic_link_confirms_count='0',
            uid=str(TEST_UID),
            step='submit',
            is_new_link='1',
        )
        self.env.statbox.bind_entry(
            'bot_api_error',
            _exclude=['origin', 'input_login'],
            mode='any_auth',
            status='error',
            error='bot_api.request_failed',
            input_login=TEST_LOGIN,
            uid=str(TEST_UID),
            step='submit',
        )

    def build_email(self, address, magic_link=None, language=TEST_ACCEPT_LANGUAGE, browser=TEST_BROWSER):
        tld = 'com.tr' if language == 'tr' else language
        data = {
            'language': language,
            'addresses': [address],
            'MAGIC_LINK': magic_link,
            'subject': 'emails.magic_link_sent.title',
            'tanker_keys': {
                'magic_link_logo_url': {},
                'greeting': {'FIRST_NAME': '\u0414'},
                'emails.magic_link_sent.title': {},
                'emails.magic_link_sent.start': {
                    'MASKED_LOGIN': TEST_LOGIN,
                    'BROWSER': browser,
                },
                'emails.magic_link_sent.login': {},
                'emails.magic_link_sent.security': {},
                'signature.secure': {},
                'emails.magic_link_feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://yandex.{}/support/passport/feedback.html\' target=\'_blank\'>'.format(tld),
                    'FEEDBACK_URL_END': '</a>',
                },
            },
        }
        return data

    def assert_track_ok(self, location=TEST_LOCATION, uid=TEST_UID, send_to='email', require_auth_for_confirm=False,
                        message_id=None):
        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.magic_link_secret, '%s%x' % (TEST_MAGIC_LINK_SECRET_KEY, uid))
        ok_(track.magic_link_sent_time is not None)
        eq_(track.magic_link_start_location, location)
        eq_(track.magic_link_start_browser, TEST_BROWSER)
        eq_(track.magic_link_send_to, send_to)
        eq_(track.magic_link_message_id, message_id)
        eq_(bool(track.require_auth_for_magic_link_confirm), require_auth_for_confirm)

    def assert_mail_sent(self, email=TEST_EMAIL, secret=TEST_MAGIC_LINK_SECRET, language=TEST_LANGUAGE):
        self.assert_emails_sent([
            self.build_email(
                language=language,
                address=email,
                magic_link=TEST_AUTH_MAGIC_LINK_TEMPLATE.format(
                    tld='ru',
                    query_string='secret=%s&track_id=%s' % (secret, TEST_TRACK_ID),
                ),
            ),
        ])

    def setup_track(self, start_time=None, confirmed=False, with_secret=False,
                    invalidated=False, uid=TEST_UID, secret=None, omit_start_time=False):
        with self.track_transaction(self.track_id) as track:
            track.uid = uid
            if not omit_start_time:
                track.magic_link_start_time = start_time or datetime_to_integer_unixtime(datetime.now())
            if confirmed:
                track.magic_link_confirm_time = datetime_to_integer_unixtime(datetime.now())
            if with_secret:
                track.magic_link_sent_time = datetime_to_integer_unixtime(datetime.now())
                track.magic_link_secret = secret or TEST_MAGIC_LINK_SECRET
                track.magic_link_start_location = TEST_LOCATION
                track.magic_link_start_browser = TEST_BROWSER
                track.magic_link_code = TEST_CODE

            if invalidated:
                track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())

    def test_sent__ok(self):
        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        self.setup_track()
        resp = self.make_request()
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok()
        self.assert_mail_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_sent__no_start_time__ok(self):
        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        self.setup_track(omit_start_time=True)
        resp = self.make_request()
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok()
        self.assert_mail_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_counters_exceeded__error(self):
        self.setup_track()
        for _ in range(10):
            magic_link_per_uid_counter.incr(TEST_UID)

        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['rate.limit_exceeded'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_ip_counter_exceeded__error(self):
        self.setup_track()
        counter = magic_link_per_ip_counter.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)

        resp = self.make_request(headers={'user_ip': TEST_USER_IP})
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_already_confirmed__error(self):
        self.setup_track(confirmed=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_track_expired_renewed__ok(self):
        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        long_ago = datetime_to_integer_unixtime(datetime.now() - timedelta(seconds=1000))
        self.setup_track(start_time=long_ago)
        resp = self.make_request()
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok()
        self.assert_mail_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_track_with_link__ok(self):
        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        self.setup_track(with_secret=True)
        resp = self.make_request()
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok()
        self.assert_mail_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent', is_new_link='0'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_confirms_exceeded__error(self):
        self.setup_track()
        with self.track_transaction(self.track_id) as track:
            for _ in range(3):
                track.magic_link_confirms_count.incr()
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_email_disappeared__error(self):
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_strong_policy__error(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
            subscribed_to=[67],
        )
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_incomplete_pdd__error(self):
        self.setup_blackbox_responses(
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            emails=[self.env.email_toolkit.create_native_email('test-user', TEST_DOMAIN)],
        )
        self.setup_track()
        resp = self.make_request(query_args={'retpath': TEST_PDD_RETPATH})
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_autoregistered__error(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.100': 1,
                'subscription.suid.100': 1,
            },
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_force_change_password__error(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 5,
                'subscription.suid.100': 1,
            },
            subscribed_to=[8],
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            password_change_required=True,
        )
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_no_location(self):
        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        self.setup_track()
        resp = self.make_request(headers={'user_ip': '127.0.0.1'})
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok(location=u'Земля')
        self.assert_mail_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent', is_new_link='1', ip='127.0.0.1'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_link_invalidated__error(self):
        self.setup_track(invalidated=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_resend_with_different_account(self):
        self.setup_blackbox_responses(
            uid=TEST_UID2,
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(uid=TEST_UID2, with_secret=True)
        resp = self.make_request()
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok(uid=TEST_UID2)
        self.assert_mail_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent', uid=str(TEST_UID2)),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_resend_with_invalid_secret(self):
        self.setup_blackbox_responses(
            uid=TEST_UID2,
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(uid=TEST_UID2, with_secret=True, secret='notasecret')
        resp = self.make_request()
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok(uid=TEST_UID2)
        self.assert_mail_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent', uid=str(TEST_UID2)),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_language_used(self):
        self.setup_blackbox_responses(
            language='tr',
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track()
        resp = self.make_request()
        self.assert_ok_response(resp, code=TEST_CODE)
        self.assert_track_ok(location=TEST_LOCATION_EN)
        self.assert_mail_sent(language='tr')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('magic_link_sent'),
        ])
        self.assert_antifraud_auth_fail_not_written()


@with_settings_hosts(
    ALLOW_MAGIC_LINK=True,
    AUTH_MAGIC_LINK_CONFIRMS_LIMIT=2,
    AUTH_MAGIC_LINK_TTL=600,
    AUTH_MAGIC_LINK_TEMPLATE=TEST_AUTH_MAGIC_LINK_TEMPLATE,
    BOT_API_URL='http://bot-api/',
    BOT_API_TIMEOUT=1,
    BOT_API_RETRIES=2,
    BOT_API_TOKEN='test',
    **mock_counters(
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UID_COUNTER=(1, 600, 10),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_IP_COUNTER=(1, 600, 10),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UNTRUSTED_IP_COUNTER=(1, 600, 3),
    )
)
class TestAuthByMagicLinkConfirmTestCase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/magic_link/commit/'
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_IP,
        'cookie': 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'referer': TEST_REFERER,
    }
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'secret': TEST_MAGIC_LINK_SECRET,
    }
    statbox_type = 'multi_step_magic_link'

    def setUp(self):
        super(TestAuthByMagicLinkConfirmTestCase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.setup_statbox_templates()

    def tearDown(self):
        del self.track_id
        super(TestAuthByMagicLinkConfirmTestCase, self).tearDown()

    def setup_statbox_templates(self):
        super(TestAuthByMagicLinkConfirmTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'error',
            _exclude=['origin'],
            mode='any_auth',
            step='confirm_link',
            error='magic_link.invalid',
            uid=str(TEST_UID),
            ip=TEST_IP,
            send_to='email',
        )
        self.env.statbox.bind_entry(
            'ok',
            _exclude=['origin'],
            mode='any_auth',
            step='confirm_link',
            uid=str(TEST_UID),
            status='ok',
            ip=TEST_IP,
            send_to='email',
        )
        self.env.statbox.bind_entry(
            'confirm_email',
            _exclude=['origin'],
            action='send_magic_link_confirm_email',
            address=mask_email_for_statbox(TEST_EMAIL),
            step='confirm_link',
            mode='any_auth',
            ip=TEST_IP,
            uid=str(TEST_UID),
            send_to='email',
        )

    def setup_track(self, start_time=None, confirmed=False, sent_time=None, uid=TEST_UID,
                    invalidated=False, send_to='email', retpath=TEST_RETPATH, require_auth=False):
        with self.track_transaction(self.track_id) as track:
            track.uid = uid
            track.magic_link_start_time = start_time or datetime_to_integer_unixtime(datetime.now())
            track.magic_link_sent_time = sent_time
            track.magic_link_secret = '%s%x' % (TEST_MAGIC_LINK_SECRET_KEY, uid) if uid else None
            if confirmed:
                track.magic_link_confirm_time = datetime_to_integer_unixtime(datetime.now())

            if invalidated:
                track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())

            track.magic_link_code = TEST_CODE
            track.magic_link_start_browser = TEST_BROWSER
            track.magic_link_start_location = TEST_LOCATION
            track.magic_link_send_to = send_to
            track.retpath = retpath

            track.require_auth_for_magic_link_confirm = require_auth

    def build_email(self, address, login=TEST_LOGIN, language=TEST_LANGUAGE):
        tld = 'com.tr' if language == 'tr' else language
        return {
            'language': language,
            'addresses': [address],
            'subject': 'emails.magic_link_confirmed.title',
            'tanker_keys': {
                'magic_link_logo_url': {},
                'greeting': {'FIRST_NAME': '\u0414'},
                'emails.magic_link_confirmed.in': {
                    'MASKED_LOGIN': login,
                },
                'emails.magic_link_confirmed.device': {
                    'BROWSER': TEST_BROWSER,
                },
                'emails.magic_link_confirmed.security': {
                    'RESTORE_URL_BEGIN': '<a href=\'https://passport.yandex.{}/restoration\' target=\'_blank\'>'.format(tld),
                    'RESTORE_URL_END': '</a>',
                },
                'signature.secure': {},
                'emails.magic_link_feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://yandex.{}/support/passport/feedback.html\' target=\'_blank\'>'.format(tld),
                    'FEEDBACK_URL_END': '</a>',
                },
            },
        }

    def assert_track_ok(self, uid=TEST_UID):
        track = self.track_manager.read(self.track_id)
        ok_(track.magic_link_confirm_time is not None)
        eq_(track.auth_method, 'magic_link')
        eq_(track.uid, str(uid))
        ok_(not track.is_password_passed)
        ok_(not track.allow_authorization)
        ok_(not track.allow_oauth_authorization)

    def test_invalid_track_state__error(self):
        self.setup_track(uid=None)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()
        self.assert_antifraud_auth_fail_not_written()

    def test_confirmed__ok(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_ok_response(resp, track_id=TEST_TRACK_ID)
        self.assert_track_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('ok'),
            self.env.statbox.entry('confirm_email'),
        ])
        self.assert_emails_sent([
            self.build_email(address='%s@%s' % (TEST_LOGIN, 'yandex.ru')),
        ])
        self.assert_antifraud_auth_fail_not_written()
        self.assert_antifraud_auth_fail_not_written()

    def test_with_redirect__ok(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request(query_args=dict(redirect=True))
        self.assert_ok_response(resp, track_id=TEST_TRACK_ID, retpath=TEST_RETPATH)
        self.assert_track_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('ok'),
            self.env.statbox.entry('confirm_email'),
        ])
        self.assert_emails_sent([
            self.build_email(address='%s@%s' % (TEST_LOGIN, 'yandex.ru')),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_pdd__ok(self):
        self.setup_blackbox_responses(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, TEST_DOMAIN)],
            subscribed_to=[102],
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            uid=TEST_PDD_UID,
        )
        resp = self.make_request(query_args={'secret': '%s%x' % (TEST_MAGIC_LINK_SECRET_KEY, TEST_PDD_UID)})
        self.assert_ok_response(resp, track_id=TEST_TRACK_ID)
        self.assert_track_ok(uid=TEST_PDD_UID)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('ok', uid=str(TEST_PDD_UID)),
            self.env.statbox.entry(
                'confirm_email',
                uid=str(TEST_PDD_UID),
                address=mask_email_for_statbox(TEST_PDD_LOGIN),
            ),
        ])
        self.assert_emails_sent([
            self.build_email(address=TEST_PDD_LOGIN, login=TEST_PDD_LOGIN),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__with_session__ok(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request(headers=dict(cookie='Session_id=foo;'))
        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__with_token__ok(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request(headers=dict(authorization='OAuth foo'))
        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__sessionid_invalid__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request(headers=dict(cookie='Session_id=foo;'))
        self.assert_error_response(resp, ['sessionid.invalid'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__token_invalid__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request(headers=dict(authorization='OAuth foo'))
        self.assert_error_response(resp, ['oauth_token.invalid'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__sessionid_uid_mismatch__error(self):
        self.setup_blackbox_responses(uid=TEST_OTHER_UID)
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request(headers=dict(cookie='Session_id=foo;'))
        self.assert_error_response(resp, ['sessionid.no_uid'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__token_uid_mismatch__error(self):
        self.setup_blackbox_responses(uid=TEST_OTHER_UID)
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request(headers=dict(authorization='OAuth foo'))
        self.assert_error_response(resp, ['account.uid_mismatch'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__no_credentials__error(self):
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['request.credentials_all_missing'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_strong_policy__error(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
            subscribed_to=[67],
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(
            comment='multi_step_magic_link/magic_link_not_allowed',
            _exclude=['AS'], ip=TEST_IP,
        )

    def test_not_sent__error(self):
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.not_sent'], track_id=TEST_TRACK_ID)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_already_confirmed__error(self):
        self.setup_track(confirmed=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'], track_id=TEST_TRACK_ID)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_secret_not_matched__error(self):
        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request(query_args={'secret': '%s%x' % (TEST_MAGIC_LINK_SECRET_KEY, TEST_OTHER_UID)})
        self.assert_error_response(resp, ['magic_link.secret_not_matched'], track_id=self.track_id)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('error'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_incomplete_pdd__error(self):
        self.setup_blackbox_responses(
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            emails=[self.env.email_toolkit.create_native_email('test-user', TEST_DOMAIN)],
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            uid=TEST_PDD_UID,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(
            comment='multi_step_magic_link/magic_link_not_allowed',
            _exclude=['AS'], ip=TEST_IP,
        )

    def test_autoregistered__error(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.100': 1,
                'subscription.suid.100': 1,
            },
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(
            comment='multi_step_magic_link/magic_link_not_allowed',
            _exclude=['AS'], ip=TEST_IP,
        )

    def test_force_change_password__error(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 5,
                'subscription.suid.100': 1,
            },
            subscribed_to=[8],
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            password_change_required=True,
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_written(
            comment='multi_step_magic_link/magic_link_not_allowed',
            _exclude=['AS'], ip=TEST_IP,
        )

    def test_link_invalidated__error(self):
        self.setup_track(invalidated=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_no_tz__ok(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request(headers={'user_ip': '127.0.0.1'})
        self.assert_ok_response(resp, track_id=TEST_TRACK_ID)
        self.assert_track_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('ok', ip='127.0.0.1'),
            self.env.statbox.entry('confirm_email', ip='127.0.0.1'),
        ])
        self.assert_emails_sent([
            self.build_email(address='%s@%s' % (TEST_LOGIN, 'yandex.ru')),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_language_used(self):
        self.setup_blackbox_responses(
            language='tr',
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_ok_response(resp, track_id=TEST_TRACK_ID)
        self.assert_track_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('ok'),
            self.env.statbox.entry('confirm_email'),
        ])
        self.assert_antifraud_auth_fail_not_written()


@with_settings_hosts(
    ALLOW_MAGIC_LINK=True,
    AUTH_MAGIC_LINK_CONFIRMS_LIMIT=2,
    AUTH_MAGIC_LINK_TTL=600,
    **mock_counters(
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_IP_COUNTER=(1, 600, 10),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UNTRUSTED_IP_COUNTER=(1, 600, 3),
    )
)
class TestAuthByMagicLinkConfirmRegistrationTestCase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/magic_link/commit_registration/'
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_IP,
        'cookie': 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'referer': TEST_REFERER,
    }
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'secret': TEST_MAGIC_LINK_SECRET_KEY,
    }
    statbox_type = 'multi_step_magic_link'

    def setUp(self):
        super(TestAuthByMagicLinkConfirmRegistrationTestCase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.setup_statbox_templates()

    def tearDown(self):
        del self.track_id
        super(TestAuthByMagicLinkConfirmRegistrationTestCase, self).tearDown()

    def setup_statbox_templates(self):
        super(TestAuthByMagicLinkConfirmRegistrationTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'error',
            _exclude=['origin'],
            mode='any_auth',
            step='confirm_link',
            error='magic_link.invalid',
            ip=TEST_IP,
            send_to='email',
        )
        self.env.statbox.bind_entry(
            'ok',
            _exclude=['origin'],
            mode='any_auth',
            step='confirm_link',
            status='ok',
            ip=TEST_IP,
            send_to='email',
        )

    def setup_track(self, start_time=None, confirmed=False, sent_time=None,
                    invalidated=False, send_to='email', magic_link_code=None):
        with self.track_transaction(self.track_id) as track:
            track.magic_link_start_time = start_time or datetime_to_integer_unixtime(datetime.now())
            track.magic_link_sent_time = sent_time
            track.magic_link_secret = TEST_MAGIC_LINK_SECRET_KEY
            if confirmed:
                track.magic_link_confirm_time = datetime_to_integer_unixtime(datetime.now())

            if invalidated:
                track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())

            track.magic_link_code = magic_link_code
            track.magic_link_start_browser = TEST_BROWSER
            track.magic_link_start_location = TEST_LOCATION
            track.magic_link_send_to = send_to
            track.retpath = TEST_RETPATH

    def assert_track_ok(self, uid=TEST_UID):
        track = self.track_manager.read(self.track_id)
        ok_(track.magic_link_confirm_time is not None)

    def test_confirmed__ok(self):
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_ok_response(resp, track_id=TEST_TRACK_ID)
        self.assert_track_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('ok'),
        ])

    def test_with_redirect__ok(self):
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request(query_args=dict(redirect=True))
        self.assert_ok_response(resp, track_id=TEST_TRACK_ID, retpath=TEST_RETPATH)
        self.assert_track_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('ok'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_not_sent__error(self):
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.not_sent'], track_id=TEST_TRACK_ID)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_already_confirmed__error(self):
        self.setup_track(confirmed=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'], track_id=TEST_TRACK_ID)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()

    def test_secret_not_matched__error(self):
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request(query_args={'secret': 'a' * 20})
        self.assert_error_response(resp, ['magic_link.secret_not_matched'], track_id=self.track_id)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('error'),
        ])
        self.assert_antifraud_auth_fail_written(
            comment='multi_step_magic_link/magic_link_invalid',
            _exclude=['AS', 'uid'], ip=TEST_IP,
        )

    def test_link_invalidated__error(self):
        self.setup_track(invalidated=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])
        self.assert_antifraud_auth_fail_not_written()


@with_settings_hosts(
    ALLOW_MAGIC_LINK=True,
    AUTH_MAGIC_LINK_CONFIRMS_LIMIT=2,
    AUTH_MAGIC_LINK_TTL=600,
    AUTH_MAGIC_LINK_TEMPLATE=TEST_AUTH_MAGIC_LINK_TEMPLATE,
    BLACKBOX_URL='localhost',
    YABS_URL='localhost',
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    TENSORNET_API_URL='http://tensornet:80/',
    WEB_PROFILE_DISTANCE_THRESHOLD=50,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    FORCED_CHALLENGE_CHANCE=0.0,
    FORCED_CHALLENGE_PERIOD_LENGTH=3600,
    YDB_PERCENTAGE=0,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    **mock_counters(
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UID_COUNTER=(1, 600, 10),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_IP_COUNTER=(1, 600, 10),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UNTRUSTED_IP_COUNTER=(1, 600, 3),
    )
)
class TestAuthByMagicLinkStatusTestCase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/magic_link/status/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
    }
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_IP,
        'cookie': 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'referer': TEST_REFERER,
    }
    http_method = 'GET'
    statbox_type = 'multi_step_magic_link'

    def setUp(self):
        super(TestAuthByMagicLinkStatusTestCase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.confirmation_code = TEST_CODE

        self._code_generator_faker = CodeGeneratorFaker()
        self._code_generator_faker.set_return_value(self.confirmation_code)
        self._code_generator_faker.start()
        self.setup_statbox_templates()

    def tearDown(self):
        self._code_generator_faker.stop()
        del self._code_generator_faker
        del self.track_id
        super(TestAuthByMagicLinkStatusTestCase, self).tearDown()

    def setup_statbox_templates(self):
        super(TestAuthByMagicLinkStatusTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'passed',
            _exclude=['origin'],
            mode='any_auth',
            step='confirmed',
            action='passed',
            start_time=TimeNow(),
            sent_time=TimeNow(),
            confirm_time=TimeNow(),
            confirms_count='1',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _exclude=[
                'is_fresh_profile_passed',
                'is_model_passed',
                'origin',
                'tensornet_estimate',
                'tensornet_model',
                'tensornet_status',
            ],
            af_action='ALLOW',
            af_is_auth_forbidden='0',
            af_is_challenge_required='1',
            af_reason='some-reason',
            af_tags='email_hint',
            current=self.make_user_profile(raw_env=TEST_RAW_ENV_FOR_PROFILE).as_json,
            decision_source='antifraud_api',
            ip=TEST_IP,
            is_challenge_required='1',
            is_fresh_account='0',
            is_mobile='0',
            is_model_passed='0',
            kind='ufo',
            type='multi_step_magic_link',
            ufo_distance='0',
            step='confirmed',
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            _exclude=['origin'],
            ip=TEST_IP,
            decision_source='ufo',
            step='confirmed',
            kind='ufo',
            is_mobile='0',
        )
        self.env.statbox.bind_entry(
            'auth_notification',
            _exclude=['origin'],
            _inherit_from='local_base',
            action='auth_notification',
            consumer='dev',
            counter_exceeded='0',
            email_sent='1',
            ip=TEST_IP,
            step='confirmed',
            uid=str(TEST_UID),
        )

    def setup_track(self, start_time=None, confirmed=False, sent_time=None, invalidated=False, captcha_required=False):
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.magic_link_start_time = start_time or datetime_to_integer_unixtime(datetime.now())
            track.magic_link_sent_time = sent_time
            track.magic_link_secret = TEST_MAGIC_LINK_SECRET
            if captcha_required:
                track.is_captcha_required = True
            if confirmed:
                track.magic_link_confirm_time = datetime_to_integer_unixtime(datetime.now())

            if invalidated:
                track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())

            track.magic_link_code = TEST_CODE

    def assert_cached_in_track(self, cached_resp, status='ok'):
        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            dict(
                cached_resp,
                status=status,
            ),
        )

    def test_confirmed__ok(self):
        self.setup_track(confirmed=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())
        resp = self.make_request()
        self.assert_ok_response(resp, magic_link_confirmed=True, track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_not_confirmed__ok(self):
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_ok_response(resp, magic_link_confirmed=False, track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_track_invalid_state__error(self):
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.not_sent'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_register_track(self):
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_show_antifraud_challenge(self):
        self.setup_blackbox_responses(
            emails=[
                self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
            ],
        )
        self.setup_track(confirmed=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        self.setup_profile_responses(ufo_items=[], estimate=TEST_PROFILE_BAD_ESTIMATE)
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_hint']))

        resp = self.make_request()
        expected_resp = dict(
            state='auth_challenge',
            account=self.account_response_values(),
            track_id=self.track_id,
            magic_link_confirmed=True,
        )
        self.assert_ok_response(
            resp,
            **expected_resp
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                decision_source='antifraud_api',
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_cached_in_track(expected_resp)
        self.assert_antifraud_auth_fail_not_written()

    def test_captcha_required(self):
        self.setup_blackbox_responses(
            emails=[
                self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        self.setup_track(confirmed=True, sent_time=datetime_to_integer_unixtime(datetime.now()))

        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['call', 'email_hint'],
        ))

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            track_id=self.track_id,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_tags='call email_hint',
                is_challenge_required='1',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                decision_source='antifraud_api',
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        expected = {
            'errors': ['captcha.required'],
            'track_id': self.track_id,
        }
        self.assert_cached_in_track(expected, status='error')
        self.assert_antifraud_auth_fail_not_written()

    def test_captcha_already_required__error(self):
        self.setup_track(captcha_required=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['captcha.required'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_link_invalidated__error(self):
        self.setup_track(invalidated=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'], track_id=self.track_id)
        self.assert_antifraud_auth_fail_not_written()


@with_settings_hosts(
    ALLOW_MAGIC_LINK=True,
    AUTH_MAGIC_LINK_TTL=600,
    GET_AVATAR_URL=TEST_AVATAR_URL_TEMPLATE,
)
class TestAuthByMagicLinkInfoView(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/magic_link/info/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'avatar_size': 'islands-75',
    }
    http_method = 'GET'
    statbox_type = 'multi_step_magic_link'

    def setUp(self):
        super(TestAuthByMagicLinkInfoView, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

    def tearDown(self):
        del self.track_id
        super(TestAuthByMagicLinkInfoView, self).tearDown()

    def setup_track(self, sent_time=None, uid=TEST_UID, invalidated=False, code=TEST_CODE, require_auth=False):
        with self.track_transaction(self.track_id) as track:
            track.uid = uid
            track.user_entered_login = TEST_EMAIL
            track.magic_link_start_time = datetime_to_integer_unixtime(datetime.now())
            track.magic_link_sent_time = sent_time
            track.magic_link_secret = TEST_MAGIC_LINK_SECRET
            track.magic_link_start_browser = TEST_BROWSER
            track.magic_link_start_location = TEST_LOCATION

            if invalidated:
                track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())
            track.magic_link_code = code

            track.require_auth_for_magic_link_confirm = require_auth

    def test_ok(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
            display_name=TEST_DISPLAY_NAME_DATA,
            avatar_key=TEST_AVATAR_KEY,
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            start_time=TimeNow(),
            code=TEST_CODE,
            location=TEST_LOCATION,
            browser=TEST_BROWSER,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'islands-75'),
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_for_register_track(self):
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.setup_track(
            uid=None,
            code=None,
            sent_time=datetime_to_integer_unixtime(datetime.now()),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            start_time=TimeNow(),
            location=TEST_LOCATION,
            browser=TEST_BROWSER,
            login=TEST_EMAIL,
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_with_session(self):
        self.setup_blackbox_responses(
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
            display_name=TEST_DISPLAY_NAME_DATA,
            avatar_key=TEST_AVATAR_KEY,
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            start_time=TimeNow(),
            code=TEST_CODE,
            location=TEST_LOCATION,
            browser=TEST_BROWSER,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'islands-75'),
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_required__error(self):
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            require_auth=True,
        )
        resp = self.make_request(headers=dict(cookie='yandexuid=foo;'))
        self.assert_error_response(resp, ['request.credentials_all_missing'])
        self.assert_antifraud_auth_fail_not_written()

    def test_not_sent__error(self):
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.not_sent'])
        self.assert_antifraud_auth_fail_not_written()

    def test_restore_track_error(self):
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_antifraud_auth_fail_not_written()

    def test_incomplete_pdd__error(self):
        self.setup_blackbox_responses(
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            emails=[self.env.email_toolkit.create_native_email('test-user', TEST_DOMAIN)],
        )
        self.setup_track(
            sent_time=datetime_to_integer_unixtime(datetime.now()),
            uid=TEST_PDD_UID,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_autoregistered__error(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.100': 1,
                'subscription.suid.100': 1,
            },
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_force_change_password__error(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 5,
                'subscription.suid.100': 1,
            },
            subscribed_to=[8],
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            password_change_required=True,
        )
        self.setup_track(sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_antifraud_auth_fail_written(comment='multi_step_magic_link/magic_link_not_allowed')

    def test_link_invalidated__error(self):
        self.setup_track(invalidated=True, sent_time=datetime_to_integer_unixtime(datetime.now()))
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'])
        self.assert_antifraud_auth_fail_not_written()


class TestAuthByMagicLinkInvalidateView(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/magic_link/invalidate/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
    }
    http_method = 'POST'
    statbox_type = 'multi_step_magic_link'

    def setUp(self):
        super(TestAuthByMagicLinkInvalidateView, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.setup_statbox_templates()

    def tearDown(self):
        del self.track_id
        super(TestAuthByMagicLinkInvalidateView, self).tearDown()

    def setup_statbox_templates(self):
        super(TestAuthByMagicLinkInvalidateView, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'invalidate',
            _exclude=['origin'],
            action='invalidate',
            sent_time=TimeNow(),
            start_time=TimeNow(),
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'bot_api_error',
            _exclude=['origin'],
            status='error',
            error='bot_api.request_failed',
            uid=str(TEST_UID),
        )

    def setup_track(self, invalidate=False, uid=TEST_UID, magic_link_code=TEST_CODE, send_to='email'):
        with self.track_transaction(self.track_id) as track:
            track.uid = uid
            track.magic_link_start_time = datetime_to_integer_unixtime(datetime.now()) - 10
            track.magic_link_sent_time = datetime_to_integer_unixtime(datetime.now()) - 9
            track.magic_link_secret = TEST_MAGIC_LINK_SECRET
            if invalidate:
                track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())
            track.magic_link_code = magic_link_code
            track.magic_link_send_to = send_to
            track.require_auth_for_magic_link_confirm = True  # это поле не влияет на данную ручку

    def test_ok(self):
        self.setup_track()
        resp = self.make_request()
        self.assert_ok_response(resp)
        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.magic_link_invalidate_time, TimeNow())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('invalidate'),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_already_invalidated(self):
        self.setup_track(invalidate=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'])
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_for_registration_track(self):
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.setup_track(uid=None, magic_link_code=None)
        resp = self.make_request()
        self.assert_ok_response(resp)
        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.magic_link_invalidate_time, TimeNow())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('invalidate', _exclude=['uid']),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_wrong_track(self):
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('complete')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_antifraud_auth_fail_not_written()


@with_settings_hosts(
    ALLOW_MAGIC_LINK=True,
    AUTH_MAGIC_LINK_CONFIRMS_LIMIT=2,
    AUTH_MAGIC_LINK_TTL=600,
    AUTH_MAGIC_LINK_TEMPLATE=TEST_AUTH_MAGIC_LINK_TEMPLATE,
    MAGIC_LINK_CODE_LENGTH=TEST_MAGIC_LINK_CODE_LENGTH,
    PASSPORT_SUBDOMAIN='passport-test',
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
    **mock_counters()
)
class TestMultiStepMagicLinkIntegrationalTestCase(BaseMultiStepTestcase):
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_RUSSIAN_IP,
        'cookie': 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'referer': TEST_REFERER,
    }

    def setUp(self):
        super(TestMultiStepMagicLinkIntegrationalTestCase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        self.urandom_mock = mock.Mock(side_effect=[TEST_UUID4_RANDOM_BYTES, TEST_MAGIC_LINK_RANDOM_BYTES])
        self.urandom_patch = mock.patch('os.urandom', self.urandom_mock)
        self.patches.append(self.urandom_patch)
        self.urandom_patch.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base'], 'session': ['create']}))
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([]),
        )

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self.cookies_patches = [
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
            ),
            mock.patch.object(
                cookie_y.SessionCookieY,
                'pack',
                self._cookie_ys_pack,
            ),
            mock.patch.object(
                cookie_y.PermanentCookieY,
                'pack',
                self._cookie_yp_pack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ]
        self.confirmation_code = TEST_CODE

        self._code_generator_faker = CodeGeneratorFaker()
        self._code_generator_faker.set_return_value(self.confirmation_code)
        self._code_generator_faker.start()

        for patch in self.cookies_patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.cookies_patches):
            patch.stop()
        self._code_generator_faker.stop()
        del self._cookie_l_pack
        del self._cookie_ys_pack
        del self._cookie_lah_pack
        del self._cookie_yp_pack
        del self.cookies_patches
        del self._code_generator_faker

        del self.urandom_patch
        del self.urandom_mock
        del self.track_id
        super(TestMultiStepMagicLinkIntegrationalTestCase, self).tearDown()

    def start(self):
        url = '/1/bundle/auth/password/multi_step/start/'
        http_query_args = {
            'retpath': TEST_RETPATH,
            'service': TEST_SERVICE,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
            'login': TEST_LOGIN,
        }
        resp = self.make_request(url, query_args=http_query_args)
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            primary_alias_type=1,
            can_authorize=True,
            auth_methods=['password', 'magic_link', 'magic_x_token'],
            csrf_token='csrf',
            preferred_auth_method='password',
            magic_link_email='@'.join([TEST_LOGIN, 'yandex.ru']),
            use_new_suggest_by_phone=False,
        )

    def submit(self):
        url = '/1/bundle/auth/password/multi_step/magic_link/submit/'
        resp = self.make_request(url, query_args={'track_id': self.track_id, 'language': TEST_LANGUAGE})
        self.assert_ok_response(resp, code=TEST_CODE)

    def status(self, confirmed):
        url = '/1/bundle/auth/password/multi_step/magic_link/status/'
        resp = self.make_request(url, method='GET', query_args={'track_id': self.track_id})
        self.assert_ok_response(resp, magic_link_confirmed=confirmed, track_id=self.track_id)

    def commit(self):
        url = '/1/bundle/auth/password/multi_step/magic_link/commit/'
        resp = self.make_request(
            url,
            query_args={'track_id': self.track_id, 'secret': TEST_MAGIC_LINK_SECRET, 'language': TEST_LANGUAGE},
        )
        self.assert_ok_response(resp, track_id=self.track_id)

    def session(self):
        url = '/1/bundle/session/'
        resp = self.make_request(url, query_args={'track_id': self.track_id})
        cookies = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
            EXPECTED_LAH_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            cookies=sorted(cookies),
            default_uid=TEST_UID,
        )

    def test__ok(self):
        self.start()
        self.submit()
        self.status(confirmed=False)
        self.commit()
        self.status(confirmed=True)
        self.session()
