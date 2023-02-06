# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.abc import (
    ABC,
    ABCAuthorizationInvalidError,
    ABCPermanentError,
    ABCTemporaryError,
)
from passport.backend.core.builders.abc.abc import GET_SERVICE_MEMBERS_FIELDS
from passport.backend.core.builders.abc.faker import (
    abc_cursor_paginated_response,
    abc_service_member,
    FakeABC,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_OAUTH_TOKEN = 'token'
TEST_SESSION_ID = 'session_id'
TEST_SERVICE_ID = 14


@with_settings(
    ABC_URL='http://localhost/',
    ABC_TIMEOUT=3,
    ABC_RETRIES=2,
)
class TestABCCommon(unittest.TestCase):
    def setUp(self):
        self.abc = ABC()

        self.response = mock.Mock()
        self.abc.useragent.request = mock.Mock()
        self.abc.useragent.request.return_value = self.response
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.abc
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = b'not a json'
        with assert_raises(ABCPermanentError):
            self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with assert_raises(ABCPermanentError):
            self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN)

    def test_abc_backend_timeout_error(self):
        self.response.status_code = 504
        self.response.content = b'"server is down"'
        with assert_raises(ABCTemporaryError):
            self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN)

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = b'"i am a teapot"'
        with assert_raises(ABCPermanentError):
            self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN)

    def test_oauth_token_invalid_error(self):
        self.response.status_code = 403
        self.response.content = b'"token invalid"'
        with assert_raises(ABCAuthorizationInvalidError):
            self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN)

    def test_default_initialization(self):
        abc = ABC()
        ok_(abc.useragent is not None)
        eq_(abc.url, 'http://localhost/')


@with_settings(
    ABC_URL='http://localhost/',
    ABC_TIMEOUT=3,
    ABC_RETRIES=2,
)
class TestABCMethods(unittest.TestCase):
    def setUp(self):
        self.fake_abc = FakeABC()
        self.fake_abc.start()
        self.abc = ABC()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'abc',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        self.fake_abc.stop()
        del self.fake_abc

    def test_authorization_missing(self):
        with assert_raises(ValueError):
            self.abc.get_service_members()

        ok_(not self.fake_abc.requests)

    def test_get_service_members_by_token_ok(self):
        self.fake_abc.set_response_value(
            'get_service_members',
            abc_cursor_paginated_response([abc_service_member()]),
        )
        response = self.abc.get_service_members(filter_args={'service': TEST_SERVICE_ID}, oauth_token=TEST_OAUTH_TOKEN)
        eq_(
            response,
            [abc_service_member()],
        )
        eq_(len(self.fake_abc.requests), 1)
        self.fake_abc.requests[0].assert_url_starts_with('http://localhost/v4/services/members/')
        self.fake_abc.requests[0].assert_query_equals({
            'fields': GET_SERVICE_MEMBERS_FIELDS,
            'page_size': '50',
            'service': str(TEST_SERVICE_ID),
        })
        self.fake_abc.requests[0].assert_headers_contain({
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        })

    def test_get_service_members_by_cookie_ok(self):
        self.fake_abc.set_response_value(
            'get_service_members',
            abc_cursor_paginated_response([abc_service_member()]),
        )
        response = self.abc.get_service_members(session_id=TEST_SESSION_ID)
        eq_(
            response,
            [abc_service_member()],
        )
        eq_(len(self.fake_abc.requests), 1)
        self.fake_abc.requests[0].assert_url_starts_with('http://localhost/v4/services/members/')
        self.fake_abc.requests[0].assert_query_equals({
            'fields': GET_SERVICE_MEMBERS_FIELDS,
            'page_size': '50',
        })
        self.fake_abc.requests[0].assert_headers_contain({
            'Cookie': 'Session_id=%s' % TEST_SESSION_ID,
        })

    def test_get_service_members_by_tvm_ok(self):
        self.fake_abc.set_response_value(
            'get_service_members',
            abc_cursor_paginated_response([abc_service_member()]),
        )
        response = ABC(use_tvm=True).get_service_members(session_id=TEST_SESSION_ID)
        eq_(
            response,
            [abc_service_member()],
        )
        eq_(len(self.fake_abc.requests), 1)
        self.fake_abc.requests[0].assert_url_starts_with('http://localhost/v4/services/members/')
        self.fake_abc.requests[0].assert_query_equals({
            'fields': GET_SERVICE_MEMBERS_FIELDS,
            'page_size': '50',
        })
        self.fake_abc.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
        })

    def test_get_service_members_with_pagination(self):
        self.fake_abc.set_response_side_effect(
            'get_service_members',
            [
                abc_cursor_paginated_response([abc_service_member()], next='http://localhost/v4/services/members/?cursor=1'),
                abc_cursor_paginated_response([abc_service_member()], next='http://localhost/v4/services/members/?cursor=2'),
                abc_cursor_paginated_response([abc_service_member()]),
            ]
        )
        response = self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN, from_page=2)
        eq_(
            response,
            [abc_service_member()] * 3,
        )
        eq_(len(self.fake_abc.requests), 3)

        urls_params = [
            {
                'fields': GET_SERVICE_MEMBERS_FIELDS,
                'page_size': '50',
            },
            {'cursor': '1'},
            {'cursor': '2'},
        ]
        for i in range(3):
            self.fake_abc.requests[i].assert_url_starts_with('http://localhost/v4/services/members/')
            self.fake_abc.requests[i].assert_query_equals(urls_params[i])
            self.fake_abc.requests[i].assert_headers_contain({
                'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
            })

    def test_get_service_members_with_pagination_limit_reached(self):
        self.fake_abc.set_response_side_effect(
            'get_service_members',
            [
                abc_cursor_paginated_response([abc_service_member()], next='http://localhost/v4/services/members/?cursor=1'),
                abc_cursor_paginated_response([abc_service_member()], next='http://localhost/v4/services/members/?cursor=2'),
                abc_cursor_paginated_response([abc_service_member()]),
            ]
        )
        response = self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN, max_pages=2)
        eq_(
            response,
            [abc_service_member()] * 2,
        )
        eq_(len(self.fake_abc.requests), 2)
