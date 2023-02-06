# -*- coding: utf-8 -*-
import mock
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 1
TEST_LOGIN = 'login'
TEST_SECRET_BINARY = b'\xff\xff\xff\xff'
TEST_SECRET_BASE32 = '777777Y'
TEST_SECRET_SERIALIZED = '1://///w'


@with_settings_hosts()
class BaseManageRfcOtpTestcase(BaseBundleTestViews):
    http_method = 'POST'
    http_query_args = {
        'login': TEST_LOGIN,
    }
    http_headers = {
        'user_agent': 'curl',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'rfc_otp': ['manage']}))
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox(self, uid=TEST_UID, rfc_2fa_on=False, has_password=True):
        attrs = {}
        if rfc_2fa_on:
            attrs['account.rfc_2fa_on'] = '1'
        if has_password:
            attrs['password.encrypted'] = '1:passwd'
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                login=TEST_LOGIN,
                attributes=attrs,
            ),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            user_agent='curl',
            uid=str(TEST_UID),
            consumer='dev',
            ip='127.0.0.1',
            login=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'enabled',
            mode='rfc_otp',
            action='enabled',
        )
        self.env.statbox.bind_entry(
            'disabled',
            mode='rfc_otp',
            action='disabled',
        )


class TestEnableRfcOtp(BaseManageRfcOtpTestcase):
    default_url = '/1/bundle/rfc_otp/enable/?consumer=dev'

    def setUp(self):
        super(TestEnableRfcOtp, self).setUp()
        self.urandom_patch = mock.patch(
            'os.urandom',
            mock.Mock(return_value=TEST_SECRET_BINARY),
        )
        self.urandom_patch.start()

    def tearDown(self):
        self.urandom_patch.stop()
        del self.urandom_patch
        super(TestEnableRfcOtp, self).tearDown()

    def test_ok(self):
        self.setup_blackbox(rfc_2fa_on=False)
        resp = self.make_request()
        self.assert_ok_response(resp, secret=TEST_SECRET_BASE32)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check(
            'attributes',
            'account.rfc_totp.secret',
            TEST_SECRET_SERIALIZED,
            uid=TEST_UID,
            db='passportdbshard1',
        )
        self.env.event_logger.assert_events_are_logged(
            {
                'action': 'enable_rfc_otp',
                'info.rfc_totp': 'enabled',
                'user_agent': 'curl',
            },
        )
        self.env.statbox.assert_has_written(self.env.statbox.entry('enabled'))

    def test_already_on(self):
        # Всё равно перезаписываем секрет
        self.setup_blackbox(rfc_2fa_on=True)
        resp = self.make_request()
        self.assert_ok_response(resp, secret=TEST_SECRET_BASE32)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check(
            'attributes',
            'account.rfc_totp.secret',
            TEST_SECRET_SERIALIZED,
            uid=TEST_UID,
            db='passportdbshard1',
        )
        self.env.event_logger.assert_events_are_logged(
            {
                'action': 'enable_rfc_otp',
                'info.rfc_totp': 'enabled',
                'user_agent': 'curl',
            },
        )
        self.env.statbox.assert_has_written(self.env.statbox.entry('enabled'))

    def test_account_without_password(self):
        self.setup_blackbox(rfc_2fa_on=False, has_password=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.without_password'])

    def test_account_not_found(self):
        self.setup_blackbox(uid=None)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])


class TestDisableRfcOtp(BaseManageRfcOtpTestcase):
    default_url = '/1/bundle/rfc_otp/disable/?consumer=dev'

    def test_ok(self):
        self.setup_blackbox(rfc_2fa_on=True)
        resp = self.make_request()
        self.assert_ok_response(resp)

        self.env.event_logger.assert_events_are_logged(
            {
                'action': 'disable_rfc_otp',
                'info.rfc_totp': 'disabled',
                'user_agent': 'curl',
            },
        )
        self.env.statbox.assert_has_written(self.env.statbox.entry('disabled'))

    def test_action_not_required(self):
        self.setup_blackbox(rfc_2fa_on=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'])

    def test_account_not_found(self):
        self.setup_blackbox(uid=None)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])
