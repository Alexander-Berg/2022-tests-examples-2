# -*- coding: utf-8 -*-
import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_HOST,
    TEST_OAUTH_SCOPE,
    TEST_OTHER_UID,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_SESSIONID_VALUE,
    TEST_UID,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.display_name import DisplayName
from passport.backend.utils.common import merge_dicts


TEST_LOGIN = 'test-login'
TEST_DISPLAY_NAME = DisplayName('test-display-name')
TEST_UNEXISTENT_UID = 456
TEST_SSL_SESSIONID = '2:sslsession'
TEST_AVATAR_KEY = '26/13-13'
TEST_OLD_AVATAR_KEY = 'oldavakey/asd'
TEST_ACCOUNT_DATA = {
    u'account': {
        u'display_login': u'test',
        u'display_name': {
            u'default_avatar': u'oldavakey',
            u'name': u'',
        },
        u'login': u'test',
        u'person': {
            u'birthday': u'1963-05-15',
            u'country': u'ru',
            u'firstname': u'\\u0414',
            u'gender': 1,
            u'language': u'ru',
            u'lastname': u'\\u0424',
        },
        u'uid': TEST_UID,
    },
}

TEST_INVALID_SESSIONID_COOKIE = 'Session_id=;sessionid2=%s' % TEST_SSL_SESSIONID
TEST_MISSING_SESSIONID_COOKIE = 'yandexuid=123'
TEST_AVATAR_SUBKEY = '567890'


