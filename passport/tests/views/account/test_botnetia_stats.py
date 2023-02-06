# -*- coding: utf-8 -*-

from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from yt.wrapper import YtError


@with_settings_hosts()
class BotnetiaStatsViewTestCase(BaseViewTestCase):

    path = '/1/account/botnetia_stats/'

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

    def test_ok(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.yt_dt.set_response_value(TEST_YT_RESPONSE)
        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_ok(
            resp,
            stats=TEST_YT_PARSED_RESPONSE,
        )

    def test_yt_disconnected(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.yt_dt.set_response_side_effect(YtError)
        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.yt_error'])

    def test_no_data(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.yt_dt.set_response_value([])
        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_ok(resp, stats=None)
