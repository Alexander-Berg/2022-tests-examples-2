# -*- coding: utf-8 -*-
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_UID2,
    TEST_USER_IP,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.oauth import (
    OAuthPermanentError,
    OAuthTemporaryError,
)
from passport.backend.core.builders.oauth.faker import (
    device_authorize_commit_response,
    device_authorize_submit_response,
    oauth_bundle_error_response,
    token_response,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_ACCESS_TOKEN = 'access.token'
TEST_CLIENT_ID = 'f' * 32
TEST_CLIENT_SECRET = 'verySecretClientSecret'
TEST_CLIENT_TITLE = u'<b>Почта России'
TEST_CLIENT_TITLE_ESCAPED = u'&lt;b&gt;Почта России'
TEST_FIRSTNAME = u'%_%'

TEST_ENCODED_ENV_DATA = {
    'region_id': 102630,
    'browser_id': 4,
    'os_family_id': 434,
}
TEST_DECODED_ENV_DATA = {
    'region_id': 102630,
    'browser': 'Safari',
    'os_family': [
        'Mac OS X Yosemite',
        '10.10.5',
    ],
}
TEST_DEVICE_NAME = 'osx-test'
TEST_LOGIN_ID = 'login-id'


@with_settings_hosts
class ClientEditedNotificationTestcase(BaseBundleTestViews, EmailTestMixin):

    default_url = '/1/bundle/oauth/client/edit/send_notifications/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        client_id=TEST_CLIENT_ID,
        client_title=TEST_CLIENT_TITLE,
        redirect_uris_changed='yes',
        scopes_changed='1',
    )
    http_headers = dict(
        host=TEST_HOST,
        cookie='Session_id=foo',
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['oauth_client.send_mail'])
        self.setup_blackbox_response()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_response(self, totp_is_set=False):
        bb_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            firstname=TEST_FIRSTNAME,
            attributes={
                'account.2fa_on': totp_is_set,
            },
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

    def check_emails_sent(self, client_id=TEST_CLIENT_ID, client_title=TEST_CLIENT_TITLE_ESCAPED,
                          redirect_uris_changed=True, scopes_changed=True, totp_is_set=False):
        self.assert_emails_sent([
            self.build_email(
                address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
                is_native=False,
                client_id=client_id,
                client_title=client_title,
                redirect_uris_changed=redirect_uris_changed,
                scopes_changed=scopes_changed,
                totp_is_set=totp_is_set,
            ),
            self.build_email(
                address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
                is_native=True,
                client_id=client_id,
                client_title=client_title,
                redirect_uris_changed=redirect_uris_changed,
                scopes_changed=scopes_changed,
                totp_is_set=totp_is_set,
            ),
        ])

    def build_email(self, address, is_native, client_id, client_title, redirect_uris_changed, scopes_changed,
                    totp_is_set):
        data = {
            'language': 'ru',
            'addresses': [address],
            'subject': 'oauth_client_edited.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': TEST_FIRSTNAME},
                'oauth_client_edited.notice': {
                    'MASKED_LOGIN': TEST_LOGIN if is_native else TEST_LOGIN[:2] + '***',
                    'CLIENT_TITLE': client_title,
                    'CLIENT_VIEW_URL_BEGIN': '<a href=\'https://oauth.yandex.ru/client/%s\'>' % client_id,
                    'CLIENT_VIEW_URL_END': '</a>',
                },
                'oauth_client_edited.if_hacked': {},
                'oauth_client_edited.view_journal': {
                    'JOURNAL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/journal\'>',
                    'JOURNAL_URL_END': '</a>',
                },
                'oauth_client_edited.edit_client': {
                    'CLIENT_EDIT_URL_BEGIN': '<a href=\'https://oauth.yandex.ru/client/%s/edit\'>' % client_id,
                    'CLIENT_EDIT_URL_END': '</a>',
                },
                'signature.secure': {},
            },
        }
        if scopes_changed:
            data['tanker_keys']['oauth_client_edited.scopes_changed'] = {}
        if redirect_uris_changed:
            data['tanker_keys']['oauth_client_edited.redirect_uris_changed'] = {}
        if not totp_is_set:
            data['tanker_keys']['oauth_client_edited.change_password'] = {
                'CHANGE_PASSWORD_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/password\'>',
                'CHANGE_PASSWORD_URL_END': '</a>',
            }
        return data

    def test_all_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_emails_sent()

    def test_scopes_only_ok(self):
        rv = self.make_request(query_args=dict(redirect_uris_changed='no'))

        self.assert_ok_response(rv)
        self.check_emails_sent(redirect_uris_changed=False)

    def test_redirect_uris_only_ok(self):
        rv = self.make_request(query_args=dict(scopes_changed='no'))

        self.assert_ok_response(rv)
        self.check_emails_sent(scopes_changed=False)

    def test_action_not_required(self):
        rv = self.make_request(query_args=dict(redirect_uris_changed='no', scopes_changed='no'))

        self.assert_error_response(rv, ['action.not_required'])

    def test_2fa_on(self):
        self.setup_blackbox_response(totp_is_set=True)
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_emails_sent(totp_is_set=True)


