# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_UID
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.time import get_unixtime


@with_settings_hosts(
    TIME_FOR_COMPLETING_EXTRACT=3600,
)
class TestStartExtract(BaseBundleTestViews):
    default_url = '/1/bundle/takeout/extract/start/'
    http_method = 'post'
    http_query_args = {
        'uid': TEST_UID,
    }
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'takeout': ['start_extract']},
            ),
        )
        self.setup_blackbox()

    def setup_blackbox(self, uid=TEST_UID, is_extract_in_progress=True):
        attributes = {}
        if is_extract_in_progress:
            attributes['takeout.fail_extract_at'] = '42'
            attributes['takeout.extract_in_progress_since'] = str(get_unixtime())

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                attributes=attributes,
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def assert_db_ok(self, uid=TEST_UID, dbshard='passportdbshard1'):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(dbshard), 1)
        self.env.db.check('attributes', 'takeout.fail_extract_at', TimeNow(offset=3600), uid=uid, db=dbshard)

    def assert_historydb_ok(self):
        expected_log_entries = {
            'action': 'start_takeout_extract',
            'consumer': 'dev',
            'takeout.fail_extract_at': TimeNow(offset=3600),
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_log_entries,
        )

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_db_ok()
        self.assert_historydb_ok()

    def test_extract_not_requested(self):
        self.setup_blackbox(is_extract_in_progress=False)

        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'])
