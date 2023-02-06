# -*- coding: utf-8 -*-
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.ydb.faker.stubs import FakeResultSet


TEST_PARTNER_ID = 'p-id'
TEST_HOST = 'kinopoisk.ru'
TEST_URL = 'https://%s/smth' % TEST_HOST


@with_settings_hosts(
    YDB_TURBOAPP_PARTNERS_ENABLED=True,
)
class TestValidatePartner(BaseBundleTestViews):

    default_url = '/1/bundle/autofill/validate_partner/'
    http_method = 'get'
    http_query_args = {
        'consumer': 'dev',
        'partner_id': TEST_PARTNER_ID,
        'page_url': TEST_URL,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'autofill': ['validate_partner']}))
        self.env.fake_ydb.set_execute_return_value([FakeResultSet([])])

    def tearDown(self):
        self.env.stop()
        del self.env

    def build_host_row(self, host=TEST_HOST, partner_id=TEST_PARTNER_ID):
        return dict(
            host=host,
            partner_id=partner_id,
            allow_psuid=False,
        )

    def build_url_row(self, url=TEST_URL, partner_id=TEST_PARTNER_ID):
        return dict(
            url=url,
            partner_id=partner_id,
        )

    def test_permissions_none(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            partner_id=TEST_PARTNER_ID,
            permissions='none',
        )
        assert len(self.env.fake_ydb.executed_queries()) == 2

    def test_permissions_no_phone(self):
        self.env.fake_ydb.set_execute_side_effect([
            [FakeResultSet([])],
            [FakeResultSet([
                self.build_host_row(),
            ])],
        ])
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            partner_id=TEST_PARTNER_ID,
            permissions='no_phone',
        )
        assert len(self.env.fake_ydb.executed_queries()) == 2

    def test_permissions_all(self):
        self.env.fake_ydb.set_execute_side_effect([
            [FakeResultSet([
                self.build_url_row(),
            ])],
        ])
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            partner_id=TEST_PARTNER_ID,
            permissions='all',
        )
        assert len(self.env.fake_ydb.executed_queries()) == 1

    def test_partner_id_mismatch(self):
        self.env.fake_ydb.set_execute_side_effect([
            [FakeResultSet([
                self.build_url_row(partner_id='smth_other'),
            ])],
        ])
        rv = self.make_request()
        self.assert_error_response(rv, ['partner_id.not_matched'])
        assert len(self.env.fake_ydb.executed_queries()) == 1

    def test_ok_with_empty_path(self):
        rv = self.make_request(query_args=dict(page_url='https://%s' % TEST_HOST))
        self.assert_ok_response(
            rv,
            partner_id=TEST_PARTNER_ID,
            permissions='none',
        )
        assert len(self.env.fake_ydb.executed_queries()) == 2
