# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.builders.perimeter_api.exceptions import (
    PerimeterApiPermanentError,
    PerimeterApiTemporaryError,
)
from passport.backend.core.builders.perimeter_api.faker import perimeter_recreate_totp_secret_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 1
TEST_LOGIN = 'login'
TEST_SECRET_BINARY = '\xff\xff\xff\xff'
TEST_SECRET_BASE32 = '777777Y'
TEST_SECRET_SERIALIZED = '1://///w'
TEST_ISSUER = 'yandex-team'
TEST_TOTP_URL = 'otpauth://totp/{issuer}:{login}?secret={secret}&issuer={issuer}'.format(
    issuer=TEST_ISSUER,
    login=TEST_LOGIN,
    secret=TEST_SECRET_BASE32,
)


@with_settings_hosts(
    PERIMETER_API_URL='http://localhost/',
    PERIMETER_API_TIMEOUT=0.5,
    PERIMETER_API_RETRIES=10,
    PERIMETER_API_CLIENT_CERT='',
    PERIMETER_API_CLIENT_CERT_KEY='',
    RFC_OTP_ISSUER=TEST_ISSUER,
    DOMAIN_KEYSPACES=(
        ('yandex-team.ru', 'yandex-team.ru'),
    )
)
class RecreateRfcOtpSecretTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/rfc_otp/recreate_secret/?consumer=dev'
    http_method = 'POST'
    http_headers = {
        'host': 'passport.yandex-team.ru',
        'cookie': 'Session_id=foo',
        'user_ip': '3.3.3.3',
        'user_agent': 'curl',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'rfc_otp': ['recreate_secret']}))

        self.setup_blackbox()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox(self, login=TEST_LOGIN, has_password=True):
        attrs = {'account.rfc_2fa_on': '1'}
        if has_password:
            attrs['password.encrypted'] = '1:passwd'
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=login,
                attributes=attrs,
            ),
        )

    def test_ok(self):
        self.env.perimeter_api.set_response_value(
            'recreate_totp_secret',
            perimeter_recreate_totp_secret_response(TEST_SECRET_BASE32),
        )
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            secret=TEST_SECRET_BASE32,
            totp_url=TEST_TOTP_URL,
        )

    def test_ok_2(self):
        self.setup_blackbox('another login')
        self.env.perimeter_api.set_response_value(
            'recreate_totp_secret',
            perimeter_recreate_totp_secret_response('another secret'),
        )
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            secret='another secret',
            totp_url='otpauth://totp/yandex-team:another%20login?secret=another%20secret&issuer=yandex-team',
        )

    def test_no_password(self):
        self.setup_blackbox(has_password=False)
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['account.without_password'])

    def test_perimeter_permanent_error(self):
        self.env.perimeter_api.set_response_side_effect(
            'recreate_totp_secret',
            PerimeterApiPermanentError,
        )
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['backend.perimeter_api_permanent_error'])

    def test_perimeter_temporary_error(self):
        self.env.perimeter_api.set_response_side_effect(
            'recreate_totp_secret',
            PerimeterApiTemporaryError,
        )
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['backend.perimeter_api_failed'])