@with_settings_hosts(
    TV_AUTH_CLIENT_ID='tv-auth-client-id',
)
class DeviceAuthorizeSubmitTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/oauth/device_authorize/qr_code/submit/?consumer=dev'

    http_method = 'post'
    http_query_args = dict(
        language='ru',
        code='123',
    )
    http_headers = dict(
        host=TEST_HOST,
        cookie='Session_id=foo',
        authorization='OAuth foo',
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['oauth_client.device_authorize'])

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        self.env.oauth.set_response_value(
            'device_authorize_submit',
            device_authorize_submit_response()
        )
        rv = self.make_request()
        self.assert_ok_response(rv, **device_authorize_submit_response())

    @parameterized.expand([
        ('client.blocked',),
        ('client.approval_pending',),
        ('client.approval_rejected',),
        ('access.denied',),
        ('request.not_found',),
        ('new_unknown_error',),
    ])
    def test_error(self, error):
        self.env.oauth.set_response_value(
            'device_authorize_submit',
            oauth_bundle_error_response(error=error)
        )
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=[error])

    def test_temporary_error(self):
        self.env.oauth.set_response_side_effect(
            'device_authorize_submit',
            OAuthTemporaryError(),
        )
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['backend.oauth_failed'])


@with_settings_hosts
class DeviceAuthorizeInfoTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/oauth/device_authorize/qr_code/info/'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['oauth_client.device_authorize'])

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.http_query_args = dict(
            track_id=self.track_id,
            consumer='dev',
        )

    def tearDown(self):
        self.env.stop()

        del self.env
        del self.track_manager

    def test_ok_empty_track(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            browser=None,
            device_name=None,
            os_family=None,
            region_id=None,
        )

    def test_ok_filled_track(self):
        with self.track_transaction() as track:
            track.browser_id = TEST_ENCODED_ENV_DATA['browser_id']
            track.device_name = TEST_DEVICE_NAME
            track.os_family_id = TEST_ENCODED_ENV_DATA['os_family_id']
            track.region_id = TEST_ENCODED_ENV_DATA['region_id']

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            device_name=TEST_DEVICE_NAME,
            **TEST_DECODED_ENV_DATA
        )


@with_settings_hosts(
    TV_AUTH_CLIENT_ID='tv-auth-client-id',
)
class DeviceAuthorizeCommitTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/oauth/device_authorize/qr_code/commit/?consumer=dev'

    http_method = 'post'
    http_query_args = dict(
        language='ru',
        code='123',
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['oauth_client.device_authorize'])

    def tearDown(self):
        self.env.stop()
        del self.env

    @parameterized.expand([
        (['cookie', 'host', 'authorization'],),
        (['cookie', 'host'],),
        (['authorization'],),
    ])
    def test_ok(self, credentials):
        self.env.oauth.set_response_value(
            'device_authorize_commit',
            device_authorize_commit_response()
        )
        headers = {}
        if 'cookie' in credentials:
            headers['cookie'] = 'Session_id=foo'
            headers['host'] = TEST_HOST
        if 'authorization' in credentials:
            headers['cookie'] = 'Authorization: OAuth foo'
        rv = self.make_request(
            headers=headers,
        )
        self.assert_ok_response(rv, **device_authorize_commit_response())

    @parameterized.expand([
        ('client.blocked',),
        ('client.approval_pending',),
        ('client.approval_rejected',),
        ('access.denied',),
        ('request.not_found',),
        ('new_unknown_error',),
    ])
    def test_error(self, error):
        self.env.oauth.set_response_value(
            'device_authorize_commit',
            oauth_bundle_error_response(error=error)
        )
        rv = self.make_request(
            headers={
                'cookie': 'Session_id=foo',
                'host': TEST_HOST,
            },
        )
        self.assert_error_response(rv, error_codes=[error])

    def test_temporary_error(self):
        self.env.oauth.set_response_side_effect(
            'device_authorize_commit',
            OAuthTemporaryError(),
        )
        rv = self.make_request(
            headers={
                'cookie': 'Session_id=foo',
                'host': TEST_HOST,
            },
        )
        self.assert_error_response(rv, error_codes=['backend.oauth_failed'])

    def test_missing_all_headers(self):
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['cookie.empty', 'host.empty', 'authorization.empty'])

    def test_missing_host_but_cookie_is_there(self):
        rv = self.make_request(
            headers={
                'cookie': 'Session_id=foo',
                'host': '',
            },
        )
        self.assert_error_response(rv, error_codes=['cookie.empty', 'host.empty', 'authorization.empty'])


