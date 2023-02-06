# -*- coding: utf-8 -*-

from copy import deepcopy
from functools import partial
import json

import mock
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_OAUTH_TOKEN,
    TEST_PDD_UID,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.avatars_mds_api.faker import (
    avatars_mds_api_upload_ok_response,
    avatars_mds_api_upload_response,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.counters import yapic_upload_ip_uid_counter
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts
from six import StringIO

from .base import (
    BaseAvatarTestCase,
    BaseAvatarTrackRequiredMixin,
    BaseAvatarTrackRequiredTestCase,
    TEST_ACCOUNT_DATA,
    TEST_AUTH_HEADER,
    TEST_AVATAR_KEY,
    TEST_DISPLAY_NAME,
    TEST_INVALID_SESSIONID_COOKIE,
    TEST_LOGIN,
    TEST_MISSING_SESSIONID_COOKIE,
    TEST_OAUTH_SCOPE,
    TEST_OLD_AVATAR_KEY,
    TEST_OTHER_UID,
    TEST_SESSIONID_VALUE,
    TEST_UID,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)


TEST_URL = 'http://someurl'
TEST_GROUP_ID = '1234'


class CommonTestsMixin(object):
    def test_missing_sessionid(self):
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_MISSING_SESSIONID_COOKIE),
        )
        self.assert_error_response(response, ['request.credentials_all_missing'])

    def test_invalid_sessionid(self):
        self.set_blackbox_response(
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_INVALID_SESSIONID_COOKIE),
        )
        self.assert_error_response(response, ['sessionid.invalid'])

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

    def test_disabled_account(self):
        self.set_blackbox_response(enabled=False)

        response = self.make_request(
            self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(response, ['account.disabled'])

    def test_disabled_on_deletion_account(self):
        self.set_blackbox_response(
            enabled=False,
            attributes={
                'account.is_disabled': '2',
            },
        )

        response = self.make_request(
            self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(response, ['account.disabled_on_deletion'])


class AvatarCounterMixin(object):
    def test_yapic_per_ip_limit_exceeded_error(self):
        """
        Проверим, что защитились счетчиком по ip от перебора
        """
        self.set_blackbox_response()
        counter = yapic_upload_ip_uid_counter.get_counter_buckets(mode=self.counter_mode)
        # установим счетчик вызовов на ip в limit + 1
        for _ in range(counter.limit + 1):
            counter.incr(TEST_USER_IP)

        response = self.make_request(
            self.build_headers(cookie=TEST_USER_COOKIE),
        )
        self.assert_error_response(
            response,
            ['rate.limit_exceeded'],
            **self.expected_on_error
        )

    def test_yapic_per_ip_and_uid_limit_exceeded_error(self):
        """
        Проверим, что защитились счетчиком по паре (ip, uid) от перебора
        """
        self.set_blackbox_response()
        counter = yapic_upload_ip_uid_counter.get_counter_buckets(check='uid', mode=self.counter_mode)
        # установим счетчик вызовов на (ip, uid) в limit + 1
        for _ in range(counter.limit + 1):
            counter.incr('%s:%s' % (TEST_USER_IP, TEST_UID))

        response = self.make_request(
            self.build_headers(cookie=TEST_USER_COOKIE),
        )
        self.assert_error_response(
            response,
            ['rate.limit_exceeded'],
            **self.expected_on_error
        )


@with_settings_hosts()
class TestAvatarGetListStartTrack(BaseAvatarTestCase,
                                  GetAccountBySessionOrTokenMixin,
                                  CommonTestsMixin):
    def setUp(self):
        super(TestAvatarGetListStartTrack, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None
            track.is_avatar_change = False

    def make_request(self, headers=None, params=None):
        if not params:
            params = {}
        params.update(consumer='dev')
        if headers is None:
            headers = self.build_headers(cookie=TEST_USER_COOKIE)

        return self.env.client.get(
            '/1/change_avatar/init/',
            query_string=params,
            headers=headers,
        )

    def get_expected_ok_response(self, avatar_key=TEST_OLD_AVATAR_KEY):
        if avatar_key is not None:
            avatars = [{
                'default': True,
                'id': avatar_key.split('/')[-1],
                'timestamp': 0,
                'url': 'avatars.mdst.yandex.net/get-yapic/%s/' % avatar_key,
            }]
        else:
            avatars = []
        expected_response = {
            'status': 'ok',
            'track_id': self.track_id,
            'avatars': avatars,
        }
        account_data = deepcopy(TEST_ACCOUNT_DATA)
        account_data['account']['display_name']['default_avatar'] = avatar_key or ''
        expected_response.update(account_data)
        return expected_response

    def test_ok_no_avatar(self):
        """
        Нет аватарки, список avatars должен быть пуст
        """
        self.set_blackbox_response(
            is_avatar_empty=True,
            default_avatar_key=None,
        )

        response = self.make_request()

        self.assert_ok_response(response, **self.get_expected_ok_response(avatar_key=None))
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('get_init_page', track_id=self.track_id),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID_VALUE)
        self.check_track(uid=TEST_UID)
        eq_(len(self.env.avatars_mds_api.requests), 0)

    def test_ok(self):
        """
        Тест успешной выдачи первой страницы смены аватара.
        Ответ включает данные аккаунта, список аватаров
        и track_id с котороым нужно ходить в остальные ручки.
        """
        self.set_blackbox_response()

        response = self.make_request()

        self.assert_ok_response(response, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('get_init_page', track_id=self.track_id),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID_VALUE)
        self.check_track(uid=TEST_UID)
        eq_(len(self.env.avatars_mds_api.requests), 0)

    def test_ok_not_default(self):
        self.set_blackbox_response()

        response = self.make_request(params={'uid': TEST_OTHER_UID})

        self.assert_ok_response(response, check_all=False)
        self.check_track(uid=TEST_OTHER_UID)
        eq_(len(self.env.avatars_mds_api.requests), 0)

    def test_ok_by_oauth_token(self):
        self.set_blackbox_response(
            scope=TEST_OAUTH_SCOPE,
            default_avatar_key=TEST_AVATAR_KEY,
        )

        response = self.make_request(
            headers=self.build_headers(
                authorization=TEST_AUTH_HEADER,
            ),
        )

        self.assert_ok_response(
            response,
            **self.get_expected_ok_response(avatar_key=TEST_AVATAR_KEY)
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'get_init_page',
                track_id=self.track_id,
            ),
        ])
        self.check_blackbox_params(oauth_token=TEST_OAUTH_TOKEN)
        eq_(len(self.env.avatars_mds_api.requests), 0)


