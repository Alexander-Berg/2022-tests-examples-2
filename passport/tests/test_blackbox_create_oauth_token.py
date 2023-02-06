# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_create_oauth_token_response
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


TEST_UID = 1
TEST_CLIENT_ID = 2
TEST_IP = '127.0.0.1'
TEST_TOKEN = 'test.token'


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestCreateOauthTokenParse(BaseBlackboxRequestTestCase):
    def test_parse_ok(self):
        self.set_blackbox_response_value(blackbox_create_oauth_token_response(TEST_TOKEN))
        response = self.blackbox.create_oauth_token(
            uid=TEST_UID,
            ip=TEST_IP,
            client_id=TEST_CLIENT_ID,
            scope_ids=[3, 4],
            expire_time=100500,
        )
        eq_(
            response,
            {
                'access_token': TEST_TOKEN,
                'token_id': 1,
            },
        )


@with_settings(
    BLACKBOX_URL='http://test.local/',
)
class TestBlackboxRequestCreateOauthTokenUrl(BaseBlackboxTestCase):
    def test_minimal(self):
        request_info = Blackbox().build_create_oauth_token_request(
            uid=TEST_UID,
            ip=TEST_IP,
            client_id=TEST_CLIENT_ID,
            expire_time=100500,
        )
        check_all_url_params_match(
            request_info.url,
            {
                'method': 'create_oauth_token',
                'uid': str(TEST_UID),
                'client_id': str(TEST_CLIENT_ID),
                'userip': TEST_IP,
                'expire_time': '100500',
                'create_time': TimeNow(),
                'format': 'json',
            },
        )

    def test_full(self):
        request_info = Blackbox().build_create_oauth_token_request(
            uid=TEST_UID,
            ip=TEST_IP,
            client_id=TEST_CLIENT_ID,
            scope_ids=[4, 3],
            expire_time=100500,
            create_time=100501,
            device_id='dev-id',
            token_id='tok-id',
            xtoken_id='xtok-id',
            xtoken_shard=1,
            meta='meta',
            some_custom_param='some_custom_value',
        )
        check_all_url_params_match(
            request_info.url,
            {
                'method': 'create_oauth_token',
                'uid': str(TEST_UID),
                'client_id': str(TEST_CLIENT_ID),
                'userip': TEST_IP,
                'scopes': '3,4',
                'expire_time': '100500',
                'create_time': '100501',
                'device_id': 'dev-id',
                'token_id': 'tok-id',
                'xtoken_id': 'xtok-id',
                'xtoken_shard': '1',
                'some_custom_param': 'some_custom_value',
                'meta': 'meta',
                'format': 'json',
            },
        )

    @raises(ValueError)
    def test_bad_args(self):
        Blackbox().build_create_oauth_token_request(
            uid=TEST_UID,
            ip=TEST_IP,
            client_id=TEST_CLIENT_ID,
            scope_ids=[3, 4],
            expire_time=100500,
            xtoken_id='xtok-id',
            xtoken_shard=None,
        )
