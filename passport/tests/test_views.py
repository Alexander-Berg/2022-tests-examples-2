# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from mock import (
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.social.common import oauth2
from passport.backend.social.common.db.execute import execute
from passport.backend.social.common.db.schemas import (
    business_application_map_table as bamt,
    profile_table as pt,
    token_table as tt,
)
from passport.backend.social.common.misc import (
    FACEBOOK_BUSINESS_ID,
    get_business_userid,
)
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.providers.Twitter import Twitter
from passport.backend.social.common.task import (
    build_provider_for_task,
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    BUSINESS_TOKEN1,
    BUSINESS_TOKEN2,
    CONSUMER1,
    CONSUMER_IP1,
    DEEZER_APPLICATION_NAME1,
    EMAIL1,
    FACEBOOK_APPLICATION_ID1,
    GOOGLE_APPLICATION_NAME1,
    MAIL_RU_APPLICATION_NAME1,
    MAIL_RU_APPLICATION_NAME2,
    MICROSOFT_APPLICATION_NAME1,
    MTS_BELARUS_APPLICATION_NAME1,
    PROFILE_ID1,
    PROFILE_ID2,
    REFRESH_TOKEN1,
    SIMPLE_USERID1,
    SIMPLE_USERID2,
    SIMPLE_USERID3,
    TASK_ID1,
    TWITTER_APPLICATION_ID1,
    UID1,
    UID2,
    UID3,
    USERNAME1,
    USERNAME2,
    YANDEX_APPLICATION_NAME1,
    YANDEXUID1,
    YANDEXUID2,
)
from passport.backend.social.common.token.db import TokenRecord
from passport.backend.social.common.web_service import Request
from passport.backend.social.proxy2.misc import FakeProfile
from passport.backend.social.proxy2.test import TestCase
from passport.backend.social.proxy2.views.v1.views import (
    _friends_to_statbox,
    ProxyResponse,
    sign_request,
)
from passport.backend.social.proxylib.test import (
    deezer as deezer_test,
    facebook as facebook_test,
    google as google_test,
    mail_ru as mail_ru_test,
    microsoft as microsoft_test,
    mts_belarus as mts_belarus_test,
    yandex as yandex_test,
)
from sqlalchemy.sql.expression import insert

from .base_proxy2_test_data import (
    TEST_TOKEN,
    TEST_USERID,
    TEST_USERNAME,
)


class BaseTestCase(TestCase):
    @property
    def application_grants(self):
        return ['no-cred-use-token']


class TestSignRequestView(BaseTestCase):
    def setUp(self):
        super(TestSignRequestView, self).setUp()

        self.proxylib_response = Mock(return_value=None)

        self.__patches = [
            patch('passport.backend.social.proxy2.views.v1.views.get_proxy_response', Mock(side_effect=self.proxylib_response)),
        ]
        for p in self.__patches:
            p.start()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['job-authorization'] + self.application_grants,
        )

    def tearDown(self):
        for p in reversed(self.__patches):
            p.stop()
        super(TestSignRequestView, self).tearDown()

    def _save_task(self, task_id, application_id):
        task = Task()
        task.profile = dict(
            username=TEST_USERNAME,
            userid=TEST_USERID,
        )

        application = providers.get_application_by_id(application_id)
        task.application = application

        provider_info = providers.get_provider_info_by_id(application.provider['id'])
        task.provider = build_provider_for_task(
            provider_info['code'],
            provider_info['name'],
            provider_info['id'],
        )

        task.access_token = TEST_TOKEN
        task.task_id = task_id
        task.consumer = CONSUMER1
        save_task_to_redis(self._fake_redis, task_id, task)

    def test_sign_request(self):
        self._save_task(
            task_id=TASK_ID1,
            application_id=TWITTER_APPLICATION_ID1,
        )

        self.request = Request.create(
            args={
                'url': 'https://api.twitter.com/1.1/account/verify_credentials.json',
                'retpath': '/internal/twitter_auth/',
                'consumer': CONSUMER1,
            },
            consumer_ip=CONSUMER_IP1,
        )

        self.proxylib_response.return_value = ProxyResponse(
            {
                'Authorization': 'OAuth oauth_consumer_key="htWyCLrQ2T33tb96BfEKAg",'
                'oauth_nonce="391756225",oauth_signature="8PbYvLZhE2xKBsN4OMJYMDFGKY0%3D",'
                'oauth_signature_method="HMAC-SHA1",oauth_timestamp="1396276816",'
                'oauth_token="14463954-VJe45F4FyrKAVmULs00000000000000",oauth_version="1.0"',
            },
            None,
        )

        response = sign_request(self.request, task_id=TASK_ID1)
        eq_(response.status_code, 307)
        eq_(response.data, '')

        header = response.headers['X-Accel-Redirect']

        eq_(header, ('/internal/twitter_auth/Authorization=OAuth%20oauth_consumer_key%3D%22htWyCLrQ2T33tb96BfEKAg'
                     '%22%2Coauth_nonce%3D%22391756225%22%2Coauth_signature%3D%228PbYvLZhE2xKBsN4OMJYMDFGKY0%253D%22'
                     '%2Coauth_signature_method%3D%22HMAC-SHA1%22%2Coauth_timestamp%3D%221396276816%22%2Coauth_token'
                     '%3D%2214463954-VJe45F4FyrKAVmULs00000000000000%22%2Coauth_version%3D%221.0%22/url=https%3A%2F'
                     '%2Fapi.twitter.com%2F1.1%2Faccount%2Fverify_credentials.json'))


