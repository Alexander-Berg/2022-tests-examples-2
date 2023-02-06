# -*- coding: utf-8 -*-

import json

from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.security.helpers import process_bt_counters
from passport.backend.core.builders.bbro_api import (
    BaseBBroApiError,
    BBroApiInvalidRequestError,
)
from passport.backend.core.builders.bbro_api.faker import (
    bbro_bt_counters_parsed,
    bbro_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    TEST_CLIENT_ID,
    TEST_TICKET,
)


TEST_USER_YANDEXUID = '123'
TEST_USER_COOKIE = 'yandexuid=%s;' % TEST_USER_YANDEXUID
TEST_USER_BAD_YANDEXUID = 'lal'
TEST_USER_BAD_COOKIE = 'yandexuid=%s' % TEST_USER_BAD_YANDEXUID
TEST_USER_IP = '127.0.0.1'
TEST_USER_AGENT = 'curl'


@with_settings_hosts(
    BBRO_API_URL='http://localhost/',
    BBRO_API_RETRIES=2,
    BBRO_API_TIMEOUT=2,
)
class TestSecurity(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.grants.set_grants_return_value(mock_grants(grants={'security': ['create_session']}))
        self.env.tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID): {
                    'alias': 'bbro',
                    'ticket': TEST_TICKET,
                },
            },
        ))

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def make_request(self, headers=None, get_params={}, post_params={}):
        get_parameters = {
            'consumer': 'dev',
        }
        post_parameters = {
            'track_id': self.track_id,
        }
        get_parameters.update(get_params)
        post_parameters.update(post_params)
        if headers is None:
            headers = mock_headers(cookie=TEST_USER_COOKIE, user_ip=TEST_USER_IP, user_agent=TEST_USER_AGENT)
        return self.env.client.post(
            '/1/bundle/security/session/',
            query_string=get_parameters,
            data=post_parameters,
            headers=headers,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            mode='security',
        )
        self.env.statbox.bind_entry(
            'session_created',
            _inherit_from='local_base',
            action='create_session',
            consumer='dev',
            ip=TEST_USER_IP,
            track_id=self.track_id,
            user_agent=TEST_USER_AGENT,
        )

    def assert_statbox_clear(self):
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def assert_statbox_ok(self):
        expected_entries = [
            self.env.statbox.entry(
                'session_created',
                yandexuid=TEST_USER_YANDEXUID,
                **process_bt_counters(bbro_bt_counters_parsed())
            ),
        ]
        self.env.statbox.assert_has_written(expected_entries)

    def assert_statbox_bbro_unavailable(self):
        expected_entries = [
            self.env.statbox.entry(
                'session_created',
                yandexuid=TEST_USER_YANDEXUID,
                error='bbro_api.unavailable',
            ),
        ]
        self.env.statbox.assert_has_written(expected_entries)

    def assert_statbox_bbro_invalid_yandexuid(self):
        expected_entries = [
            self.env.statbox.entry(
                'session_created',
                yandexuid=TEST_USER_BAD_YANDEXUID,
                error='bbro_api.invalid_yandexuid',
            ),
        ]
        self.env.statbox.assert_has_written(expected_entries)

    def test_missing_headers(self):
        response = self.env.client.post(
            '/1/bundle/security/session/',
        )
        self.assert_error_response(response, ['consumer.empty', 'track_id.empty'])

    def test_missing_cookie(self):
        response = self.make_request(headers=mock_headers(cookie=None, user_ip=TEST_USER_IP, user_agent=TEST_USER_AGENT))
        self.assert_error_response(response, ['cookie.empty'])

    def test_cookie_without_yandexuid(self):
        response = self.make_request(headers=mock_headers(cookie='kek=123;', user_ip=TEST_USER_IP, user_agent=TEST_USER_AGENT))
        self.assert_ok_response(response)

    def test_missing_user_agent(self):
        response = self.make_request(headers=mock_headers(cookie=TEST_USER_COOKIE, user_ip=TEST_USER_IP, user_agent=None))
        self.assert_error_response(response, ['useragent.empty'])

    def test_missing_ip(self):
        response = self.make_request(headers=mock_headers(cookie=TEST_USER_COOKIE, user_ip=None, user_agent=TEST_USER_AGENT))
        self.assert_error_response(response, ['ip.empty'])

    def test_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        self.env.bbro_api.set_response_value_without_method(json.dumps(bbro_response()))
        response = self.make_request()
        self.assert_ok_response(response)
        requests = self.env.bbro_api.requests
        eq_(len(requests), 1)
        self.assert_statbox_ok()

    def test_non_existing_yandexuid(self):
        self.env.bbro_api.set_response_value_without_method(json.dumps({}))
        response = self.make_request()
        self.assert_ok_response(response)
        requests = self.env.bbro_api.requests
        eq_(len(requests), 1)
        self.assert_statbox_clear()

    def test_bbro_fail_to_response(self):
        self.env.bbro_api.set_response_side_effect_without_method(BaseBBroApiError)
        response = self.make_request()
        self.assert_ok_response(response)
        requests = self.env.bbro_api.requests
        eq_(len(requests), 1)
        self.assert_statbox_bbro_unavailable()

    def test_bbro_invalid_yandexuid(self):
        self.env.bbro_api.set_response_side_effect_without_method(BBroApiInvalidRequestError)
        response = self.make_request(
            headers=mock_headers(
                cookie=TEST_USER_BAD_COOKIE,
                user_ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
            ),
        )
        self.assert_ok_response(response)
        self.assert_statbox_bbro_invalid_yandexuid()
