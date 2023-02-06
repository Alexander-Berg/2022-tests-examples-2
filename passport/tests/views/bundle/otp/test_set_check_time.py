# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts


TEST_UID = 1
TEST_TIMESTAMP = 123456789


@with_settings_hosts()
class TestSetCheckTime(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['set_check_time']}))

    def tearDown(self):
        self.env.stop()
        del self.env

    def query_params(self, **kwargs):
        base_params = {
            'uid': TEST_UID,
            'totp_check_time': TEST_TIMESTAMP,
        }
        return merge_dicts(base_params, kwargs)

    def make_request(self, **data):
        return self.env.client.post(
            '/1/bundle/otp/set_check_time/?consumer=dev',
            data=data,
            headers=mock_headers(),
        )

    def test_ok(self):
        resp = self.make_request(**self.query_params())
        self.assert_ok_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.totp.check_time', str(TEST_TIMESTAMP), uid=TEST_UID, db='passportdbshard1')

        self.assert_events_are_empty(self.env.handle_mock)

    def test_db_error(self):
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)
        resp = self.make_request(**self.query_params())
        self.assert_error_response(resp, ['backend.database_failed'])
        self.env.db.check_missing('attributes', 'account.totp.check_time', uid=TEST_UID, db='passportdbshard1')