class BaseAvatarTestCase(BaseBundleTestViews):
    counter_mode = None

    @property
    def ok_params(self):
        """Правильные параметры для тестирования ручки"""
        return {}   # pragma: no cover

    def setUp(self):
        self.track_id = None
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'change_avatar': ['base'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.is_avatar_change = True

        self.setup_statbox_templates()
        self.env.avatars_mds_api.set_response_value('delete', 'ok')

        self.get_avatar_mds_key_patch = mock.patch(
            'passport.backend.core.avatars.avatars.get_avatar_mds_key',
            mock.Mock(return_value=TEST_AVATAR_SUBKEY),
        )
        self.get_avatar_mds_key_patch.start()

    def tearDown(self):
        self.track_id_generator.stop()
        self.get_avatar_mds_key_patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.get_avatar_mds_key_patch

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'account_modification',
            ip=TEST_USER_IP,
            uid=str(TEST_UID),
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'local_base',
            mode='avatar_change',
            ip=TEST_USER_IP,
            uid=str(TEST_UID),
            track_id=self.track_id,
        )
        for action in (
                'get_init_page',
                'set_default',
                'delete',
                'delete_default',
                'upload_from_url',
                'upload_from_file',
        ):
            self.env.statbox.bind_entry(
                action,
                _inherit_from='local_base',
                action=action,
            )

    def check_blackbox_params(self, **kwargs):
        self.env.blackbox.requests[0].assert_query_contains(kwargs)

    def check_avatars_mds_api_params(self, files=None, **kwargs):
        self.env.avatars_mds_api.requests[0].assert_query_contains(kwargs)
        if files is not None:
            expected_filename, expected_file_stream = files.items()[0]
            self.env.avatars_mds_api.requests[0].assert_properties_equal(
                files={'file': expected_file_stream.read()},
            )

    def check_track(self, uid=TEST_UID):
        track = self.track_manager.read(self.track_id)
        eq_(track.track_type, 'authorize')
        eq_(track.uid, str(uid))

    def build_headers(self, **kwargs):
        base_headers = dict(
            user_ip=TEST_USER_IP,
            cookie=None,
            host=TEST_HOST,
            authorization=None,
        )
        headers = merge_dicts(
            base_headers,
            kwargs,
        )
        return mock_headers(**headers)

    def make_request(self, headers, params=None):
        raise NotImplementedError()   # pragma: no cover

    def set_blackbox_response(self, uid=TEST_UID,
                              default_avatar_key=TEST_OLD_AVATAR_KEY,
                              scope=TEST_OAUTH_SCOPE,
                              status=blackbox.BLACKBOX_SESSIONID_VALID_STATUS, serialize=False, **kwargs):
        kwargs.update(
            uid=uid,
            default_avatar_key=default_avatar_key,
        )

        if uid == TEST_PDD_UID:
            kwargs.update(
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    status=status,
                    **kwargs
                ),
                uid=TEST_OTHER_UID,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                status=status,
                **kwargs
            ),
        )

        userinfo_response = blackbox_userinfo_response(**kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        if serialize:
            self.env.db.serialize(userinfo_response)


class BaseAvatarTrackRequiredTestCase(BaseAvatarTestCase):
    url = None
    yapic_ok_response = None
    method = 'post'

    def make_request(self, headers=None, params=None):
        if params is None:
            params = self.ok_params
        if headers is None:
            headers = self.build_headers(cookie=TEST_USER_COOKIE)
        if self.method == 'post':
            return self.env.client.post(
                self.url,
                data=params,
                headers=headers,
            )
        else:
            return getattr(self.env.client, self.method)(
                self.url,
                query_string=params,
                headers=headers,
            )

    @property
    def expected_on_error(self):
        return {
            'track_id': self.track_id,
        }

    def get_expected_ok_response(self):
        return {}   # pragma: no cover

    def _check_get_list_ok(self):
        self.set_blackbox_response()

        response = self.make_request()

        self.check_track(uid=TEST_UID)
        self.assert_ok_response(response, **self.get_expected_ok_response())
        self.check_blackbox_params(
            sessionid=TEST_SESSIONID_VALUE,
            multisession='yes',
        )
        eq_(len(self.env.avatars_mds_api.requests), 0)


class BaseAvatarTrackRequiredMixin(object):
    """
    Этот класс является вспомогательным для базовых тестовых проверок.
    Необходимо наследоваться от него после наследования от BaseAvatarTrackRequiredTestCase
    """

    def test_missing_headers(self):
        response = self.make_request(
            headers=self.build_headers(host=None, user_ip=None),
        )
        self.assert_error_response(response, ['host.empty', 'ip.empty'])

    def test_missing_host(self):
        response = self.make_request(
            headers=self.build_headers(
                cookie=TEST_USER_COOKIE,
                host=None,
            ),
        )
        self.assert_error_response(response, ['host.empty'])

    def test_missing_sessionid(self):
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_MISSING_SESSIONID_COOKIE),
        )
        self.assert_error_response_with_track_id(response, ['request.credentials_all_missing'])

    def test_invalid_sessionid(self):
        self.set_blackbox_response(
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_INVALID_SESSIONID_COOKIE),
        )

        self.assert_error_response_with_track_id(response, ['sessionid.invalid'])

    def test_disabled_account(self):
        self.set_blackbox_response(enabled=False)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response_with_track_id(response, ['account.disabled'])

    def test_disabled_on_deletion_account(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            enabled=False,
            attributes={
                'account.is_disabled': '2',
            },
        )
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response_with_track_id(response, ['account.disabled_on_deletion'])

    def test_missing_track(self):
        params = self.ok_params
        params.pop('track_id')
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params=params,
        )
        self.assert_error_response(response, ['track_id.empty'])

    def test_different_uid_in_track_and_in_credentials(self):

        self.set_blackbox_response(
            uid=TEST_UID,
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UNEXISTENT_UID  # uid не как в сессии

        headers = dict(
            cookie=TEST_USER_COOKIE,
            authorization=TEST_AUTH_HEADER,
        )
        for name, header in headers.items():
            response = self.make_request(
                headers=self.build_headers(**{name: header}),
            )
            self.assert_error_response_with_track_id(response, ['track.invalid_state'])

    def test_track_from_different_process(self):
        """Соответствие трека процессу определяется по полю is_avatar_change"""
        params = self.ok_params

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_avatar_change = False

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params=params,
        )

        self.assert_error_response_with_track_id(response, ['track.invalid_state'])
