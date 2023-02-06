# -*- coding: utf-8 -*-
import json
import time

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts


TEST_ACCESS_TOKEN = 'a68d97976a66444496148b694802b009'
TEST_CLIENT_ID = 'a4ed2d853ee74a51bfc61911ae2622d1'
TEST_CLIENT_SECRET = 'ada1c32c759e482b993e2be31f250822'
TEST_HOST = '.yandex.ru'
TEST_USER_IP = '127.0.0.1'
TEST_USER_AGENT = 'curl'
TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_USER_COOKIES = 'yandexuid=%s' % TEST_YANDEXUID_COOKIE
TEST_REFERER = 'http://passportdev-python.yandex.ru/passport?mode=passport'

EXPECTED_COOKIE = u'Session_id=2:session; Domain=.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure; HttpOnly; Path=/'
EXPECTED_SECURE_COOKIE = u'sessionid2=2:sslsession; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'


def build_headers(user_ip=TEST_USER_IP):
    return mock_headers(
        host=TEST_HOST,
        user_ip=user_ip,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIES,
        referer=TEST_REFERER,
    )


@with_settings_hosts(
    PERMANENT_COOKIE_TTL=5,
    OAUTH_RETRIES=5,
    OAUTH_URL='http://localhost/',
)
class TestTokenCreate(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'oauth': ['token_create']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.setup_statbox_templates()
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 1
            track.login = 'test'
            track.language = 'tr'
            track.allow_oauth_authorization = True
            track.have_password = True

        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_ACCESS_TOKEN,
                'token_type': 'bearer',
            },
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def assert_statbox_clear(self):
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def assert_statbox_ok(self):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'oauth_token_created',
                client_id=TEST_CLIENT_ID,
                ip=TEST_USER_IP,
                track_id=self.track_id,
                uid='1',
            ),
        ])

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'oauth_token_created',
            _inherit_from='base',
            action='oauth_token_created',
        )

    def token_create_request(self, data, headers, consumer='dev'):
        return self.env.client.post(
            '/1/oauth/token/?consumer=%s' % consumer,
            data=data,
            headers=headers,
        )

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'client_id': TEST_CLIENT_ID,
            'client_secret': TEST_CLIENT_SECRET,
        }
        params = merge_dicts(base_params, kwargs)
        if exclude is not None:
            for key in exclude:
                del params[key]
        return params

    def test_without_need_headers(self):
        rv = self.token_create_request(self.query_params(), {})

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None, u'message': u'Missing required headers: "Ya-Consumer-Client-Ip"',
                          u'code': u'missingheader'}]},
        )
        self.assert_statbox_clear()

    def test_without_consumer(self):
        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
            consumer='',
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': u'consumer', u'message': u'Missing value', u'code': u'missingvalue'}]},
        )
        self.assert_statbox_clear()

    def test_without_track(self):
        rv = self.token_create_request(
            self.query_params(exclude=['track_id']),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': u'track_id', u'message': u'Missing value', u'code': u'missingvalue'}]},
        )
        self.assert_statbox_clear()

    def test_oauth_error(self):
        self.env.oauth.set_response_side_effect(
            '_token',
            OAuthTemporaryError('Request failed'),
        )

        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 503)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'OAuth failed',
                          u'code': u'oauthfailed'}]})
        self.assert_statbox_clear()

    def test_with_not_registered_account(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.allow_oauth_authorization = False

        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Authorization is not allowed for this track',
                          u'code': u'authorizationnotallowed'}]})
        self.assert_statbox_clear()

    def test_with_already_created_token(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.oauth_token_created_at = 100

        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'OAuth token already created for this account',
                          u'code': u'oauthtokenalreadycreated'}]})
        self.assert_statbox_clear()

    def test_with_bad_headers(self):
        rv = self.token_create_request(
            self.query_params(),
            mock_headers('127.0.0.1,123.4.5.6'),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Invalid header in request',
                          u'code': u'invalidheader'}]})
        self.assert_statbox_clear()

    def test_account_global_logout_after_track_created_error(self):
        """
        Дергаем ручку с треком, после создания которого был сделан
        глогаут на аккаунте
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                attributes={'account.global_logout_datetime': str(int(time.time()) + 1)},
            ),
        )
        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [
                    {
                        u'field': None,
                        u'message': u'User was logged out globally',
                        u'code': u'accountgloballogout',
                    },
                ],
            },
        )
        self.assert_statbox_clear()

    def test_ok_with_blackbox_unknown_uid_error(self):
        """
        Данные о пользователе не успели дойти до реплики,
        а мы уже спросили ЧЯ об этом пользователе.
        Удостоверяемся, что не упадем.
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'oauth': {
                    'access_token': TEST_ACCESS_TOKEN,
                    'token_type': 'bearer',
                },
            },
        )
        self.assert_statbox_ok()

    def test_response_with_token(self):
        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'oauth': {
                    'access_token': TEST_ACCESS_TOKEN,
                    'token_type': 'bearer',
                },
            },
        )

        # Проверка отсутствия записи в auth.log
        self.check_auth_log_entries(self.env.auth_handle_mock, [])
        track = self.track_manager.read(self.track_id)
        eq_(track.oauth_token_created_at, TimeNow())
        self.assert_statbox_ok()

    def test_response_with_error(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'error': 'invalid_client',
                'error_description': 'Client not found',
            },
        )
        rv = self.token_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'oauth': {
                    'error': 'invalid_client',
                    'error_description': 'Client not found',
                },
            },
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.oauth_token_created_at is None)
        self.assert_statbox_clear()

    def test_device_info(self):
        DEVICE_INFO_FIELDS = {
            'am_version': 'account_manager_version',
            'app_id': 'device_application',
            'app_platform': 'device_os_id',
            'os_version': 'device_os_version',
            'app_version': 'device_application_version',
            'manufacturer': 'device_manufacturer',
            'model': 'device_hardware_model',
            'uuid': 'device_app_uuid',
            'deviceid': 'device_hardware_id',
            'ifv': 'device_ifv',
            'device_name': 'device_name',
        }

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for field in DEVICE_INFO_FIELDS.values():
                setattr(track, field, field)

        rv = self.token_create_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data)['status'], 'ok')

        oauth_req = self.env.oauth.requests[0]
        oauth_req.assert_query_contains(DEVICE_INFO_FIELDS)
