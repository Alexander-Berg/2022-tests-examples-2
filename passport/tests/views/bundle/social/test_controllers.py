# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json
import time

from nose.tools import eq_
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_editsession_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.social_api import (
    BaseSocialApiError,
    SocialApiRequestError,
    SocialApiTemporaryError,
    SubscriptionAlreadyExistsError,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    FACEBOOK_AVATAR,
    FIRSTNAME,
    get_bind_response,
    get_ok_response,
    get_profiles_full_response,
    get_profiles_no_profiles,
    get_profiles_response,
    get_subscription_info,
    get_template_profile_full_response,
    GOOGLE_AVATAR,
    GOOGLE_PROVIDER,
    LASTNAME,
    profile_item,
    profile_not_found_error,
    social_api_person_item,
    subscription_not_found_error,
    task_data_response,
    USERNAME,
)
from passport.backend.core.test.consts import (
    TEST_EMAIL1,
    TEST_EMAIL2,
    TEST_LOGIN2,
    TEST_SOCIAL_LOGIN1,
    TEST_SOCIAL_TASK_ID1,
    TEST_UID2,
    TEST_UNIXTIME1,
    TEST_YANDEX_EMAIL1,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.utils.time import datetime_to_integer_unixtime

from .base import (
    BaseSocialTestCase,
    BaseSocialTrackRequiredMixin,
    BaseSocialTrackRequiredTestCase,
    SOCIAL_AUTH_PROVIDERS,
    SOCIAL_DEFAULT_SUBSCRIPTION,
    TEST_ACCOUNT_DATA,
    TEST_AUTH_OFF,
    TEST_AUTH_ON,
    TEST_DISPLAY_NAME,
    TEST_HOST,
    TEST_INVALID_SESSIONID_COOKIE,
    TEST_LOGIN,
    TEST_MISSING_SESSIONID_COOKIE,
    TEST_NEW_SESSIONID,
    TEST_NOT_USERS_PROFILE_ID,
    TEST_OTHER_UID,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_PROFILE_ID,
    TEST_SESSIONID,
    TEST_SID,
    TEST_UID,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)


TEST_PHONISH_LOGIN1 = 'phne-test1'
TEST_PHONISH_DISPLAY_NAME1 = '+7 812 ***-**-96'
TEST_DATETIME1 = datetime(2015, 3, 1, 12, 2, 4)

eq_ = iterdiff(eq_)


def _get_expected_profiles_response():
    return {
        'profiles': [
            _get_expected_profile(100000000, 100, True, 25, 'google'),
            _get_expected_profile(100000001, 101, False, 83, 'vkontakte'),
            _get_expected_profile(100000002, 102, True, 2, 'facebook'),
            _get_expected_profile(100000003, 103, True, 74, 'twitter'),
            _get_expected_profile(100000004, 104, None, None, 'lastfm'),
            _get_expected_profile(100000005, 105, None, None, 'instagram'),
        ]
    }


def _get_expected_profile(uid, profile_id, allow_auth, sid, provider):
    returns = get_template_profile_full_response(uid, profile_id, allow_auth, sid, provider)

    del returns['allow_auth']
    if allow_auth is not None:
        returns['allow_auth'] = allow_auth

    returns['subscriptions'] = []
    if profile_id == 100:
        returns['subscriptions'] = [
            _get_subscription(25, checked=True),
            _get_subscription(74),
        ]

    elif profile_id == 101:
        returns['subscriptions'] = [
            _get_subscription(25),
            _get_subscription(74),
            _get_subscription(83, checked=True),
        ]

    elif profile_id == 102:
        returns['subscriptions'] = [
            _get_subscription(2, checked=True),
            _get_subscription(25),
            _get_subscription(74),
            _get_subscription(83),
        ]
    elif profile_id == 103:
        returns['subscriptions'] = [
            _get_subscription(25),
            _get_subscription(74, checked=True),
            _get_subscription(83),
        ]
    return returns


def _get_subscription(sid, checked=False):
    return {
        'sid': sid,
        'checked': bool(checked),
    }


@with_settings_hosts(
    SOCIAL_API_URL='localhost',
    SOCIAL_API_RETRIES=1,
)
class SocialGetThumbnailViewTest(BaseBundleTestViews):
    def setUp(self):
        super(SocialGetThumbnailViewTest, self).setUp()
        self.default_url = '/1/bundle/social/thumbnail/'
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'social': ['get_thumbnail']}))

    def tearDown(self):
        self.env.stop()
        del self.env
        super(SocialGetThumbnailViewTest, self).tearDown()

    def query_params(self, task_id=TEST_SOCIAL_TASK_ID1, avatar_size_x=60, avatar_size_y=60):
        return {
            'task_id': task_id,
            'avatar_size_x': avatar_size_x,
            'avatar_size_y': avatar_size_y,
        }

    def make_request(self, headers=None, params=None):
        params = params or {}
        params['consumer'] = 'dev'
        return self.env.client.get(
            self.default_url,
            query_string=params,
            headers=headers,
        )

    def test_social_api_temporary_error_fails(self):
        """Временная ошибка при запросе SocialApi"""
        self.env.social_api.set_social_api_response_side_effect(SocialApiTemporaryError)
        resp = self.make_request(params=self.query_params())
        self.assert_error_response(resp, error_codes=['backend.social_api_failed'])

    def test_social_api_request_error_fails(self):
        """Ошибка запроса SocialApi"""
        self.env.social_api.set_social_api_response_side_effect(SocialApiRequestError)
        resp = self.make_request(params=self.query_params())
        self.assert_error_response(resp, error_codes=['backend.social_api_permanent_error'])

    def test_social_api_base_error_fails(self):
        """Необрабатываемая ошибка запроса SocialApi"""
        self.env.social_api.set_social_api_response_side_effect(BaseSocialApiError)
        resp = self.make_request(params=self.query_params())
        self.assert_error_response(resp, error_codes=['exception.unhandled'])

    def test_with_empty_profile_ok(self):
        """Пришел почти совсем пустой профиль"""
        provider = GOOGLE_PROVIDER
        self.env.social_api.set_social_api_response_value(dict(profile={'provider': provider}))
        resp = self.make_request(params=self.query_params())
        self.assert_ok_response(
            resp,
            thumbnail={
                'provider': provider,
                'username': None,
                'firstname': None,
                'lastname': None,
                'avatar': None,
            },
        )

    def test_with_empty_profile_fields_ok(self):
        """Часть полей в профиле пустые"""
        self.env.social_api.set_social_api_response_value(
            task_data_response(username=None, firstname=None, lastname=None),
        )
        resp = self.make_request(params=self.query_params())
        self.assert_ok_response(
            resp,
            thumbnail={
                'provider': GOOGLE_PROVIDER,
                'username': None,
                'firstname': None,
                'lastname': None,
                'avatar': GOOGLE_AVATAR['0x0'],
            },
        )

    def test_with_multiple_avatars_ok(self):
        """Выбираем правильную аватарку из многих вариантов"""
        self.env.social_api.set_social_api_response_value(
            task_data_response(avatar=FACEBOOK_AVATAR),
        )
        resp = self.make_request(params=self.query_params(avatar_size_x=150, avatar_size_y=150))
        self.assert_ok_response(
            resp,
            thumbnail={
                'provider': GOOGLE_PROVIDER,
                'username': USERNAME,
                'firstname': FIRSTNAME,
                'lastname': LASTNAME,
                'avatar': FACEBOOK_AVATAR['50x150'],
            },
        )


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialGetListStartTrackTest(BaseSocialTestCase):
    def make_request(self, headers, params=None):
        params = params or {}
        params['consumer'] = 'dev'
        return self.env.client.get(
            '/1/change_social/init/',
            query_string=params,
            headers=headers,
        )

    def test_missing_headers(self):
        response = self.make_request(
            headers={},
        )
        self.assert_error_response(
            response,
            [
                'host.empty',
                'ip.empty',
            ],
        )

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
            headers=self.build_headers(cookie=TEST_MISSING_SESSIONID_COOKIE)
        )
        self.assert_error_response(response, ['sessionid.invalid'])

    def test_invalid_sessionid(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_INVALID_SESSIONID_COOKIE),
        )
        self.assert_error_response(response, ['sessionid.invalid'])

    def test_disabled_account(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            enabled=False,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(response, ['account.disabled'])

    def test_disabled_on_deletion_account(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            enabled=False,
            attributes={
                'account.is_disabled': '2',
            }
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        self.assert_error_response(response, ['account.disabled_on_deletion'])

    def test_social_response_error(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', 'Invalid response')

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )
        self.assert_error_response(response, ['backend.social_api_permanent_error'])

    def get_expected_ok_response(self, data):
        expected_response = _get_expected_profiles_response()
        expected_response.update({
            'status': 'ok',
            'track_id': data['track_id'],
        })
        expected_response.update(TEST_ACCOUNT_DATA)
        return expected_response

    def test_ok(self):
        """Тест успешной выдачи первой страницы социальных аккаунтов.
        Ответ включает данные аккаунта, список аккаунтов
        и track_id с которым нужно ходить в остальные ручки.
        """
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_full_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
        )

        data = json.loads(response.data)
        eq_(response.status_code, 200)
        eq_(data, self.get_expected_ok_response(data))
        track_id = data['track_id']
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry(
                'initialized',
                track_id=track_id,
            ),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_get_list_params(TEST_UID)


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialGetListSingleAuthTest(BaseSocialTrackRequiredTestCase, BaseSocialTrackRequiredMixin):
    social_ok_response = get_profiles_full_response()

    def make_request(self, headers, params=None):
        params = params or {}
        params['consumer'] = 'dev'
        return self.env.client.get(
            '/1/change_social/',
            query_string=params,
            headers=headers,
        )

    def test_social_response_error(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', 'Invalid response')

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['backend.social_api_permanent_error'])

    def get_expected_ok_response(self):
        expected_response = _get_expected_profiles_response()
        expected_response.update({
            'status': 'ok',
            'track_id': self.track_id,
        })
        return expected_response

    def test_ok(self):
        """Тест успешного получения спиcка соц.авторизаций (моноавторизация) """
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'track_id': self.track_id,
            },
        )

        self.check_track(uid=TEST_UID)
        eq_(response.status_code, 200)
        eq_(json.loads(response.data), self.get_expected_ok_response())
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_get_list_params(TEST_UID)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('listed'),
        ])

    def test_ok_no_profiles(self):
        """Тест успешного получения спиcка соц.авторизаций без профилей (моноавторизация) """
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_no_profiles())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'track_id': self.track_id,
            },
        )

        self.check_track(uid=TEST_UID)
        eq_(response.status_code, 200)
        eq_(json.loads(response.data), {
            'status': 'ok',
            'track_id': self.track_id,
            'profiles': [],
        })
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_get_list_params(TEST_UID)


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialGetListYandexPhonishProfileTest(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/change_social/init/'
    http_query_args = {}
    http_headers = {
        'host': TEST_HOST,
        'cookie': TEST_USER_COOKIE,
        'user_ip': '1.2.3.4',
    }

    def setUp(self):
        super(SocialGetListYandexPhonishProfileTest, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value({
            'dev': {
                'networks': ['127.0.0.1'],
                'grants': {'social_profiles': ['base']},
            },
        })

        self._setup_blackbox()
        self._setup_social()

    def tearDown(self):
        self.env.stop()
        del self.env
        super(SocialGetListYandexPhonishProfileTest, self).tearDown()

    def _setup_blackbox(self):
        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                ),
            ],
        )
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    uid=TEST_OTHER_UID,
                    aliases=dict(phonish=TEST_PHONISH_LOGIN1),
                    dbfields={'userinfo.reg_date.uid': TEST_DATETIME1.strftime('%Y-%m-%d %H:%M:%S')},
                    display_name={'name': TEST_PHONISH_DISPLAY_NAME1},
                ),
            ],
        )

    def _setup_social(self):
        self.env.social_api.set_response_side_effect(
            'get_profiles_by_uid',
            [
                get_profiles_response([
                    dict(
                        uid=TEST_UID,
                        provider='yandex',
                        provider_code='ya',
                        userid=str(TEST_OTHER_UID),
                        username=None,
                        allow_auth=False,
                        addresses=[],
                        subscriptions=[],
                        person=social_api_person_item(
                            firstname=None,
                            lastname=None,
                            birthday=None,
                            gender=None,
                            email=None,
                        ),
                    ),
                ]),
            ],
        )

    def _assert_phonish_profile_ok(self, profile):
        eq_(
            profile,
            {
                'provider': 'yandex',
                'provider_code': 'ya',
                'uid': TEST_UID,
                'userid': str(TEST_OTHER_UID),
                'phonish': {
                    'display_name': {'name': TEST_PHONISH_DISPLAY_NAME1},
                    'registration_timestamp': datetime_to_integer_unixtime(TEST_DATETIME1),
                },
                'profile_id': 123,
                'username': None,
                'addresses': [],
                'subscriptions': [],
                'person': {
                    'birthday': 'None',
                    'email': '',
                    'firstname': '',
                    'gender': '',
                    'lastname': '',
                    'nickname': '',
                    'phone_number': '',
                    'profile_id': 123,
                },
            },
        )

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            skip=['account', 'profiles', 'track_id'],
        )

        rv = json.loads(rv.data)
        eq_(len(rv['profiles']), 1)
        profile = rv['profiles'][0]

        self._assert_phonish_profile_ok(profile)


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialSetSubscriptionSingleAuthTest(BaseSocialTrackRequiredTestCase, BaseSocialTrackRequiredMixin):
    social_ok_response = get_subscription_info(TEST_PROFILE_ID, TEST_SID)
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'sid': TEST_SID,
    }

    def make_request(self, headers, params=None):
        params = params or {}
        return self.env.client.post(
            '/1/change_social/subscription/',
            data=params,
            query_string={'consumer': 'dev'},
            headers=headers,
        )

    def test_social_response_error(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('create_subscription', 'Invalid response')

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['backend.social_api_permanent_error'])

    def test_missing_profile_id(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['profile_id.empty'])

    def test_not_users_profile_id(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_NOT_USERS_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['social_profile.invalid'])

    def test_missing_sid(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['sid.empty'])

    def test_error_already_deleted(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_side_effect('create_subscription', SubscriptionAlreadyExistsError())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['action.not_required'])

    def test_ok(self):
        """Тест успешной установки подписки на сервис (моноавторизация) """
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('create_subscription', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('set_subscription'),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_subscr_set_params(TEST_PROFILE_ID, TEST_SID, index=1)


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialSetSubscriptionMultiAuthTest(BaseSocialTrackRequiredTestCase, BaseSocialTrackRequiredMixin):
    social_ok_response = get_ok_response()
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'sid': TEST_SID,
    }

    def make_request(self, headers, params=None):
        params = params or {}
        return self.env.client.post(
            '/1/change_social/subscription/',
            data=params,
            query_string={'consumer': 'dev'},
            headers=headers,
        )

    def test_change_user(self):
        bb_response = blackbox_sessionid_multi_append_user(
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
            ),
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )

        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('create_subscription', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        self.env.blackbox.requests[1].assert_query_contains(
            {
                'method': 'editsession',
                'uid': str(TEST_UID),
                'sessionid': TEST_SESSIONID,
                'userip': TEST_USER_IP,
                'host': TEST_HOST,
                'op': 'select',
            },

        )

        self.assert_auth_log(
            [
                self.build_auth_log_entries('ses_update', TEST_OTHER_UID),
                self.build_auth_log_entries('ses_update', TEST_UID),
            ]
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('set_subscription'),
        ])

        eq_(response.status_code, 200)
        data = json.loads(response.data)
        self.assert_cookies_ok(data.pop('cookies'))
        eq_(data, self.get_expected_ok_response(default_uid=TEST_UID))

        self.check_social_subscr_set_params(TEST_PROFILE_ID, TEST_SID, index=1)

    def test_ok(self):
        """Тест успешной установки подписки (мультиавторизация) """
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('create_subscription', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, **self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('set_subscription'),
        ])
        self.check_blackbox_params(
            sessionid=TEST_SESSIONID,
            multisession='yes',
        )
        self.check_social_subscr_set_params(TEST_PROFILE_ID, TEST_SID, index=1)


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialDeleteSubscriptionSingleAuthTest(BaseSocialTrackRequiredTestCase, BaseSocialTrackRequiredMixin):
    social_ok_response = u''
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'sid': TEST_SID,
    }

    def make_request(self, headers, params=None):
        params = params or {}
        params['consumer'] = 'dev'
        return self.env.client.delete(
            '/1/change_social/subscription/',
            query_string=params,
            headers=headers,
        )

    def test_missing_profile_id(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['profile_id.empty'])

    def test_not_users_profile_id(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_NOT_USERS_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['social_profile.invalid'])

    def test_missing_sid(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['sid.empty'])

    def test_social_response_error(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('delete_subscription', 'Invalid response')

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['backend.social_api_permanent_error'])

    def test_error_already_deleted(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('delete_subscription', subscription_not_found_error())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['action.not_required'])

    def test_ok(self):
        """Тест успешного удаления подписки (моноавторизация) """
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('delete_subscription', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        eq_(response.status_code, 200)
        eq_(json.loads(response.data), self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('deleted_subscription'),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_subscr_delete_params(TEST_PROFILE_ID, TEST_SID, index=1)


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialDeleteSubscriptionMultiAuthTest(BaseSocialTrackRequiredTestCase, BaseSocialTrackRequiredMixin):
    social_ok_response = get_ok_response()
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'sid': TEST_SID,
    }

    def make_request(self, headers, params=None):
        params = params or {}
        params['consumer'] = 'dev'
        return self.env.client.delete(
            '/1/change_social/subscription/',
            query_string=params,
            headers=headers,
        )

    def test_change_user(self):
        bb_response = blackbox_sessionid_multi_append_user(
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
            ),
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )

        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('delete_subscription', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        self.env.blackbox.requests[1].assert_query_contains(
            {
                'method': 'editsession',
                'uid': str(TEST_UID),
                'sessionid': TEST_SESSIONID,
                'userip': TEST_USER_IP,
                'host': TEST_HOST,
                'op': 'select',
            },

        )

        self.assert_auth_log(
            [
                self.build_auth_log_entries('ses_update', TEST_OTHER_UID),
                self.build_auth_log_entries('ses_update', TEST_UID),
            ]
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('deleted_subscription'),
        ])

        eq_(response.status_code, 200)
        data = json.loads(response.data)
        self.assert_cookies_ok(data.pop('cookies'))
        eq_(data, self.get_expected_ok_response(default_uid=TEST_UID))

        self.check_social_subscr_delete_params(TEST_PROFILE_ID, TEST_SID, index=1)

    def test_ok(self):
        """Тест успешного удаления подписки на сервис (мультиавторизация) """
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('delete_subscription', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'sid': TEST_SID,
                'track_id': self.track_id,
            },
        )

        eq_(response.status_code, 200)
        eq_(json.loads(response.data), self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('deleted_subscription'),
        ])
        self.check_blackbox_params(
            sessionid=TEST_SESSIONID,
            multisession='yes',
        )
        self.check_social_subscr_delete_params(TEST_PROFILE_ID, TEST_SID, index=1)


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialDeleteSingleAuthTest(BaseSocialTrackRequiredTestCase, BaseSocialTrackRequiredMixin):
    social_ok_response = u''
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'current_password': TEST_PASSWORD,
    }

    def make_request(self, headers, params=None):
        params = params or {}
        params['consumer'] = 'dev'
        return self.env.client.delete(
            '/1/change_social/profile/',
            query_string=params,
            headers=headers,
        )

    def check_track(self, is_password_passed=True, is_captcha_required=False):
        track = self.track_manager.read(self.track_id)
        eq_(track.is_password_passed, is_password_passed)
        eq_(track.is_captcha_required, is_captcha_required)

    def test_missing_profile_id(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['profile_id.empty'])

    def test_not_users_profile_id(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_NOT_USERS_PROFILE_ID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['social_profile.invalid'])

    def test_social_response_error(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [
                get_template_profile_full_response(TEST_UID, TEST_PROFILE_ID, True, TEST_SID, 'facebook'),
            ]
        })
        self.env.social_api.set_response_value('delete_profile', 'Invalid response')

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['backend.social_api_permanent_error'])

    def test_error_account_without_password_with_login_one_profile(self):
        self.setup_track()
        self.set_blackbox_response(
            uid=TEST_UID,
            social_profile_id=1,
            aliases={
                'social': 'uid-login',
            },
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [
                get_template_profile_full_response(TEST_UID, 101, True, TEST_SID, 'facebook'),
            ],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 101,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['social_profile.single_auth_method'])

    def test_error_account_without_password_with_login_two_profiles(self):
        self.setup_track()
        self.set_blackbox_response(
            uid=TEST_UID,
            social_profile_id=1,
            aliases={
                'social': 'uid-login',
            },
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [
                get_template_profile_full_response(TEST_UID, 101, True, TEST_SID, 'facebook'),
                get_template_profile_full_response(TEST_UID, 102, True, TEST_SID, 'twitter'),
            ],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 101,
                'track_id': self.track_id,
            },
        )
        eq_(response.status_code, 200)
        eq_(json.loads(response.data)['state'], 'complete_social_with_login')

    def test_error_account_without_password_without_login_one_profile(self):
        self.setup_track()
        self.set_blackbox_response(
            aliases=dict(social=TEST_SOCIAL_LOGIN1),
            login=None,
            social_profile_id=1,
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [
                get_template_profile_full_response(TEST_UID, 101, True, TEST_SID, 'facebook'),
            ],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 101,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['social_profile.single_auth_method'])

    def test_error_account_without_password_without_login_two_profiles(self):
        self.setup_track()
        self.set_blackbox_response(
            uid=TEST_UID,
            social_profile_id=1,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [
                get_template_profile_full_response(TEST_UID, 101, True, TEST_SID, 'facebook'),
                get_template_profile_full_response(TEST_UID, 102, True, TEST_SID, 'twitter'),
            ],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 101,
                'track_id': self.track_id,
            },
        )
        eq_(response.status_code, 200)
        eq_(json.loads(response.data)['state'], 'complete_social')

    def test_error_require_password(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [get_template_profile_full_response(TEST_UID, TEST_PROFILE_ID, True, TEST_SID, 'facebook')],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['password.required'])

    def test_error_invalid_password(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [get_template_profile_full_response(TEST_UID, TEST_PROFILE_ID, True, TEST_SID, 'facebook')],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'current_password': 'invalid_password',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['password.not_matched'])

        self.check_track(is_password_passed=None)

    def test_error_captcha_required(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [get_template_profile_full_response(TEST_UID, TEST_PROFILE_ID, True, TEST_SID, 'facebook')],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'current_password': 'invalid_password',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['captcha.required'])

        self.check_track(is_password_passed=None, is_captcha_required=True)

    def test_error_already_deleted(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())

        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [get_template_profile_full_response(TEST_UID, TEST_PROFILE_ID, True, TEST_SID, 'facebook')],
        })
        self.env.social_api.set_response_value('delete_profile', profile_not_found_error())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['action.not_required'], check_content=False)

    def test_ok_no_password_not_auth_profile(self):
        self.setup_track()

        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [
                get_template_profile_full_response(TEST_UID, 101, True, TEST_SID, 'facebook'),
                get_template_profile_full_response(TEST_UID, 102, False, TEST_SID, 'facebook'),
            ],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 102,
                'track_id': self.track_id,
            },
        )
        eq_(response.status_code, 200)
        eq_(json.loads(response.data), self.get_expected_ok_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('deleted'),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_delete_params(102, index=1)

    def test_ok_has_password(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [get_template_profile_full_response(TEST_UID, TEST_PROFILE_ID, True, TEST_SID, 'facebook')],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )
        response_data = json.loads(response.data)
        eq_(response.status_code, 200)
        self.assert_cookies_ok(response_data.pop('cookies'))
        eq_(response_data, self.get_expected_ok_response(default_uid=TEST_UID))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('deleted'),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_delete_params(TEST_PROFILE_ID, index=1)

        self.check_track()

    def test_lite(self):
        self.set_blackbox_response(
            aliases=dict(lite=TEST_EMAIL1),
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=True,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)
        self.check_social_delete_params(TEST_PROFILE_ID, index=1)

    def test_superlite(self):
        self.set_blackbox_response(
            aliases=dict(lite=TEST_EMAIL1),
            crypt_password=None,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=True,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)
        self.check_social_delete_params(TEST_PROFILE_ID, index=1)

    def test_mailish(self):
        self.set_blackbox_response(
            aliases=dict(mailish=TEST_EMAIL1),
            crypt_password=None,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=True,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(
            response,
            state='complete_social',
            track_id=self.track_id,
        )


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
)
class SocialDeleteMultiAuthTest(BaseSocialTrackRequiredTestCase, BaseSocialTrackRequiredMixin):
    social_ok_response = u''
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'current_password': TEST_PASSWORD,
    }

    def make_request(self, headers, params=None):
        params = params or {}
        params['consumer'] = 'dev'
        return self.env.client.delete(
            '/1/change_social/profile/',
            query_string=params,
            headers=headers,
        )

    def test_change_user(self):
        bb_response = blackbox_sessionid_multi_append_user(
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
            ),
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )

        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [get_template_profile_full_response(TEST_UID, TEST_PROFILE_ID, True, TEST_SID, 'facebook')],
        })
        self.env.social_api.set_response_value('delete_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )

        self.env.blackbox.requests[2].assert_query_contains(
            {
                'method': 'editsession',
                'uid': str(TEST_UID),
                'new_default': str(TEST_UID),
                'sessionid': TEST_SESSIONID,
                'userip': TEST_USER_IP,
                'host': TEST_HOST,
                'op': 'add',
            },
        )

        self.assert_auth_log(
            [
                self.build_auth_log_entries('ses_update', TEST_OTHER_UID),
                self.build_auth_log_entries('ses_update', TEST_UID),
            ]
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('deleted'),
        ])

        eq_(response.status_code, 200)
        data = json.loads(response.data)
        self.assert_cookies_ok(data.pop('cookies'))
        eq_(data, self.get_expected_ok_response(default_uid=TEST_UID))
        self.check_social_delete_params(TEST_PROFILE_ID, index=1)


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'login_method_change', 'social_allow'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'login_method_change', 'social_allow'},
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:social_allow': 5,
            'email:login_method_change': 5,
            'push:login_method_change': 5,
            'push:social_allow': 5,
        },
    )
)
class SocialSetAuthSingleAuthTest(
    EmailTestMixin,
    BaseSocialTrackRequiredTestCase,
    BaseSocialTrackRequiredMixin,
    AccountModificationNotifyTestMixin,
):
    social_ok_response = ''
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'current_password': TEST_PASSWORD,
        'set_auth': TEST_AUTH_ON,
    }

    def setUp(self):
        super(SocialSetAuthSingleAuthTest, self).setUp()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(
            ip=TEST_USER_IP,
        )

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        super(SocialSetAuthSingleAuthTest, self).tearDown()

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK', 'OK', 'OK'])

    def make_request(self, headers, params=None):
        params = params or {}
        return self.env.client.post(
            '/1/change_social/profile/',
            data=params,
            query_string={'consumer': 'dev'},
            headers=headers,
        )

    def check_track(self, is_password_passed=True, is_captcha_required=False):
        track = self.track_manager.read(self.track_id)
        eq_(track.is_password_passed, is_password_passed)
        eq_(track.is_captcha_required, is_captcha_required)

    def check_social_bind_task_params(
        self,
        request,
        task_id=TEST_SOCIAL_TASK_ID1,
        uid=TEST_UID,
    ):
        request.assert_url_starts_with('http://socialdev-2.yandex.ru/api/task/%s/bind?' % task_id)
        request.assert_query_equals(
            dict(
                allow_auth='1',
                consumer='passport',
                uid=str(uid),
            ),
        )

    def test_missing_profile_id(self):
        self.set_blackbox_response(uid=TEST_UID)
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'track_id': self.track_id,
                'set_auth': TEST_AUTH_ON,
            },
        )
        self.assert_error_response_with_track_id(response, ['profile_id.empty'])

    def test_not_users_profile_id(self):
        self.set_blackbox_response(
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_NOT_USERS_PROFILE_ID,
                'set_auth': TEST_AUTH_ON,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['social_profile.invalid'])

    def test_social_response_error(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', 'Invalid response')

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_ON,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['backend.social_api_permanent_error'])

    def test_error_set_auth_strong_password_policy(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
            subscribed_to=[67],
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_ON,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['account.strong_password_policy_enabled'])

    def test_ok_unset_auth_strong_password_policy(self):
        """
        Тест успешного удаления возможности авторизовываться профилем(моноавторизация) при политике сложного пароля
        """
        self.set_blackbox_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
            subscribed_to=[67],
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_OFF,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )

        eq_(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assert_cookies_ok(response_data.pop('cookies'))
        eq_(response_data, self.get_expected_ok_response(default_uid=TEST_UID))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('unset_auth'),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=TEST_AUTH_OFF, index=1)

        self.check_track()

    def test_error_account_without_password_with_login_single_auth_method(self):
        self.setup_track()
        self.set_blackbox_response(
            uid=TEST_UID,
            social_profile_id=1,
            aliases={
                'social': 'uid-login',
            },
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', {
            'profiles': [
                get_template_profile_full_response(TEST_UID, 101, True, TEST_SID, 'facebook'),
                get_template_profile_full_response(TEST_UID, 102, False, TEST_SID, 'twitter'),
            ]
        })
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 101,
                'set_auth': TEST_AUTH_OFF,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['social_profile.single_auth_method'])

    def test_error_account_without_password_with_login(self):
        self.setup_track()
        self.set_blackbox_response(
            uid=TEST_UID,
            social_profile_id=1,
            aliases={
                'social': 'uid-login',
            },
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 101,
                'set_auth': TEST_AUTH_ON,
                'track_id': self.track_id,
            },
        )
        eq_(response.status_code, 200)
        eq_(json.loads(response.data)['state'], 'complete_social_with_login')

    def test_error_account_without_password_without_login(self):
        self.setup_track()
        self.set_blackbox_response(
            uid=TEST_UID,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': 101,
                'set_auth': TEST_AUTH_ON,
                'track_id': self.track_id,
            },
        )
        eq_(response.status_code, 200)
        eq_(json.loads(response.data)['state'], 'complete_social')

    def test_error_require_password(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_OFF,
                'track_id': self.track_id,
            },
        )
        self.assert_error_response_with_track_id(response, ['password.required'])

    def test_error_invalid_password(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_OFF,
                'current_password': 'invalid_password',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['password.not_matched'])

        self.check_track(is_password_passed=None)

    def test_error_captcha_required(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_OFF,
                'current_password': 'invalid_password',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response_with_track_id(response, ['captcha.required'])

        self.check_track(is_password_passed=None, is_captcha_required=True)

    def test_on_provider_not_allow_auth(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password=TEST_PASSWORD_HASH,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    dict(
                        allow_auth=False,
                        profile_id=TEST_PROFILE_ID,
                        provider_code='zz',
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['social_profile.provider_not_allow_auth'], track_id=self.track_id)

    def test_ok_on(self):
        """Тест успешной установки возможности авторизовываться профилем(моноавторизация) """
        email = self.create_native_email(TEST_LOGIN, 'yandex.ru')
        self.set_blackbox_response(
            emails=[email],
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_ON,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )

        eq_(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assert_cookies_ok(response_data.pop('cookies'))
        eq_(response_data, self.get_expected_ok_response(default_uid=TEST_UID))

        self.env.blackbox.requests[2].assert_query_contains(
            {
                'method': 'editsession',
                'uid': str(TEST_UID),
                'new_default': str(TEST_UID),
                'sessionid': TEST_SESSIONID,
                'userip': TEST_USER_IP,
                'host': TEST_HOST,
                'op': 'add',
            },
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('set_auth'),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID, emails='getall')
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=TEST_AUTH_ON, index=1)

        self.check_track()
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='social_allow',
            uid=TEST_UID,
            title='Теперь вход в аккаунт {} возможен через соцсети'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='login_method_change',
            uid=TEST_UID,
            title='Изменён способ входа в аккаунт {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
            index=1,
        )
        self.assert_emails_sent([
            self.create_account_modification_mail(
                'social_allow',
                email['address'],
                dict(
                    login=TEST_LOGIN,
                    PROVIDER='Facebook',
                    USER_IP=TEST_USER_IP,
                ),
            ),
            self.create_account_modification_mail(
                'login_method_change',
                email['address'],
                dict(
                    login=TEST_LOGIN,
                    USER_IP=TEST_USER_IP,
                ),
            ),
        ])

    def test_ok_off(self):
        """Тест успешного удаления возможности авторизовываться профилем(моноавторизация) """
        self.set_blackbox_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_OFF,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )

        eq_(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assert_cookies_ok(response_data.pop('cookies'))
        eq_(response_data, self.get_expected_ok_response(default_uid=TEST_UID))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('unset_auth'),
        ])
        self.check_blackbox_params(sessionid=TEST_SESSIONID)
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=TEST_AUTH_OFF, index=1)

        self.check_track()
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='login_method_change',
            uid=TEST_UID,
            title='Изменён способ входа в аккаунт {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_ok_on_lite(self):
        self.set_blackbox_response(
            aliases=dict(lite=TEST_EMAIL1),
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=False,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=1, index=1)

    def test_ok_off_lite(self):
        self.set_blackbox_response(
            aliases=dict(lite=TEST_EMAIL1),
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=True,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': '0',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=0, index=1)

    def test_ok_on_superlite(self):
        self.set_blackbox_response(
            aliases=dict(lite=TEST_EMAIL1),
            crypt_password=None,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=False,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=1, index=1)

    def test_ok_off_superlite(self):
        self.set_blackbox_response(
            aliases=dict(lite=TEST_EMAIL1),
            crypt_password=None,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=True,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': '0',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=0, index=1)

    def test_on_phonish(self):
        self.set_blackbox_response(
            aliases=dict(phonish=TEST_PHONISH_LOGIN1),
            crypt_password=None,
            login=TEST_PHONISH_LOGIN1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(
                [
                    profile_item(
                        allow_auth=False,
                        profile_id=TEST_PROFILE_ID,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        eq_(len(self.env.social_api.requests), 1)
        self.check_social_get_list_params(TEST_UID, with_include=False)

    def test_on_portal_with_social_task(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email='cO.W@yA.rU')

        self.set_blackbox_response(
            crypt_password=TEST_PASSWORD_HASH,
            login='co-w',
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('bind_task_profile', get_bind_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)

        eq_(len(self.env.social_api.requests), 2)
        self.check_social_get_list_params(TEST_UID, with_include=False)
        self.check_social_bind_task_params(self.env.social_api.requests[1], TEST_SOCIAL_TASK_ID1, TEST_UID)

    def test_on_with_social_task_without_email(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email=None)

        self.set_blackbox_response(
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_LOGIN,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['social_profile.invalid'], track_id=self.track_id)

    def test_on_portal_with_social_task_alias_mismatch(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email=TEST_LOGIN2 + '@ya.ru')

        self.set_blackbox_response(
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_LOGIN,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['social_profile.invalid'], track_id=self.track_id)

    def test_on_portal_with_social_task_not_yandex_mail(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email=TEST_LOGIN + '@mail.ru')

        self.set_blackbox_response(
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_LOGIN,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['social_profile.invalid'], track_id=self.track_id)

    def test_on_lite_with_social_task(self):
        lite_email = 'cOW@mAiL.RU'

        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email=lite_email)

        self.set_blackbox_response(
            aliases=dict(lite=lite_email.lower()),
            crypt_password=TEST_PASSWORD_HASH,
            login=lite_email.lower(),
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('bind_task_profile', get_bind_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)

        eq_(len(self.env.social_api.requests), 2)
        self.check_social_get_list_params(TEST_UID, with_include=False)
        self.check_social_bind_task_params(self.env.social_api.requests[1], TEST_SOCIAL_TASK_ID1, TEST_UID)

    def test_on_completed_lite_with_social_task(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email=TEST_EMAIL1)

        self.set_blackbox_response(
            aliases=dict(
                lite=TEST_EMAIL1,
                portal=TEST_LOGIN,
            ),
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_LOGIN,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('bind_task_profile', get_bind_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)

        eq_(len(self.env.social_api.requests), 2)
        self.check_social_get_list_params(TEST_UID, with_include=False)
        self.check_social_bind_task_params(self.env.social_api.requests[1], TEST_SOCIAL_TASK_ID1, TEST_UID)

    def test_on_lite_with_social_task_alias_mismatch(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email=TEST_EMAIL2)

        self.set_blackbox_response(
            aliases=dict(lite=TEST_EMAIL1),
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_EMAIL1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['social_profile.invalid'], track_id=self.track_id)

    def test_on_phonish_with_social_task(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(email=TEST_EMAIL1)

        self.set_blackbox_response(
            aliases=dict(phonish=TEST_PHONISH_LOGIN1),
            crypt_password=None,
            login=TEST_PHONISH_LOGIN1,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['social_profile.invalid'], track_id=self.track_id)

    def test_off_with_social_task(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response()

        self.set_blackbox_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '0',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['profile_id.empty'], track_id=self.track_id)

    def test_on_with_social_task_provider_not_allow_auth(self):
        with self.track_transaction() as track:
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.social_task_data = task_data_response(
                email=TEST_LOGIN + '@yandex.ru',
                provider_code='zz',
            )

        self.set_blackbox_response(
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_LOGIN,
            uid=TEST_UID,
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(response, ['social_profile.provider_not_allow_auth'], track_id=self.track_id)

    def test_ok_with_authorization_track(self):
        with self.track_transaction() as track:
            track.allow_authorization = True
            track.password_verification_passed_at = str(int(time.time()))
            track.social_task_data = task_data_response(email=TEST_YANDEX_EMAIL1)
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.uid = TEST_UID

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                crypt_password=TEST_PASSWORD_HASH,
                login=TEST_YANDEX_EMAIL1.split('@')[0],
                uid=TEST_UID,
            ),
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('bind_task_profile', get_bind_response())

        response = self.make_request(
            headers=self.build_headers(cookie=None),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)

    def test_ok_with_valid_session_and_new_account_authorization_track(self):
        self.set_blackbox_response(
            crypt_password=TEST_PASSWORD_HASH,
            login=TEST_LOGIN,
            uid=TEST_UID2,
        )

        with self.track_transaction() as track:
            track.allow_authorization = True
            track.password_verification_passed_at = str(int(time.time()))
            track.social_task_data = task_data_response(email=TEST_YANDEX_EMAIL1)
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.uid = TEST_UID

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                crypt_password=TEST_PASSWORD_HASH,
                login=TEST_YANDEX_EMAIL1.split('@')[0],
                uid=TEST_UID,
            ),
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('bind_task_profile', get_bind_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)

    def test_ok_with_invalid_session_and_new_account_authorization_track(self):
        self.set_blackbox_response(
            uid=TEST_UID,
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )

        with self.track_transaction() as track:
            track.allow_authorization = True
            track.password_verification_passed_at = str(int(time.time()))
            track.social_task_data = task_data_response(email=TEST_YANDEX_EMAIL1)
            track.social_task_id = TEST_SOCIAL_TASK_ID1
            track.uid = TEST_UID

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                crypt_password=TEST_PASSWORD_HASH,
                login=TEST_YANDEX_EMAIL1.split('@')[0],
                uid=TEST_UID,
            ),
        )

        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())
        self.env.social_api.set_response_value('bind_task_profile', get_bind_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(response, track_id=self.track_id)

    def test_authorization_track_with_global_logout(self):
        with self.track_transaction() as track:
            track.allow_authorization = True
            track.password_verification_passed_at = str(TEST_UNIXTIME1 - timedelta(minutes=5).total_seconds())
            track.uid = TEST_UID

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                attributes={
                    'account.global_logout_datetime': TEST_UNIXTIME1,
                },
                crypt_password=TEST_PASSWORD_HASH,
                login=TEST_LOGIN,
                uid=TEST_UID,
            ),
        )

        response = self.make_request(
            headers=self.build_headers(cookie=None),
            params={
                'set_auth': '1',
                'track_id': self.track_id,
            },
        )

        self.assert_error_response(
            response,
            ['account.global_logout'],
            track_id=self.track_id,
        )


@with_settings_hosts(
    SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION,
    SOCIAL_AUTH_PROVIDERS=SOCIAL_AUTH_PROVIDERS,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:social_allow': 5,
            'email:login_method_change': 5,
            'push:login_method_change': 5,
            'push:social_allow': 5,
        },
    )
)
class SocialSetAuthMultiAuthTest(
    BaseSocialTrackRequiredTestCase,
    BaseSocialTrackRequiredMixin,
    AccountModificationNotifyTestMixin,
):
    social_ok_response = ''
    ok_params = {
        'profile_id': TEST_PROFILE_ID,
        'current_password': TEST_PASSWORD,
        'set_auth': TEST_AUTH_ON,
    }

    def setUp(self):
        super(SocialSetAuthMultiAuthTest, self).setUp()
        self.start_account_modification_notify_mocks(
            ip=TEST_USER_IP,
        )
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        super(SocialSetAuthMultiAuthTest, self).tearDown()

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK', 'OK', 'OK'])

    def make_request(self, headers, params=None):
        params = params or {}
        return self.env.client.post(
            '/1/change_social/profile/',
            data=params,
            query_string={'consumer': 'dev'},
            headers=headers,
        )

    def test_change_user(self):
        bb_response = blackbox_sessionid_multi_append_user(
            blackbox_sessionid_multi_response(
                uid=TEST_OTHER_UID,
            ),
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME.as_dict(),
            crypt_password=TEST_PASSWORD_HASH,
            age=-1,
        )

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_UID,
                session_value=TEST_NEW_SESSIONID,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())

        self.env.social_api.set_response_value('set_authentificate_profile', self.social_ok_response)
        self.env.social_api.set_response_value('get_profiles_by_uid', get_profiles_response())

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params={
                'profile_id': TEST_PROFILE_ID,
                'set_auth': TEST_AUTH_ON,
                'current_password': TEST_PASSWORD,
                'track_id': self.track_id,
            },
        )

        self.env.blackbox.requests[2].assert_query_contains(
            {
                'method': 'editsession',
                'uid': str(TEST_UID),
                'new_default': str(TEST_UID),
                'sessionid': TEST_SESSIONID,
                'userip': TEST_USER_IP,
                'host': TEST_HOST,
                'op': 'add',
            },
        )

        self.assert_auth_log(
            [
                self.build_auth_log_entries('ses_update', TEST_OTHER_UID),
                self.build_auth_log_entries('ses_update', TEST_UID),
            ]
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('cookie_edit'),
            self.env.statbox.entry('set_auth'),
        ])

        eq_(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assert_cookies_ok(response_data.pop('cookies'))
        eq_(response_data, self.get_expected_ok_response(default_uid=TEST_UID))
        self.check_social_put_params(TEST_PROFILE_ID, allow_auth=TEST_AUTH_ON, index=1)