@with_settings_hosts()
class TokenBySessionidTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/oauth/token_by_sessionid/?consumer=dev'
    http_method = 'post'

    def _build_headers(self, sessionid='sessionid.1234'):
        headers = dict(
            host=TEST_HOST,
            user_ip=TEST_USER_IP,
        )
        if sessionid:
            headers.update(cookie='Session_id=' + sessionid)
        return headers

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['oauth_client.token_by_sessionid'])
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

    def tearDown(self):
        self.env.stop()

    def setup_blackbox_response(
        self, multi=False, has_secure_phone=False,
        status=blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
    ):
        bb_kwargs = dict()
        if has_secure_phone:
            bb_kwargs.update(build_phone_secured(1, TEST_PHONE_NUMBER.e164))
        bb_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            status=status,
            login_id=TEST_LOGIN_ID,
            **bb_kwargs
        )
        if multi:
            bb_response = blackbox_sessionid_multi_append_user(bb_response, uid=TEST_UID2)
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)

    def assert_oauth_called(self, get_args=None, uid=TEST_UID, with_track_id=False, **kwargs):
        self.assertEqual(len(self.env.oauth.requests), 1)
        request = self.env.oauth.requests[0]
        expected_data = dict(
            assertion=uid,
            grant_type='passport_assertion',
            password_passed=False,
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
            auth_source='sessionid',
            login_id=TEST_LOGIN_ID,
            **kwargs
        )
        if with_track_id:
            expected_data['passport_track_id'] = self.track_id
        request.assert_post_data_equals(expected_data)
        get_args = dict(get_args or {}, user_ip=TEST_USER_IP)
        request.assert_query_equals(get_args)

    def test_ok__simple(self):
        self.setup_blackbox_response()
        self.env.oauth.set_response_value('_token', token_response(access_token=TEST_ACCESS_TOKEN))

        rv = self.make_request(
            query_args=dict(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
            ),
            headers=self._build_headers(),
        )
        self.assert_ok_response(
            rv,
            access_token=TEST_ACCESS_TOKEN,
            token_type='bearer',
            expires_in=30,
        )
        self.assert_oauth_called()
        self.env.blackbox.get_requests_by_method('sessionid')[0].assert_query_contains(dict(host=TEST_HOST))

    def test_ok__set_trusted_device(self):
        self.setup_blackbox_response(has_secure_phone=True)
        self.env.oauth.set_response_value('_token', token_response(access_token=TEST_ACCESS_TOKEN))
        with self.track_transaction() as track:
            track.allow_set_xtoken_trusted = True

        rv = self.make_request(
            query_args=dict(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
                track_id=self.track_id,
            ),
            headers=self._build_headers(),
        )
        self.assert_ok_response(
            rv,
            access_token=TEST_ACCESS_TOKEN,
            token_type='bearer',
            expires_in=30,
        )
        self.assert_oauth_called(with_track_id=True, set_is_xtoken_trusted=True)

    def test_ok__all_parameters(self):
        self.setup_blackbox_response(multi=True)
        self.env.oauth.set_response_value('_token', token_response(access_token=TEST_ACCESS_TOKEN))

        device_info = {
            'am_version': '5.6.7',
            'am_version_name': '5.6.7(123456)',
            'app_id': 'com.coding.like.i',
            'app_platform': '9 3/4',
            'manufacturer': 'Umbrella inc',
            'model': 'Nemesis 3',
            'app_version': '1.2.4',
            'app_version_name': '1.2.4(123456)',
            'uuid': '1f56abdd-5ab9-457c-95bd-e18312b4843b',
            'deviceid': '1f56abdd-5ab9-457c-95bd-e18312b4843b',
            'ifv': 'hz',
            'device_name': 'There are many like it, but this one is mine',
            'os_version': 'Windows 95',
            'device_id': '1f56abdd-5ab9-457c-95bd-e18312b4843b',
        }
        query_args = dict(
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
            uid=TEST_UID2,
            track_id=self.track_id,
        )
        query_args.update(device_info)
        rv = self.make_request(
            query_args=query_args,
            headers=self._build_headers(),
        )
        self.assert_ok_response(
            rv,
            access_token=TEST_ACCESS_TOKEN,
            token_type='bearer',
            expires_in=30,
        )
        self.assert_oauth_called(get_args=device_info, uid=TEST_UID2, with_track_id=True)

    def test_missing_userip(self):
        headers = self._build_headers()
        headers.pop('user_ip')
        rv = self.make_request(
            query_args=dict(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
            ),
            headers=headers,
        )
        self.assert_error_response(rv, ['ip.empty'])

    def test_invalid_sessionid(self):
        self.setup_blackbox_response(status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS)
        rv = self.make_request(
            query_args=dict(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
            ),
            headers=self._build_headers(),
        )
        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_invalid_uid(self):
        self.setup_blackbox_response()
        rv = self.make_request(
            query_args=dict(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
                uid=TEST_UID2,
            ),
            headers=self._build_headers(),
        )
        self.assert_error_response(rv, ['sessionid.no_uid'])

    def test_oauth_temporary_error(self):
        self.setup_blackbox_response()
        self.env.oauth.set_response_side_effect('_token', OAuthTemporaryError('error123'))
        rv = self.make_request(
            query_args=dict(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
            ),
            headers=self._build_headers(),
        )
        self.assert_error_response(rv, ['error123'])

    def test_oauth_permanent_error(self):
        self.setup_blackbox_response()
        self.env.oauth.set_response_side_effect('_token', OAuthPermanentError('error456'))
        rv = self.make_request(
            query_args=dict(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
            ),
            headers=self._build_headers(),
        )
        self.assert_error_response(rv, ['error456'])
