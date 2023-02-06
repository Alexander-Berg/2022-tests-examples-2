# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

import mock
from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_AUTH_MAGIC_LINK_TEMPLATE,
    TEST_DEVICE_NAME,
    TEST_ESCAPED_DEVICE_NAME,
    TEST_EXTERNAL_EMAIL,
    TEST_LOCATION,
    TEST_MAGIC_LINK_RANDOM_BYTES,
    TEST_MAGIC_LINK_SECRET,
    TEST_MAGIC_LINK_SECRET_WITH_UID,
    TEST_NATIVE_EMAIL,
    TEST_REGISTER_MAGIC_LINK_TEMPLATE,
    TEST_USER_IP,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_KEY,
    TEST_DISPLAY_NAME_DATA,
    TEST_LOGIN,
    TEST_PASSWORD_HASH,
    TEST_RETPATH,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.counters import (
    magic_link_per_ip_counter,
    magic_link_per_uid_counter,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_MODEL = 'iPhone M'
TEST_MAGIC_LINK_TTL = 1200
TEST_POLL_INTERVAL = 5


@nottest
@with_settings_hosts(
    ALLOW_MAGIC_LINK=True,
    AUTH_MAGIC_LINK_CONFIRMS_LIMIT=2,
    AUTH_MAGIC_LINK_POLL_INTERVAL=TEST_POLL_INTERVAL,
    AUTH_MAGIC_LINK_TTL=TEST_MAGIC_LINK_TTL,
    AUTH_MAGIC_LINK_TEMPLATE=TEST_AUTH_MAGIC_LINK_TEMPLATE,
    REGISTER_MAGIC_LINK_TEMPLATE=TEST_REGISTER_MAGIC_LINK_TEMPLATE,
    **mock_counters()
)
class BaseMagicLinkSendTestcase(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/mobile/magic_link/send/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }
    http_query_args = {
        'retpath': TEST_RETPATH,
    }
    track_type = None

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.urandom_mock = mock.Mock(return_value=TEST_MAGIC_LINK_RANDOM_BYTES)
        self.urandom_patch = mock.patch('os.urandom', self.urandom_mock)
        self.urandom_patch.start()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.device_name = TEST_DEVICE_NAME
            track.language = 'ru'

        self.http_query_args.update(track_id=self.track_id)

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['magic_link']},
            ),
        )

    def tearDown(self):
        self.urandom_patch.stop()
        self.env.stop()
        del self.track_manager
        del self.urandom_patch
        del self.urandom_mock
        del self.env

    def assert_track_ok(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover

    def assert_mail_sent(self, email=TEST_NATIVE_EMAIL, secret=TEST_MAGIC_LINK_SECRET):
        raise NotImplementedError()  # pragma: no cover

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        self.assert_track_ok()
        self.assert_mail_sent()

    def test_without_device_name__ok(self):
        with self.track_transaction(self.track_id) as track:
            track.device_name = None
            track.device_hardware_model = TEST_MODEL

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        self.assert_track_ok(device_name=TEST_MODEL)
        self.assert_mail_sent(device_name=TEST_MODEL)

    def test_ip_counter_exceeded__error(self):
        counter = magic_link_per_ip_counter.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)

        resp = self.make_request(headers={'user_ip': TEST_USER_IP})
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_no_emails_sent()

    def test_already_confirmed__error(self):
        with self.track_transaction(self.track_id) as track:
            track.magic_link_confirm_time = datetime_to_integer_unixtime(datetime.now())

        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'])
        self.assert_no_emails_sent()

    def test_track_expired_renewed__ok(self):
        long_ago = datetime_to_integer_unixtime(datetime.now() - timedelta(seconds=1000))
        with self.track_transaction(self.track_id) as track:
            track.magic_link_start_time = long_ago

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        self.assert_track_ok()
        self.assert_mail_sent()

    def test_confirms_exceeded__error(self):
        with self.track_transaction(self.track_id) as track:
            for _ in range(3):
                track.magic_link_confirms_count.incr()

        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_no_emails_sent()

    def test_no_location(self):
        resp = self.make_request(headers={'user_ip': '127.0.0.1'})
        self.assert_ok_response(
            resp,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        self.assert_track_ok(location=u'Земля')
        self.assert_mail_sent()

    def test_link_invalidated__error(self):
        with self.track_transaction(self.track_id) as track:
            track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())

        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'])
        self.assert_no_emails_sent()


