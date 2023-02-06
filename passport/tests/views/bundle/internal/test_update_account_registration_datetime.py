# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.models.phones.faker import build_account
from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime


@with_settings_hosts()
class TestUpdateAccountRegistrationDatetime(BaseBundleTestViews):
    default_url = '/1/bundle/test/update_account_registration_datetime/'
    consumer = 'dev'
    http_query_args = {
        'uid': TEST_UID1,
        'registration_datetime': to_unixtime(TEST_DATETIME1),
    }
    http_method = 'POST'

    def setUp(self):
        super(TestUpdateAccountRegistrationDatetime, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value({
            'dev': {
                'networks': ['127.0.0.1'],
                'grants': {'internal': ['update_account_registration_datetime']},
            },
        })

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestUpdateAccountRegistrationDatetime, self).tearDown()

    def _build_account(self):
        userinfo = dict(
            uid=TEST_UID1,
            attributes={},
        )
        return dict(userinfo=userinfo)

    def _setup_account(self, account):
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **account['userinfo']
        )

    def assert_db_ok(self, registration_datetime=TEST_DATETIME1):
        self.env.db.check(
            'attributes',
            'account.registration_datetime',
            str(to_unixtime(registration_datetime)),
            uid=TEST_UID,
            db='passportdbshard1',
        )

    def test_ok(self):
        self._setup_account(self._build_account())

        rv = self.make_request(
            query_args={'registration_datetime': to_unixtime(TEST_DATETIME2)},
        )

        self.assert_ok_response(rv)
        self.assert_db_ok(TEST_DATETIME2)
        self.env.statbox.assert_equals([])
        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                {'name': 'info.reg_date', 'value': TEST_DATETIME2.strftime('%Y-%m-%d %H:%M:%S')},
                {'name': 'action', 'value': 'update_account_registration_datetime'},
                {'name': 'consumer', 'value': 'dev'},
            ],
        )

    def test_account_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.not_found'])

    def test_empty_form(self):
        rv = self.make_request(exclude_args=('uid', 'registration_datetime'))
        self.assert_error_response(rv, ['registration_datetime.empty', 'uid.empty'])

    def test_invalid_registration_datetime(self):
        rv = self.make_request(
            query_args={'registration_datetime': 'foobar'},
        )
        self.assert_error_response(rv, ['registration_datetime.invalid'])
