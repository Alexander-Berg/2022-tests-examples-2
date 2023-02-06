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


@with_settings_hosts()
class TestDeleteExtractResult(BaseBundleTestViews):
    default_url = '/1/bundle/takeout/extract/delete_result/'
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
                grants={'takeout': ['delete_extract_result']},
            ),
        )
        self.setup_blackbox()

    def setup_blackbox(self, uid=TEST_UID, with_fail_extract_at=False):
        attributes = {
            'takeout.archive_s3_key': 'key',
            'takeout.archive_password': 'password',
            'takeout.archive_created_at': '123',
        }
        if with_fail_extract_at:
            attributes['takeout.fail_extract_at'] = '456'
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
        eq_(self.env.db.query_count(dbshard), 1)  # delete атрибутов

        self.env.db.check_missing('attributes', 'takeout.archive_s3_key', uid=uid, db=dbshard)
        self.env.db.check_missing('attributes', 'takeout.archive_password', uid=uid, db=dbshard)
        self.env.db.check_missing('attributes', 'takeout.archive_created_at', uid=uid, db=dbshard)
        self.env.db.check_missing('attributes', 'takeout.fail_extract_at', uid=uid, db=dbshard)

    def assert_historydb_ok(self, with_fail_extract_at=False):
        expected_log_entries = {
            'action': 'delete_takeout_extract_result',
            'consumer': 'dev',
            'takeout.archive_s3_key': '-',
            'takeout.archive_password': '-',
            'takeout.archive_created_at': '0',
        }
        if with_fail_extract_at:
            expected_log_entries['takeout.fail_extract_at'] = '0'
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_log_entries,
        )

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_db_ok()
        self.assert_historydb_ok()

    def test_ok_with_extra_attrs_in_db(self):
        self.setup_blackbox(with_fail_extract_at=True)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_db_ok()
        self.assert_historydb_ok(with_fail_extract_at=True)