@istest
class TestMagicLinkSendForAuth(BaseMagicLinkSendTestcase):
    track_type = 'authorize'

    def setUp(self):
        super(TestMagicLinkSendForAuth, self).setUp()
        with self.track_transaction(self.track_id) as track:
            track.magic_link_start_time = datetime_to_integer_unixtime(datetime.now())
            track.uid = TEST_UID

        self.setup_blackbox_userinfo_response()

    def setup_blackbox_userinfo_response(self, account_type='portal', with_native_email=True, with_external_email=False,
                                         **kwargs):
        emails = []
        if with_native_email:
            emails.append(self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'))
        elif with_external_email:
            emails.append(self.env.email_toolkit.create_validated_external_email(TEST_LOGIN, 'gmail.com', default=True))

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    account_type: TEST_LOGIN,
                },
                display_name=TEST_DISPLAY_NAME_DATA,
                default_avatar_key=TEST_AVATAR_KEY,
                is_avatar_empty=True,
                crypt_password=TEST_PASSWORD_HASH,
                emails=emails,
                **kwargs
            ),
        )

    def build_email(self, language, address, magic_link, device_name):
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
                    'BROWSER': device_name,
                },
                'emails.magic_link_sent.login': {},
                'emails.magic_link_sent.security': {},
                'signature.secure': {},
                'emails.magic_link_feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/feedback.html\' target=\'_blank\'>',
                    'FEEDBACK_URL_END': '</a>',
                },
            },
        }
        return data

    def assert_mail_sent(self, language='ru', email=TEST_NATIVE_EMAIL, tld='ru',
                         secret=TEST_MAGIC_LINK_SECRET, device_name=TEST_ESCAPED_DEVICE_NAME):
        self.assert_emails_sent([
            self.build_email(
                language=language,
                address=email,
                magic_link=TEST_AUTH_MAGIC_LINK_TEMPLATE.format(
                    tld=tld,
                    query_string='secret=%s&track_id=%s&redirect=true' % (secret, self.track_id),
                ),
                device_name=device_name,
            ),
        ])

    def assert_track_ok(self, device_name=TEST_DEVICE_NAME, location=TEST_LOCATION):
        track = self.track_manager.read(self.track_id)
        eq_(track.magic_link_secret, TEST_MAGIC_LINK_SECRET_WITH_UID)
        eq_(track.magic_link_sent_time, TimeNow())
        eq_(track.magic_link_start_location, location)
        eq_(track.magic_link_start_browser, device_name)
        eq_(track.magic_link_send_to, 'email')
        eq_(track.retpath, TEST_RETPATH)

    def test_ok_for_custom_language(self):
        self.setup_blackbox_userinfo_response(language='uk')
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        self.assert_track_ok(location=u'Ферфілд')
        self.assert_mail_sent(language='uk', tld='ua')

    def test_ok_for_external_email(self):
        self.setup_blackbox_userinfo_response(account_type='lite', with_native_email=False, with_external_email=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        self.assert_track_ok()
        self.assert_mail_sent(email=TEST_EXTERNAL_EMAIL)

    def test_action_impossible_error(self):
        self.setup_blackbox_userinfo_response(with_native_email=False, with_external_email=True)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['action.impossible'])
        self.assert_no_emails_sent()

    def test_uid_counter_exceeded__error(self):
        for _ in range(10):
            magic_link_per_uid_counter.incr(TEST_UID)

        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['rate.limit_exceeded'])
        self.assert_no_emails_sent()

    def test_force_change_password__error(self):
        self.setup_blackbox_userinfo_response(
            dbfields={
                'subscription.login_rule.8': 5,
                'subscription.suid.100': 1,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            subscribed_to=[8],
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])
        self.assert_no_emails_sent()