@with_settings_hosts()
class TestAvatarGetList(BaseAvatarTrackRequiredTestCase,
                        BaseAvatarTrackRequiredMixin,
                        GetAccountBySessionOrTokenMixin):
    url = '/1/change_avatar/'
    method = 'get'

    @property
    def ok_params(self):
        return {
            'consumer': 'dev',
            'track_id': self.track_id,
        }

    def get_expected_ok_response(self, avatar_key=TEST_OLD_AVATAR_KEY):
        expected_response = {
            'status': 'ok',
            'track_id': self.track_id,
            'avatars': [{
                'default': True,
                'id': avatar_key.split('/')[-1],
                'timestamp': 0,
                'url': 'avatars.mdst.yandex.net/get-yapic/%s/' % avatar_key,
            }],
        }
        return expected_response

    def test_ok(self):
        """Тест успешного получения списка аватаров"""
        self._check_get_list_ok()

    def test_ok_by_oauth_token(self):
        """Тест успешного получения списка аватаров по авторизационному токену"""
        self.set_blackbox_response()

        response = self.make_request(
            headers=self.build_headers(authorization=TEST_AUTH_HEADER),
        )

        self.check_track(uid=TEST_UID)
        self.assert_ok_response(response, **self.get_expected_ok_response())
        self.check_blackbox_params(oauth_token=TEST_OAUTH_TOKEN)
        eq_(len(self.env.avatars_mds_api.requests), 0)


