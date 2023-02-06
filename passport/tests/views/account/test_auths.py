# -*- coding: utf-8 -*-

from nose.tools import assert_equal as eq_
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.core import authtypes
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.builders.historydb_api import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_aggregated_browser_info,
    auth_aggregated_ip_info,
    auth_aggregated_item,
    auth_aggregated_os_info,
    auths_aggregated_response,
)


@with_settings_hosts(
    HISTORYDB_API_URL='http://localhost',
    HISTORYDB_API_CONSUMER='adminka',
)
class AuthsViewTestCase(BaseViewTestCase):

    path = '/1/account/auths_aggregated/'

    def test_no_headers(self):
        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
        )
        self.check_response_error(resp, ['ip.empty', 'cookie.empty', 'host.empty'])

    def test_no_grants(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='looser'))
        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['access.denied'])

    def test_historydb_api_failed(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.historydb_api.set_response_side_effect('auths_aggregated', HistoryDBApiTemporaryError)

        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.historydb_api_failed'])

    def test_ok(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        auths = [
            auth_aggregated_item(
                authtype=authtypes.AUTH_TYPE_WEB,
                ip_info=auth_aggregated_ip_info(),
                browser_info=auth_aggregated_browser_info(),
                os_info=auth_aggregated_os_info(),
                ts=3600,
            ),
        ]
        self.env.historydb_api.set_response_value('auths_aggregated', auths_aggregated_response(auths=auths))

        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_ok(
            resp,
            auths=auths,
        )
        eq_(len(self.env.historydb_api.requests), 1)
        request = self.env.historydb_api.requests[0]
        request.assert_query_equals({'consumer': 'adminka', 'uid': str(TEST_UID)})

    def test_ok_with_options_with_post(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        auths = []
        self.env.historydb_api.set_response_value('auths_aggregated', auths_aggregated_response(auths=auths))

        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID, 'password_auths': '1'},
            headers=self.get_headers(),
        )
        self.check_response_ok(
            resp,
            auths=auths,
        )
        eq_(len(self.env.historydb_api.requests), 1)
        request = self.env.historydb_api.requests[0]
        request.assert_query_equals({'consumer': 'adminka', 'uid': str(TEST_UID), 'password_auths': 'true'})
