# -*- coding: utf-8 -*-
import datetime

from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from passport.backend.utils.common import merge_dicts
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


TEST_BLACKBOX_RESPONSE = '''
{
    "tokens": [
        {
            "oauth": {
                "uid": "123456",
                "client_name": "test-client", "client_icon": "", "meta": "",
                "issue_time": "2013-07-01 17:05:01",
                "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3b",
                "scope": "login:birthday login:info login:email",
                "client_homepage": "",
                "ctime": "2013-07-01 18:05:01",
                "expire_time": "2013-07-01 19:05:01"
            },
            "status": {
                "value": "DISABLED",
                "id": 4
            },
            "error": "some_error"
        },
        {
            "oauth": {
                "uid": "1234567",
                "client_name": "test-client2", "client_icon": "", "meta": "",
                "issue_time": "2013-07-02 17:05:01",
                "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3c",
                "scope": "login:birthday login:info login:email",
                "client_homepage": "",
                "ctime": "2013-07-02 18:05:01",
                "is_xtoken_trusted": true
            },
            "status": {
                "value": "VALID",
                "id": 0
            },
            "login_id": "login-id1",
            "error": "OK"
        }
    ]
}
'''


@with_settings(BLACKBOX_URL='http://localhost/')
class BlackboxGetOauthTokensRequestTestCase(BaseBlackboxRequestTestCase):

    def test_get_tokens(self):
        self.set_blackbox_response_value(TEST_BLACKBOX_RESPONSE)

        response = self.blackbox.get_oauth_tokens(uid=TEST_UID)

        self.assertEqual(response, [
            {
                "oauth": {
                    "uid": "123456",
                    "client_name": "test-client", "client_icon": "",
                    "meta": "",
                    "issue_time": datetime.datetime(2013, 7, 1, 17, 5, 1),
                    "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3b",
                    "scope": "login:birthday login:info login:email",
                    "client_homepage": "",
                    "ctime": datetime.datetime(2013, 7, 1, 18, 5, 1),
                    "expire_time": datetime.datetime(2013, 7, 1, 19, 5, 1),
                },
                "status": {
                    "value": "DISABLED",
                    "id": 4,
                },
                "error": "some_error",
            },
            {
                "oauth": {
                    "uid": "1234567",
                    "client_name": "test-client2", "client_icon": "",
                    "meta": "",
                    "issue_time": datetime.datetime(2013, 7, 2, 17, 5, 1),
                    "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3c",
                    "scope": "login:birthday login:info login:email",
                    "client_homepage": "",
                    "ctime": datetime.datetime(2013, 7, 2, 18, 5, 1),
                    "is_xtoken_trusted": True,
                },
                "status": {
                    "value": "VALID",
                    "id": 0,
                },
                "login_id": "login-id1",
                "error": "OK",
            },
        ])


@with_settings(BLACKBOX_URL='http://test.local/')
class BlackboxGetOauthTokensRequestUrlTestCase(BaseBlackboxTestCase):
    base_params = {
        'method': 'get_oauth_tokens',
        'format': 'json',
    }

    def test_get_oauth_tokens_url__basic(self):
        request_info = Blackbox().build_get_oauth_tokens_request(
            uid=TEST_UID,
            full_info=False,
            xtoken_only=False,
            get_is_xtoken_trusted=False,
            get_login_id=False,
            device_id=None,
            client_id=None,
        )

        url = urlparse(request_info.url)
        self.assertEqual(url.netloc, 'test.local')

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'uid': str(TEST_UID),
                },
            ),
        )

    def test_get_oauth_tokens_url__extended(self):
        request_info = Blackbox().build_get_oauth_tokens_request(
            uid=TEST_UID,
            full_info=True,
            xtoken_only=True,
            get_is_xtoken_trusted=True,
            get_login_id=True,
            device_id='c0ffee',
            client_id='deadface',
        )

        url = urlparse(request_info.url)
        self.assertEqual(url.netloc, 'test.local')

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'uid': str(TEST_UID),
                    'full_info': 'yes',
                    'xtoken_only': 'yes',
                    'get_is_xtoken_trusted': 'yes',
                    'get_login_id': 'yes',
                    'device_id': 'c0ffee',
                    'client_id': 'deadface',
                },
            ),
        )