class AvatarUploadCommonTestsMixin(object):
    def test_upload_from_url(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_ok_response(response, **self.get_expected_ok_response())
        self.check_blackbox_params(sessionid=TEST_SESSIONID_VALUE)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('upload_from_url'),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
            ),
        ])
        self.check_avatars_mds_api_params(
            url=TEST_URL,
        )

    def test_upload_from_file(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_file', avatars_mds_api_upload_ok_response())

        params = merge_dicts(
            self.base_params,
            {
                'file': (StringIO('my file content'), 'test.png'),
            },
        )

        response = self.make_request(
            params=params,
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_ok_response(response, **self.get_expected_ok_response())
        self.check_blackbox_params(sessionid=TEST_SESSIONID_VALUE)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('upload_from_file'),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
            ),
        ])
        self.check_avatars_mds_api_params(
            files={'file': StringIO('my file content')},
        )

    def test_no_file_no_url(self):
        self.set_blackbox_response()

        response = self.make_request(
            params=self.base_params,
        )

        self.assert_error_response(response, ['form.invalid'], **self.expected_on_error)

    def test_both_file_and_url(self):
        self.set_blackbox_response()

        params = merge_dicts(
            self.base_params,
            {
                'file': (StringIO('my file content'), 'test.png'),
                'url': 'http://someurl.ru',
            },
        )

        response = self.make_request(params=params)

        self.assert_error_response(response, ['form.invalid'], **self.expected_on_error)

    def test_bad_url(self):
        self.set_blackbox_response()

        params = merge_dicts(
            self.base_params,
            {
                'url': 'http://.ru',
            },
        )

        response = self.make_request(
            params=params,
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(response, ['url.invalid'], **self.expected_on_error)

    def test_invalid_avatar_size(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value(
            'upload_from_file',
            avatars_mds_api_upload_response(
                status_code=415,
                description='Image is too small',
            ),
        )

        params = merge_dicts(
            self.base_params,
            {
                'file': (StringIO('my file content'), 'test.png'),
            },
        )

        response = self.make_request(
            params=params,
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(
            response,
            ['change_avatar.invalid_image_size'],
            **self.expected_on_error
        )

    def test_invalid_file_size(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value(
            'upload_from_file',
            avatars_mds_api_upload_response(
                status_code=415,
                description='bytes more than maximum allowed',
            ),
        )

        params = merge_dicts(
            self.base_params,
            {
                'file': (StringIO('my file content'), 'test.png'),
            },
        )

        response = self.make_request(
            params=params,
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(
            response,
            ['change_avatar.invalid_file_size'],
            **self.expected_on_error
        )

    def test_invalid_url_avatars_mds_api_response(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_response(status_code=434))

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(
            response,
            ['change_avatar.invalid_url'],
            **self.expected_on_error
        )

    def test_invalid_avatar_size_for_url_upload_avatars_mds_api_response(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value(
            'upload_from_url',
            avatars_mds_api_upload_response(
                status_code=415,
                description='Image is too small',
            ),
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(
            response,
            ['change_avatar.invalid_image_size'],
            **self.expected_on_error
        )

    def test_invalid_file_size_for_url_upload_avatars_mds_api_response(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value(
            'upload_from_url',
            avatars_mds_api_upload_response(
                status_code=415,
                description='bytes more than maximum allowed',
            ),
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(
            response,
            ['change_avatar.invalid_file_size'],
            **self.expected_on_error
        )

    def test_mds_temporary_error_avatars_mds_api_response(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_response(status_code=500))

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(
            response,
            ['change_avatar.mds_temporary_error'],
            **self.expected_on_error
        )


@with_settings_hosts(
    GET_AVATAR_URL_SCHEMALESS='localhost/get-yapic/%s/',
    **mock_counters(
        YAPIC_UPLOAD_PER_IP_LIMIT_COUNTER=(6, 600, 4),
        YAPIC_UPLOAD_PER_UID_LIMIT_COUNTER=(2, 60, 2),
        YAPIC_DELETE_PER_IP_LIMIT_COUNTER=(6, 600, 4),
        YAPIC_DELETE_PER_UID_LIMIT_COUNTER=(2, 60, 2),
    )
)
class TestAvatarUpload(BaseAvatarTrackRequiredTestCase,
                       BaseAvatarTrackRequiredMixin,
                       GetAccountBySessionOrTokenMixin,
                       AvatarCounterMixin,
                       AvatarUploadCommonTestsMixin):
    url = '/1/change_avatar/?consumer=dev'

    @property
    def base_params(self):
        return {
            'track_id': self.track_id,
        }

    @property
    def ok_params(self):
        return merge_dicts(
            self.base_params,
            {
                'url': TEST_URL,
            },
        )

    def get_expected_ok_response(self):
        return {
            'status': 'ok',
            'track_id': self.track_id,
            'avatar_url': 'localhost/get-yapic/1234/567890/',
        }

    def test_ok(self):
        bb_response = blackbox_sessionid_multi_append_user(
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
            ),
            uid=TEST_UID,
            login=TEST_LOGIN,
            default_avatar_key=TEST_OLD_AVATAR_KEY,
            display_name=TEST_DISPLAY_NAME.as_dict(),
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())

        response = self.make_request(
            params={
                'url': TEST_URL,
                'track_id': self.track_id,
            },
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('upload_from_url'),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
            ),
        ])

        eq_(response.status_code, 200)

        data = json.loads(response.data)

        expected_response = self.get_expected_ok_response()
        eq_(data, expected_response)

        self.check_avatars_mds_api_params(
            url=TEST_URL,
        )

    def test_upload_from_file_with_cyrillic_name(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_file', avatars_mds_api_upload_ok_response())

        # Замокаем secure_filename, чтобы она считала, что файловая система
        # кодирует имена в utf-8, т.к. в teamcity кодировка ФС -- ascii.
        import passport.backend.api.common.decorators
        with mock.patch.object(
            passport.backend.api.common.decorators,
            u'secure_filename',
            partial(
                passport.backend.api.common.decorators.secure_filename,
                file_system_encoding=u'utf-8',
            ),
        ):
            response = self.make_request(
                params={
                    'file': (StringIO('my file content'), u'привет.png'),
                    'track_id': self.track_id,
                },
            )

        eq_(response.status_code, 200)
        eq_(json.loads(response.data), self.get_expected_ok_response())
        self.check_blackbox_params(sessionid=TEST_SESSIONID_VALUE)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('upload_from_file'),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
            ),
        ])
        self.check_avatars_mds_api_params(
            files={u'file': StringIO(u'my file content')},
        )


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    **mock_counters(
        YAPIC_UPLOAD_PER_IP_LIMIT_COUNTER=(6, 600, 4),
        YAPIC_UPLOAD_PER_UID_LIMIT_COUNTER=(2, 60, 2),
        YAPIC_DELETE_PER_IP_LIMIT_COUNTER=(6, 600, 4),
        YAPIC_DELETE_PER_UID_LIMIT_COUNTER=(2, 60, 2),
    )
)
class TestAvatarUploadV2(BaseAvatarTestCase,
                         GetAccountBySessionOrTokenMixin,
                         CommonTestsMixin,
                         AvatarCounterMixin,
                         AvatarUploadCommonTestsMixin):
    url = '/2/change_avatar/?consumer=dev'

    @property
    def base_params(self):
        return {}

    @property
    def ok_params(self):
        return {
            'url': TEST_URL,
        }

    @property
    def expected_on_error(self):
        return {}

    def get_expected_ok_response(self, avatar_size='normal'):
        return {
            'avatar_url': 'https://localhost/get-yapic/1234/567890/%s' % avatar_size,
        }

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='avatar_change',
            ip=TEST_USER_IP,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'account_modification',
            ip=TEST_USER_IP,
            uid=str(TEST_UID),
            consumer='dev',
        )
        for action in (
                'upload_from_url',
                'upload_from_file',
        ):
            self.env.statbox.bind_entry(
                action,
                _inherit_from='local_base',
                action=action,
            )

    def make_request(self, headers=None, params=None):
        if params is None:
            params = self.ok_params
        if headers is None:
            headers = self.build_headers()

        return self.env.client.post(
            self.url,
            data=params,
            headers=headers,
        )

    def test_invalid_form(self):
        self.set_blackbox_response()
        resp = self.make_request(params={'uid': ''})
        self.assert_error_response(resp, ['uid.empty'])

    def test_missing_credentials(self):
        resp = self.make_request()
        self.assert_error_response(
            resp,
            error_codes=['request.credentials_all_missing'],
        )

    def test_uid_and_token_error(self):
        resp = self.make_request(
            params=merge_dicts(
                self.ok_params,
                {
                    'uid': TEST_UID,
                },
            ),
            headers=self.build_headers(
                authorization=TEST_AUTH_HEADER,
            ),
        )
        self.assert_error_response(
            resp,
            error_codes=['request.credentials_several_present'],
        )

    def test_by_uid_no_grants(self):
        self.set_blackbox_response()
        resp = self.make_request(
            params=merge_dicts(
                self.ok_params,
                {
                    'uid': TEST_UID,
                },
            ),
        )
        self.assert_error_response(
            resp,
            status_code=403,
            error_codes=['access.denied'],
            ignore_error_message=False,
            error_message="Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: ['change_avatar.by_uid']",
        )

    def test_pdd_by_uid_no_grants(self):
        self.set_blackbox_response(uid=TEST_PDD_UID)
        resp = self.make_request(
            params=merge_dicts(
                self.ok_params,
                {
                    'uid': TEST_PDD_UID,
                },
            ),
        )
        self.assert_error_response(
            resp,
            status_code=403,
            error_codes=['access.denied'],
            ignore_error_message=False,
            error_message="Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: ['change_avatar.pdd_by_uid']",
        )

    def test_by_uid_pdd_account_ok(self):
        self.set_blackbox_response(uid=TEST_PDD_UID)
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'change_avatar': ['base', 'by_uid'],
        }))

        resp = self.make_request(
            params=merge_dicts(
                self.ok_params,
                {
                    'uid': TEST_PDD_UID,
                },
            ),
        )
        self.assert_ok_response(resp, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'upload_from_url',
                uid=str(TEST_PDD_UID),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
                uid=str(TEST_PDD_UID),
            ),
        ])
        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_PDD_UID,
        })
        self.check_avatars_mds_api_params(url=TEST_URL)

    def test_by_uid_ok(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'change_avatar': ['base', 'by_uid'],
        }))

        resp = self.make_request(
            params=merge_dicts(
                self.ok_params,
                {
                    'uid': TEST_UID,
                },
            ),
        )
        self.assert_ok_response(resp, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('upload_from_url'),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
            ),
        ])
        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_UID,
        })
        self.check_avatars_mds_api_params(url=TEST_URL)

    def test_pdd_by_uid_ok(self):
        self.set_blackbox_response(uid=TEST_PDD_UID)
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'change_avatar': ['base', 'pdd_by_uid'],
        }))

        resp = self.make_request(
            params=merge_dicts(
                self.ok_params,
                {
                    'uid': TEST_PDD_UID,
                },
            ),
        )
        self.assert_ok_response(resp, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'upload_from_url',
                uid=str(TEST_PDD_UID),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
                uid=str(TEST_PDD_UID),
            ),
        ])
        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_PDD_UID,
        })
        self.check_avatars_mds_api_params(url=TEST_URL)

    def test_grants_for_pdd_account_not_pdd(self):
        self.set_blackbox_response()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'change_avatar': ['base', 'pdd_by_uid'],
        }))
        resp = self.make_request(
            params=merge_dicts(
                self.ok_params,
                {
                    'uid': TEST_UID,
                },
            ),
        )
        self.assert_error_response(
            resp,
            status_code=403,
            error_codes=['access.denied'],
            ignore_error_message=False,
            error_message="Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: ['change_avatar.by_uid']",
        )

    def test_ok_by_session(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())

        resp = self.make_request(headers=self.build_headers(cookie=TEST_USER_COOKIE))

        self.assert_ok_response(resp, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('upload_from_url'),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
            ),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID_VALUE)
        self.check_avatars_mds_api_params(url=TEST_URL)

    def test_pdd_ok_by_token(self):
        self.set_blackbox_response(uid=TEST_PDD_UID)
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())

        resp = self.make_request(
            headers=self.build_headers(
                authorization=TEST_AUTH_HEADER,
            ),
        )

        self.assert_ok_response(resp, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'upload_from_url',
                uid=str(TEST_PDD_UID),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='1234/567890',
                operation='updated',
                uid=str(TEST_PDD_UID),
            ),
        ])
        self.check_blackbox_params(oauth_token=TEST_OAUTH_TOKEN)
        self.check_avatars_mds_api_params(url=TEST_URL)

    def test_custom_avatar_size(self):
        self.set_blackbox_response()
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())

        resp = self.make_request(
            headers=self.build_headers(
                authorization=TEST_AUTH_HEADER,
            ),
            params=dict(self.ok_params, avatar_size='xxl'),
        )

        self.assert_ok_response(resp, **self.get_expected_ok_response(avatar_size='xxl'))
