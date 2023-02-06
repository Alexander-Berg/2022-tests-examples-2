# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_IP,
    TEST_LOGIN,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.types.login.login import masked_login


TEST_USER_AGENT = 'com.yandex.mobile.auth.sdk/4.30.2744 (TCT ALCATEL ONE TOUCH 7025D; Android 4.2.1)'
TEST_LOCATION = u'Фэрфилд'
TEST_DEVICE_NAME = u'Почта на айфоне %<b>'
TEST_ESCAPED_DEVICE_NAME = u'Почта на айфоне &amp;#37;&lt;b&gt;'


class SendChallengeNotificationsTestcase(BaseBundleTestViews, EmailTestMixin):

    default_url = '/1/bundle/auth/password/challenge/send_email/?consumer=dev'
    http_method = 'POST'
    http_query_args = dict(
        uid=TEST_UID,
        device_name=TEST_DEVICE_NAME,
    )
    http_headers = dict(
        user_ip=TEST_IP,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['challenge.send_email'])
        self.setup_blackbox_response()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_response(self):
        bb_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            bb_response,
        )

    def check_emails_sent(self, location=TEST_LOCATION, browser=None, device_name=TEST_ESCAPED_DEVICE_NAME):
        self.assert_emails_sent([
            self.build_email(
                address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
                is_native=False,
                location=location,
                browser=browser,
                device_name=device_name,
            ),
            self.build_email(
                address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
                is_native=True,
                location=location,
                browser=browser,
                device_name=device_name,
            ),
        ])

    def check_blackbox_call(self):
        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_UID,
            'emails': 'getall',
        })

    def build_email(self, address, location, browser, device_name, login=TEST_LOGIN, is_native=False):
        data = {
            'language': 'ru',
            'addresses': [address],
            'subject': 'auth_challenge.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': u'\\u0414'},
                'auth_challenge.notice': {
                    'MASKED_LOGIN': login if is_native else masked_login(login),
                },
                'auth_challenge.if_hacked.with_url': {
                    'SUPPORT_URL': '<a href=\'https://yandex.ru/support/passport/troubleshooting/hacked.html\'>https://yandex.ru/support/passport/troubleshooting/hacked.html</a>',
                },
                'auth_challenge.journal.with_url': {
                    'JOURNAL_URL': '<a href=\'https://passport.yandex.ru/profile/journal\'>https://passport.yandex.ru/profile/journal</a>',
                },
                'signature.secure': {},
            },
        }
        if location or browser:
            data['tanker_keys']['auth_challenge.we_know'] = {}
        if location:
            data['tanker_keys']['user_meta_data.location'] = {
                'LOCATION': location,
            }
        if browser:
            data['tanker_keys']['user_meta_data.browser'] = {
                'BROWSER': browser,
            }
        if device_name:
            data['tanker_keys']['auth_challenge.device_name'] = {
                'DEVICE_NAME': device_name,
            }
        return data

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, email_sent=True)
        self.check_emails_sent()
        self.check_blackbox_call()

    def test_ok_without_device_name(self):
        rv = self.make_request(exclude_args=['device_name'])
        self.assert_ok_response(rv, email_sent=True)
        self.check_emails_sent(device_name=None)
        self.check_blackbox_call()
