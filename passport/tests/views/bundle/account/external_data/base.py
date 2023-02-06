# -*- coding: utf-8 -*-
import json

from nose.tools import nottest
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_HOST,
    TEST_LOGIN,
    TEST_NORMALIZED_PUBLIC_ID,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.datasync_api import DatasyncApiObjectNotFoundError
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import passport_external_data_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import fake_tvm_credentials_data


TEST_REQUEST_ID = 'request-id'
TEST_SESSION_ID = 'sessionid'

TEST_TOKEN_HEADERS = {'authorization': TEST_AUTH_HEADER}
TEST_COOKIE_HEADERS = {'cookie': 'Session_id=%s;' % TEST_SESSION_ID}

TEST_TVM_TICKET_BLACKBOX = 'test-ticket-blackbox'
TEST_TVM_TICKET_OTHER = 'test-ticket-other'
TEST_USER_TICKET = 'test-user-ticket'

TEST_DATASYNC_API_URL = 'https://datasync.net'


@nottest
class BaseExternalDataTestCase(BaseBundleTestViews):
    http_method = 'GET'
    oauth_scope = None
    http_headers = {
        'host': TEST_HOST,
        'user_ip': TEST_USER_IP,
        'other': {'X-Request-Id': TEST_REQUEST_ID},
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['external_info'],
        }))
        self.setup_blackbox_responses()
        self.setup_shakur_responses()
        self.env.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {'alias': 'blackbox', 'ticket': TEST_TVM_TICKET_BLACKBOX},
                    '2': {'alias': 'datasync_api', 'ticket': TEST_TVM_TICKET_OTHER},
                },
            ),
        )
        self.env.personality_api.set_response_side_effect(
            'passport_external_data_get',
            DatasyncApiObjectNotFoundError,
        )
        self.env.personality_api.set_response_value(
            'passport_external_data_update',
            passport_external_data_response(),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_responses(self, **blackbox_kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                user_ticket=TEST_USER_TICKET,
                public_id=TEST_NORMALIZED_PUBLIC_ID,
                **blackbox_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope=self.oauth_scope,
                user_ticket=TEST_USER_TICKET,
                public_id=TEST_NORMALIZED_PUBLIC_ID,
                **blackbox_kwargs
            ),
        )

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def test_authorization_missing_error(self):
        rv = self.make_request()
        self.assert_error_response(rv, ['request.credentials_all_missing'])

    def test_token_invalid_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['oauth_token.invalid'])

    def test_token_bad_scope_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope='test:foo'),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['oauth_token.invalid'])

    def test_session_invalid_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_error_response(rv, ['sessionid.invalid'])