class TestFriendsView(BaseTestCase):
    def setUp(self):
        super(TestFriendsView, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['friends'] + self.application_grants,
        )
        self._setup_statbox_templates()

    def tearDown(self):
        super(TestFriendsView, self).tearDown()

    def test_facebook_simple_userid(self):
        self._setup_master_profile()
        self._setup_friend_profile()

        rv = self._make_request(profile_id=PROFILE_ID1, yandex_profiles='1')

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['raw_response'], facebook_test.GraphApi.get_friends([{'id': SIMPLE_USERID2}]).value)
        eq_(rv['result']['friends'][0]['userid'], SIMPLE_USERID2)

        yandex_profiles = rv['result']['friends'][0]['yandex_profiles']
        eq_(
            yandex_profiles[0],
            {
                'profile_id': PROFILE_ID2,
                'uid': UID2,
                'userid': get_business_userid(FACEBOOK_BUSINESS_ID, BUSINESS_TOKEN1),
                'username': USERNAME2,
            },
        )

        self._fake_statbox_friends.assert_equals([
            self._fake_statbox_friends.entry('get_friends'),
        ])

    def test_friends_to_statbox__no_friends(self):
        context = dict(
            profile=FakeProfile(
                provider_id=Twitter.id,
                username=None,
                uid=UID1,
                userid=SIMPLE_USERID1,
                profile_id=None,
            ),
            consumer=CONSUMER1,
            provider=providers.get_provider_info_by_id(Twitter.id),
        )

        _friends_to_statbox(context, friends=list(), with_yandex_profiles=True)

        self._fake_statbox_friends.assert_equals([
            self._fake_statbox_friends.entry(
                'get_friends',
                provider='twitter',
                userid=SIMPLE_USERID1,
                friends_userids='',
                friends_uids='',
            ),
        ])

    def test_friends_to_statbox__many_friends(self):
        context = dict(
            profile=FakeProfile(
                provider_id=Twitter.id,
                username=None,
                uid=UID1,
                userid=SIMPLE_USERID1,
                profile_id=None,
            ),
            consumer=CONSUMER1,
            provider=providers.get_provider_info_by_id(Twitter.id),
        )
        friends = [
            dict(
                userid=SIMPLE_USERID2,
                yandex_profiles=[
                    dict(uid=UID2),
                    dict(uid=UID3),
                ],
            ),
            dict(
                userid=SIMPLE_USERID3,
                yandex_profiles=[],
            ),
        ]

        _friends_to_statbox(context, friends, with_yandex_profiles=True)

        self._fake_statbox_friends.assert_equals([
            self._fake_statbox_friends.entry(
                'get_friends',
                provider='twitter',
                userid=SIMPLE_USERID1,
                friends_userids='%s,%s,%s' % (SIMPLE_USERID2, SIMPLE_USERID2, SIMPLE_USERID3),
                friends_uids='%s,%s,%s' % (UID2, UID3, ''),
            ),
        ])

    def test_friends_to_statbox__many_friends__no_profiles_needed(self):
        context = dict(
            profile=FakeProfile(
                provider_id=Twitter.id,
                username=None,
                uid=UID1,
                userid=SIMPLE_USERID1,
                profile_id=None,
            ),
            consumer=CONSUMER1,
            provider=providers.get_provider_info_by_id(Twitter.id),
        )
        friends = [
            dict(
                userid=SIMPLE_USERID2,
                yandex_profiles=[
                    dict(uid=UID2),
                    dict(uid=UID3),
                ],
            ),
            dict(
                userid=SIMPLE_USERID3,
                yandex_profiles=[],
            ),
        ]

        _friends_to_statbox(context, friends, with_yandex_profiles=False)

        self._fake_statbox_friends.assert_equals([
            self._fake_statbox_friends.entry(
                'get_friends',
                provider='twitter',
                userid=SIMPLE_USERID1,
                friends_userids='%s,%s' % (SIMPLE_USERID2, SIMPLE_USERID3),
                friends_uids_enabled='0',
                friends_uids='',
            ),
        ])

    def test_friends_to_statbox__no_profile(self):
        context = dict(
            profile=None,
            consumer=CONSUMER1,
            provider=providers.get_provider_info_by_id(Twitter.id),
        )

        _friends_to_statbox(context, friends=list(), with_yandex_profiles=True)

        self._fake_statbox_friends.assert_equals([])

    def test_friends_to_statbox__no_uid(self):
        context = dict(
            profile=FakeProfile(
                provider_id=Twitter.id,
                username=None,
                uid=None,
                userid=SIMPLE_USERID1,
                profile_id=None,
            ),
            consumer=CONSUMER1,
            provider=providers.get_provider_info_by_id(Twitter.id),
        )

        _friends_to_statbox(context, friends=list(), with_yandex_profiles=True)

        self._fake_statbox_friends.assert_equals([])

    def test_friends_to_statbox__escape_commas(self):
        context = dict(
            profile=FakeProfile(
                provider_id=Twitter.id,
                username=None,
                uid=UID1,
                userid=SIMPLE_USERID1,
                profile_id=None,
            ),
            consumer=CONSUMER1,
            provider=providers.get_provider_info_by_id(Twitter.id),
        )
        friends = [
            dict(
                userid='user,id\\1',
                yandex_profiles=[
                    dict(uid='uid,\\1'),
                    dict(uid='uid2'),
                ],
            ),
        ]

        _friends_to_statbox(context, friends, with_yandex_profiles=True)

        self._fake_statbox_friends.assert_equals([
            self._fake_statbox_friends.entry(
                'get_friends',
                provider='twitter',
                userid=SIMPLE_USERID1,
                friends_userids='%s,%s' % ('user\\\\,id\\\\\\\\1', 'user\\\\,id\\\\\\\\1'),
                friends_uids='%s,%s' % ('uid\\\\,\\\\\\\\1', 'uid2'),
            ),
        ])

    def test_friends_to_statbox__lot_of_friends(self):
        context = dict(
            profile=FakeProfile(
                provider_id=Twitter.id,
                username=None,
                uid=UID1,
                userid=SIMPLE_USERID1,
                profile_id=None,
            ),
            consumer=CONSUMER1,
            provider=providers.get_provider_info_by_id(Twitter.id),
        )
        LOT_OF_USERIDS = range(1, 2000)
        friends = [dict(userid=u, yandex_profiles=[dict(uid=u)]) for u in LOT_OF_USERIDS]

        _friends_to_statbox(context, friends, with_yandex_profiles=True)

        self._fake_statbox_friends.assert_equals([
            self._fake_statbox_friends.entry(
                'get_friends',
                provider='twitter',
                userid=SIMPLE_USERID1,
                friends_userids=','.join(map(str, LOT_OF_USERIDS)),
                friends_uids=','.join(map(str, LOT_OF_USERIDS)),
            ),
        ])

    def _make_request(self, profile_id, yandex_profiles=None):
        query_dict = {}

        if yandex_profiles:
            query_dict['yandex_profiles'] = yandex_profiles

        return self._client.get(
            '/proxy2/profile/%d/friends' % profile_id,
            query_string=query_dict,
            environ_base={'REMOTE_ADDR': CONSUMER_IP1},
        )

    def _setup_master_profile(self):
        queries = [
            insert(pt).values({
                'profile_id': PROFILE_ID1,
                'uid': UID1,
                'provider_id': Facebook.id,
                'userid': SIMPLE_USERID1,
                'allow_auth': 1,
                'referer': 1,
                'username': USERNAME1,
                'yandexuid': YANDEXUID1,
            }),
            insert(tt).values({
                'uid': UID1,
                'profile_id': PROFILE_ID1,
                'application_id': FACEBOOK_APPLICATION_ID1,
                'value': APPLICATION_TOKEN1,
                'value_hash': TokenRecord.eval_value_hash(APPLICATION_TOKEN1),
            }),
            insert(bamt).values({
                'business_id': FACEBOOK_BUSINESS_ID,
                'business_token': BUSINESS_TOKEN2,
                'application_id': FACEBOOK_APPLICATION_ID1,
                'userid': SIMPLE_USERID1,
            }),
        ]
        db = self._fake_db.get_engine()
        for query in queries:
            execute(db, query)

        self._fake_facebook.set_response_value(
            'get_friends',
            facebook_test.GraphApi.get_friends([{'id': SIMPLE_USERID2}]),
        )

    def _setup_friend_profile(self):
        queries = [
            insert(bamt).values({
                'business_id': FACEBOOK_BUSINESS_ID,
                'business_token': BUSINESS_TOKEN1,
                'application_id': FACEBOOK_APPLICATION_ID1,
                'userid': SIMPLE_USERID2,
            }),
            insert(pt).values({
                'profile_id': PROFILE_ID2,
                'uid': UID2,
                'provider_id': Facebook.id,
                'userid': get_business_userid(FACEBOOK_BUSINESS_ID, BUSINESS_TOKEN1),
                'allow_auth': 1,
                'referer': 1,
                'username': USERNAME2,
                'yandexuid': YANDEXUID2,
            }),
        ]
        db = self._fake_db.get_engine()
        for query in queries:
            execute(db, query)

    def _setup_statbox_templates(self):
        self._fake_statbox_friends.bind_entry(
            'get_friends',
            action='get_friends',
            consumer=CONSUMER1,
            uid=str(UID1),
            provider='facebook',
            userid=get_business_userid(FACEBOOK_BUSINESS_ID, BUSINESS_TOKEN2),
            friends_userids=get_business_userid(FACEBOOK_BUSINESS_ID, BUSINESS_TOKEN1),
            friends_uids_enabled='1',
            friends_uids=str(UID2),
        )


