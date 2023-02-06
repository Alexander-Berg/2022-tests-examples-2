# -*- coding: utf-8 -*-
import json

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_create_pwd_hash_response
from passport.backend.core.builders.shakur.faker import shakur_check_password_not_found
from passport.backend.core.models.phones.faker import build_account
from passport.backend.core.test.consts import (
    TEST_LOGIN,
    TEST_UID,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_OLD_PASSWORD = 'aaa1bbbccc'
TEST_OLD_PASSWORD_QUALITY = 30
TEST_NEW_PASSWORD = 'aaa1bbbccc_2'
TEST_NEW_PASSWORD_QUALITY = 100
TEST_SERIALIZED_NEW_PASSWORD = '6:hash'


@with_settings_hosts()
class TestSetPassword(BaseBundleTestViews):
    default_url = '/1/bundle/test/set_password/'
    http_method = 'POST'
    consumer = 'dev'
    http_query_args = {
        'uid': TEST_UID,
        'password': TEST_NEW_PASSWORD,
    }

    def setUp(self):
        super(TestSetPassword, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_NEW_PASSWORD),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_not_found()),
        )

        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['set_password']}))

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestSetPassword, self).tearDown()

    def _build_account(self, enabled=True, with_2fa=False):
        userinfo = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'password_quality.quality.uid': TEST_OLD_PASSWORD_QUALITY,
                'password_quality.version.uid': 3,
            },
            attributes={
                'password.encrypted': TEST_OLD_PASSWORD,
                'account.2fa_on': '1' if with_2fa else '0',
            },
            enabled=enabled,
        )
        return dict(userinfo=userinfo)

    def _setup_account(self, account):
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **account['userinfo']
        )

    def assert_historydb_ok(self):
        expected_log_entries = [
            {'name': 'info.password', 'value': TEST_SERIALIZED_NEW_PASSWORD},
            {'name': 'info.password_quality', 'value': str(TEST_NEW_PASSWORD_QUALITY)},
            {'name': 'info.password_update_time', 'value': TimeNow()},
            {'name': 'action', 'value': 'set_password_internal'},
        ]
        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            expected_log_entries,
        )

    def test_ok(self):
        self._setup_account(self._build_account())

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_historydb_ok()

    def test_disabled_ok(self):
        self._setup_account(self._build_account(enabled=False))

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_historydb_ok()

    def test_2fa_enabled_error(self):
        self._setup_account(self._build_account(with_2fa=True))

        rv = self.make_request()

        self.assert_error_response(rv, ['account.2fa_enabled'])
