# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.builders.meltingpot_api import (
    MeltingpotApiInvalidResponseError,
    MeltingpotApiTemporaryError,
)
from passport.backend.core.builders.meltingpot_api.faker.fake_meltingpot_api import (
    meltingpot_error_database_response,
    meltingpot_exception_unhandled,
    meltingpot_ok_response,
    meltingtpot_users_history_response,
)


TEST_MELTINGPOT_API_URL = 'http://meltingpot_api'
TEST_MELTINGPOT_API_CONSUMER = 'dev'


@with_settings_hosts(
    MELTINGPOT_API_URL=TEST_MELTINGPOT_API_URL,
    MELTINGPOT_API_CONSUMER=TEST_MELTINGPOT_API_CONSUMER,
)
class MeltingpotProxyViewTestCase(BaseViewTestCase):
    def check_meltingpot_api_params(self, method, path, data=None, index=0):
        if data is None:
            data = {}
        self.env.meltingpot_api.requests[index].assert_properties_equal(
            method=method,
            url=TEST_MELTINGPOT_API_URL + path,
            post_args=data,
        )

    def test_no_headers(self):
        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
        )
        self.check_response_error(resp, ['ip.empty', 'cookie.empty', 'host.empty'])

    def test_no_grants(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='looser'))
        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['access.denied'])

    def test_no_handler(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users-not-found',
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.meltingpot_handler_not_found'])

    def test_meltingpot_api_failed(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.meltingpot_api.set_meltingpot_response_side_effect(MeltingpotApiInvalidResponseError)

        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.meltingpot_failed'])

    def test_meltingpot_api_temporary_failed(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.meltingpot_api.set_meltingpot_response_side_effect(MeltingpotApiTemporaryError)

        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.meltingpot_failed'])

    def test_meltingpot_api_database_error(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.meltingpot_api.set_meltingpot_response_value(meltingpot_error_database_response())

        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.database_failed'])

    def test_meltingpot_api_unhandled_exception(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.meltingpot_api.set_meltingpot_response_value(meltingpot_exception_unhandled())

        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.meltingpot_failed'])

    def test_meltingpot_api_invalid_response(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.meltingpot_api.set_meltingpot_response_value('')

        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.meltingpot_failed'])

    def test_ok_users_history(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.meltingpot_api.set_meltingpot_response_value(meltingtpot_users_history_response())

        resp = self.make_request(
            method='GET',
            path='/1/meltingpot/1/users/%s/' % TEST_UID,
            params={'limit': 1, 'page': 1},
            headers=self.get_headers(),
        )

        response_json = json.loads(resp.data)
        eq_(response_json['status'], 'ok')
        eq_(response_json['history'][0]['id'], 1)
        self.check_meltingpot_api_params('GET', '/1/users/%s/?consumer=%s&limit=%s&page=%s' %
                                         (TEST_UID, TEST_MELTINGPOT_API_CONSUMER, 1, 1))

    def test_ok_add_user(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.meltingpot_api.set_meltingpot_response_value(meltingpot_ok_response())

        resp = self.make_request(
            method='POST',
            path='/1/meltingpot/1/users/',
            data={
                'uid': TEST_UID,
                'priority': TEST_PRIORITY,
                'reason': TEST_REASON,
            },
            headers=self.get_headers(),
        )

        response_json = json.loads(resp.data)
        eq_(response_json['status'], 'ok')
        self.check_meltingpot_api_params(
            method='POST',
            path='/1/users/?consumer=%s' % TEST_MELTINGPOT_API_CONSUMER,
            data={
                'uid': str(TEST_UID),
                'priority': str(TEST_PRIORITY),
                'reason': str(TEST_REASON),
            },
        )
