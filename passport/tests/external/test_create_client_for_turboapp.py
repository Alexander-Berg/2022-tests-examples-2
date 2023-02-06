# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.urls import reverse_lazy
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.avatars_mds_api.faker import (
    avatars_mds_api_download_response,
    avatars_mds_api_upload_ok_response,
)
from passport.backend.core.builders.blackbox import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.oauth.core.db.client import (
    Client,
    PLATFORM_TURBOAPP,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_HOST,
    TEST_OTHER_UID,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.fake_configs import mock_grants
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


TEST_COOKIE = 'yandexuid=yu;Session_id=foo'
TEST_TITLE = 'test-title'
TEST_DESCRIPTION = 'test-description'
TEST_ICON_URL = 'https://localhost/avatars/get-icon/smth'
TEST_TURBOAPP_BASE_URL = 'https://ozon.ru'

TEST_REDIRECT_URI = 'yandexta://ozon.ru'
TEST_NEW_CLIENT_ICON_ID_PREFIX = '1234/%s-'  # сюда подставится client_id


@override_settings(
    DEFAULT_TURBOAPP_SCOPES=['test:foo', 'test:bar'],
    AVATARS_READ_URL='https://localhost/avatars/',
)
class CreateClientForTurboappTestcase(BundleApiTestCase):
    default_url = reverse_lazy('api_create_client_for_turboapp')
    http_method = 'POST'

    def setUp(self):
        super(CreateClientForTurboappTestcase, self).setUp()
        self.fake_grants.set_data({
            'dev': mock_grants(grants={'api': ['create_client_for_turboapp']}),
        })
        self.fake_avatars_mds_api.set_response_value(
            'download',
            avatars_mds_api_download_response(),
        )
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            avatars_mds_api_upload_ok_response(),
        )
        self.setup_blackbox_response()

    def setup_blackbox_response(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(uid=TEST_UID),
                uid=TEST_OTHER_UID,
            ),
        )

    def default_headers(self, user_ip=TEST_USER_IP, cookie=TEST_COOKIE):
        return {
            'HTTP_HOST': TEST_HOST,
            'HTTP_YA_CONSUMER_CLIENT_IP': user_ip,
            'HTTP_X_REAL_IP': user_ip,
            'HTTP_YA_CLIENT_USER_AGENT': 'curl',
            'HTTP_YA_CLIENT_COOKIE': cookie,
        }

    def default_params(self):
        return {
            'consumer': 'dev',
            'title': TEST_TITLE,
            'description': TEST_DESCRIPTION,
            'icon_url': TEST_ICON_URL,
            'turboapp_base_url': TEST_TURBOAPP_BASE_URL,
        }

    def assert_statbox_ok(self, client_id, **kwargs):
        expected_entries = [
            {
                'mode': 'check_cookies',
                'host': TEST_HOST,
                'consumer': 'dev',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'create_client',
                'type': 'turboapp',
                'status': 'ok',
                'client_id': client_id,
                'creator_uid': str(TEST_UID),
                'client_title': TEST_TITLE,
                'client_description': TEST_DESCRIPTION,
                'client_scopes': 'test:foo,test:bar',
                'client_redirect_uris': '',
            },
        ]
        expected_entries[0].update(kwargs)
        self.check_statbox_entries(expected_entries)

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        ok_('client_id' in rv)

        client = Client.by_display_id(rv['client_id'])
        eq_(client.uid, TEST_UID)
        eq_(client.default_title, TEST_TITLE)
        eq_(client.default_description, TEST_DESCRIPTION)
        eq_(sorted([s.keyword for s in client.scopes]), sorted(['test:foo', 'test:bar']))
        ok_(client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % rv['client_id']), client.icon_id)
        eq_(client.homepage, TEST_TURBOAPP_BASE_URL)
        eq_(client.redirect_uris, [])
        eq_(client.platforms, {PLATFORM_TURBOAPP})
        eq_(client.platform_specific_redirect_uris, [TEST_REDIRECT_URI])
        ok_(not client.is_yandex)

        self.assert_statbox_ok(rv['client_id'])

    def test_failed_to_download_icon_error(self):
        self.fake_avatars_mds_api.set_response_value(
            'download',
            avatars_mds_api_download_response(status_code=404),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['icon.not_found'])

    def test_failed_to_upload_icon_error(self):
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            '{"error": "crit"}',
            status=500,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['backend.failed'])

    def test_icon_bad_format(self):
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            '{"description": "cannot process image"}',
            status=400,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['icon.bad_format'])

    def test_no_session_cookie(self):
        rv = self.make_request(headers=self.default_headers(cookie='yandexuid=yu'))
        self.assert_status_error(rv, ['sessionid.empty'])

    def test_session_cookie_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessionid.invalid'])

    def test_user_not_in_cookie(self):
        rv = self.make_request(uid=43)
        self.assert_status_error(rv, ['sessionid.no_uid'])