@istest
class TestMagicLinkSendForRegistration(BaseMagicLinkSendTestcase):
    track_type = 'register'

    def setUp(self):
        super(TestMagicLinkSendForRegistration, self).setUp()
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_EXTERNAL_EMAIL

    def build_email(self, address, magic_link, device_name):
        data = {
            'language': 'ru',
            'addresses': [address],
            'MAGIC_LINK': magic_link,
            'subject': 'emails.magic_link_for_registration_sent.title',
            'tanker_keys': {
                'magic_link_logo_url': {},
                'greeting.noname': {},
                'emails.magic_link_for_registration_sent.title': {},
                'emails.magic_link_for_registration_sent.start': {
                    'EMAIL': address,
                    'DEVICE_NAME': device_name,
                },
                'emails.magic_link_for_registration_sent.confirm': {},
                'emails.magic_link_for_registration_sent.security': {},
                'emails.magic_link_for_registration_sent.signature': {},
                'emails.magic_link_feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/feedback.html\' target=\'_blank\'>',
                    'FEEDBACK_URL_END': '</a>',
                },
            },
        }
        return data

    def assert_mail_sent(self, email=TEST_EXTERNAL_EMAIL, secret=TEST_MAGIC_LINK_SECRET, device_name=TEST_ESCAPED_DEVICE_NAME):
        self.assert_emails_sent([
            self.build_email(
                address=email,
                magic_link=TEST_REGISTER_MAGIC_LINK_TEMPLATE.format(
                    tld='ru',
                    query_string='secret=%s&track_id=%s&redirect=true' % (secret, self.track_id),
                ),
                device_name=device_name,
            ),
        ])

    def assert_track_ok(self, device_name=TEST_DEVICE_NAME, location=TEST_LOCATION):
        track = self.track_manager.read(self.track_id)
        eq_(track.magic_link_secret, TEST_MAGIC_LINK_SECRET)
        eq_(track.magic_link_sent_time, TimeNow())
        eq_(track.magic_link_start_location, location)
        eq_(track.magic_link_start_browser, device_name)
        eq_(track.magic_link_send_to, 'email')
        eq_(track.retpath, TEST_RETPATH)

    def test_invalid_email_in_track__error(self):
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_no_emails_sent()


@with_settings_hosts(
    MOBILE_LITE_DATA_STATUS_DEFAULT={
        'name': 'not_used',
        'phone_number': 'not_used',
        'password': 'not_used',
    },
    MOBILE_LITE_DATA_STATUS_BY_APP_ID_PREFIX={},
)
class MagicLinkStatusTestcase(BaseBundleTestViews):
    default_url = '/1/bundle/mobile/magic_link/status/'
    consumer = 'dev'
    http_method = 'GET'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.create_and_setup_track()

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['magic_link']},
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.track_manager
        del self.env

    def create_and_setup_track(self, track_type='authorize', link_age=10,
                               is_sent=True, is_confirmed=False, is_invalidated=False):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(track_type)
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.magic_link_start_time = datetime_to_integer_unixtime(datetime.now() - timedelta(seconds=link_age))
            if is_sent:
                track.magic_link_sent_time = datetime_to_integer_unixtime(datetime.now())
            if is_confirmed:
                track.magic_link_confirm_time = datetime_to_integer_unixtime(datetime.now())
            if is_invalidated:
                track.magic_link_invalidate_time = datetime_to_integer_unixtime(datetime.now())

        self.http_query_args.update(track_id=self.track_id)

    def test_not_confirmed__ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            magic_link_confirmed=False,
        )

    def test_confirmed__ok(self):
        self.create_and_setup_track(is_confirmed=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            magic_link_confirmed=True,
        )

    def test_confirmed_for_registration__ok(self):
        self.create_and_setup_track(is_confirmed=True, track_type='register')
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            magic_link_confirmed=True,
            lite_data_necessity={
                'name': 'not_used',
                'password': 'not_used',
                'phone_number': 'not_used',
            },
        )

    def test_not_sent__error(self):
        self.create_and_setup_track(is_sent=False)

        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.not_sent'])

    def test_track_expired__error(self):
        self.create_and_setup_track(link_age=1000)

        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.expired'])

    def test_link_invalidated__error(self):
        self.create_and_setup_track(is_invalidated=True)

        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.invalidated'])