class TestProfileView(BaseTestCase):
    def setUp(self):
        super(TestProfileView, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['profile'] + self.application_grants,
        )

    def build_settings(self):
        settings = super(TestProfileView, self).build_settings()
        settings['social_config'].update(
            dict(
                yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
                yandex_get_profile_url='https://login.yandex.ru/info',
            ),
        )
        return settings

    def test_yandex__ok(self):
        self._fake_yandex.set_response_value(
            'get_profile',
            yandex_test.YandexApi.get_profile(),
        )

        rv = self._make_request(application=YANDEX_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(
            rv['result'],
            {
                'account': {
                    'userid': '12345',
                    'username': 'Ivanov the Best',
                    'person': {
                        'name': {'first': 'Иван', 'last': 'Иванов'},
                        'birthdate': '1931-05-28',
                        'email': 'ivan@yandex.ru',
                        'gender': 'm',
                        'avatar': {
                            '16x16': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/mini',
                            '25x25': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/small',
                            '28x28': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-small',
                            '34x34': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-34',
                            '42x42': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-middle',
                            '50x50': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-50',
                            '56x56': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-retina-small',
                            '68x68': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-68',
                            '75x75': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-75',
                            '84x84': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-retina-middle',
                            '100x100': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-retina-50',
                            '150x150': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-150',
                            '200x200': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-200',
                            '300x300': 'https://avatars.mds.yandex.net/get-yapic/4321/12345-123456/islands-300',
                        },
                    },
                },
                'addresses': [],
            },
        )
        eq_(rv['raw_response'], yandex_test.YandexApi.get_profile().value)

    def test_yandex__error(self):
        self._fake_yandex.set_response_value(
            'get_profile',
            yandex_test.YandexApi.build_error(),
        )

        rv = self._make_request(application=YANDEX_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['task']['state'], 'failure')

        eq_(
            rv['task']['reason'],
            {
                'code': 'invalid_token',
                'type': 'external',
                'description': 'User cannot be authenticated using existing tokens',
                'message': '',
            },
        )

    def test_mail_ru_o2__ok(self):
        self._fake_mail_ru.set_response_value(
            'get_profile',
            mail_ru_test.MailRuO2Api.get_profile(),
        )

        rv = self._make_request(application=MAIL_RU_APPLICATION_NAME2)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(
            rv['result'],
            {
                'account': {
                    'userid': SIMPLE_USERID1,
                    'username': 'ivanov@mail.ru',
                    'person': {
                        'email': 'ivanov@mail.ru',
                        'name': {
                            'last': 'Иванов',
                            'first': 'Иван',
                        },
                        'gender': 'm',
                    },
                },
                'addresses': ['http://my.mail.ru/mail/ivanov'],
            },
        )
        eq_(rv['raw_response'], mail_ru_test.MailRuO2Api.get_profile().value)

    def test_mail_ru_o2__error(self):
        self._fake_mail_ru.set_response_value(
            'get_profile',
            mail_ru_test.MailRuO2Api.build_error(),
        )

        rv = self._make_request(application=MAIL_RU_APPLICATION_NAME2)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['task']['state'], 'failure')

        eq_(
            rv['task']['reason'],
            {
                'type': 'external',
                'code': 'invalid_token',
                'message': 'token not found',
                'description': 'User cannot be authenticated using existing tokens',
            },
        )

    def test_deezer__ok(self):
        self._fake_deezer.set_response_value(
            'get_profile',
            deezer_test.DeezerApi.get_profile(),
        )

        rv = self._make_request(application=DEEZER_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(
            rv['result'],
            {
                'account': {
                    'userid': SIMPLE_USERID1,
                    'username': USERNAME1,
                    'person': {
                        'email': EMAIL1,
                        'name': {
                            'last': 'Иванов',
                            'first': 'Иван',
                        },
                        'birthdate': '1931-05-28',
                        'gender': 'm',
                    },
                },
                'addresses': ['https://www.deezer.com/profile/' + SIMPLE_USERID1],
            },
        )
        eq_(rv['raw_response'], deezer_test.DeezerApi.get_profile().value)

    def test_deezer__zero_birthdate(self):
        self._fake_deezer.set_response_value(
            'get_profile',
            deezer_test.DeezerApi.get_profile({'birthday': '0000-00-00'}),
        )

        rv = self._make_request(application=DEEZER_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        birthdate = rv['result']['account']['person']['birthdate']
        eq_(birthdate, '0000-00-00')

    def test_deezer__error(self):
        self._fake_deezer.set_response_value(
            'get_profile',
            deezer_test.DeezerApi.build_error(),
        )

        rv = self._make_request(application=DEEZER_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['task']['state'], 'failure')

        eq_(
            rv['task']['reason'],
            {
                'type': 'external',
                'code': 'permission_error',
                'message': 'Blabla blablabla labla alabla',
                'description': 'There is no token with sufficient permissions to complete the request',
            },
        )

    def test_mts_belarus__ok(self):
        self._fake_mts_belarus.set_response_value(
            'get_profile',
            mts_belarus_test.MtsBelarusApi.get_profile(),
        )

        rv = self._make_request(application=MTS_BELARUS_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(
            rv['result'],
            {
                'account': {
                    'userid': '375299999999:123456789000',
                    'person': {
                        'phone_number': '+375299999999',
                    },
                },
                'addresses': [],
            },
        )
        eq_(rv['raw_response'], mts_belarus_test.MtsBelarusApi.get_profile().value)

    def test_mts_belarus__invalid_token(self):
        self._fake_mts_belarus.set_response_value(
            'get_profile',
            mts_belarus_test.MtsBelarusApi.build_error(http_status_code=401),
        )

        rv = self._make_request(application=MTS_BELARUS_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['task']['state'], 'failure')

        eq_(
            rv['task']['reason'],
            {
                'type': 'external',
                'code': 'invalid_token',
                'message': '',
                'description': 'User cannot be authenticated using existing tokens',
            },
        )

    def _make_request(self, application=YANDEX_APPLICATION_NAME1, application_token=APPLICATION_TOKEN1):
        headers = {'X-Social-Access-Token-Value': application_token}
        return self._client.get(
            '/proxy2/token',
            query_string={'application': application},
            headers=headers,
            environ_base={'REMOTE_ADDR': CONSUMER_IP1},
        )


class TestTokenView(BaseTestCase):
    def setUp(self):
        super(TestTokenView, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['refresh_token'] + self.application_grants,
        )

    def test_mail_ru__ok(self):
        self._fake_mail_ru.set_response_value(
            'refresh_token',
            mail_ru_test.MailRuApi.refresh_token(),
        )

        rv = self._make_request()

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(
            rv['result'],
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
                'refresh_token': REFRESH_TOKEN1,
            },
        )
        eq_(rv['raw_response'], mail_ru_test.MailRuApi.refresh_token().value)

    def test_mail_ru__invalid_refresh_token(self):
        self._fake_mail_ru.set_response_value(
            'refresh_token',
            oauth2.test.build_error(error='invalid_request'),
        )

        rv = self._make_request()

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['task']['state'], 'failure')

        eq_(
            rv['task']['reason'],
            {
                'type': 'external',
                'code': 'invalid_token',
                'message': '',
                'description': 'User cannot be authenticated using existing tokens',
            },
        )

    def test_google__ok(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.refresh_token(),
        )

        rv = self._make_request(application=GOOGLE_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(
            rv['result'],
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
            },
        )
        eq_(rv['raw_response'], google_test.GoogleApi.refresh_token().value)

    def test_google__invalid_refresh_token(self):
        self._fake_google.set_response_value(
            'refresh_token',
            oauth2.test.build_error(error='invalid_grant', error_description='Bad Request'),
        )

        rv = self._make_request(application=GOOGLE_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['task']['state'], 'failure')

        eq_(
            rv['task']['reason'],
            {
                'type': 'external',
                'code': 'invalid_token',
                'message': 'Bad Request',
                'description': 'User cannot be authenticated using existing tokens',
            },
        )

    def test_microsoft__ok(self):
        self._fake_microsoft.set_response_value(
            'refresh_token',
            microsoft_test.MicrosoftApi.refresh_token(),
        )

        rv = self._make_request(application=MICROSOFT_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(
            rv['result'],
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
                'refresh_token': REFRESH_TOKEN1,
            },
        )
        eq_(rv['raw_response'], microsoft_test.MicrosoftApi.refresh_token().value)

    def test_microsoft__invalid_reshresh_token(self):
        self._fake_microsoft.set_response_value(
            'refresh_token',
            oauth2.test.build_error(
                error='invalid_grant',
                error_description="The provided value for the input parameter 'refresh_token' is not valid.",
            ),
        )

        rv = self._make_request(application=MICROSOFT_APPLICATION_NAME1)

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)

        eq_(rv['task']['state'], 'failure')

        eq_(
            rv['task']['reason'],
            {
                'type': 'external',
                'code': 'invalid_token',
                'message': "The provided value for the input parameter 'refresh_token' is not valid.",
                'description': 'User cannot be authenticated using existing tokens',
            },
        )

    def _make_request(self, application=MAIL_RU_APPLICATION_NAME1):
        return self._client.post(
            '/proxy2/application/%s/refresh_token' % application,
            data={'refresh_token': REFRESH_TOKEN1},
            environ_base={'REMOTE_ADDR': CONSUMER_IP1},
        )
