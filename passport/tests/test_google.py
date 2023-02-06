# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)
import json

from nose.tools import eq_
from passport.backend.social.common.application import application_eav_configuration
from passport.backend.social.common.chrono import now
from passport.backend.social.common.eav import EavSelector
from passport.backend.social.common.exception import NetworkProxylibError
from passport.backend.social.common.profile import create_profile
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import save_refresh_token
from passport.backend.social.common.task import (
    build_provider_for_task,
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN4,
    APPLICATION_TOKEN_TTL1,
    CONSUMER1,
    GOOGLE_APPLICATION_ID1,
    GOOGLE_APPLICATION_NAME1,
    SIMPLE_USERID1,
    TASK_ID1,
    UID1,
    UNIXTIME1,
    YANDEXUID1,
)
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.sql import (
    SelectProfileByProfileIdDataQuery,
    SelectRefreshTokenByTokenIdDataQuery,
    SelectRefreshTokensByTokenIdsDataQuery,
    SelectTokenByTokenIdDataQuery,
    SelectTokensForProfileDataQuery,
    UpdateTokenDataQuery,
)
from passport.backend.social.common.test.types import (
    ApproximateFloat,
    DatetimeNow,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import save_token
from passport.backend.social.proxy2.test import TestCase
from passport.backend.social.proxylib.test import google as google_test


class GoogleTestCase(TestCase):
    def setUp(self):
        super(GoogleTestCase, self).setUp()
        self._fake_grants_config = FakeGrantsConfig().start()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=['127.0.0.1'],
            grants=[
                'profile',
                'no-cred-use-token',
            ],
        )

    def tearDown(self):
        self._fake_grants_config.stop()
        super(GoogleTestCase, self).tearDown()

    def _make_request_by_profile(self):
        return self._client.get('/proxy2/profile/1', environ_base={'REMOTE_ADDR': '127.0.0.1'})

    def _make_request_by_task_id(self):
        return self._client.get(
            '/proxy2/task/%s' % TASK_ID1,
            query_string={'consumer': CONSUMER1},
            environ_base={'REMOTE_ADDR': '127.0.0.1'},
        )

    def _make_request_by_token(self):
        return self._client.get(
            '/proxy2/token',
            query_string={'application': GOOGLE_APPLICATION_NAME1},
            headers={'X-Social-Access-Token-Value': APPLICATION_TOKEN1},
            environ_base={'REMOTE_ADDR': '127.0.0.1'},
        )

    def _assert_ok_response(self, rv, expected, status_code=200):
        eq_(rv.status_code, status_code)
        rv = json.loads(rv.data)
        eq_(rv, expected)

    def _assert_invalid_token_error_response(self, rv, message='Invalid Credentials'):
        self._assert_ok_response(
            rv,
            {
                'task': {
                    'state': 'failure',
                    'runtime': ApproximateFloat(0.1),
                    'provider': 'google',
                    'reason': {
                        'type': 'external',
                        'code': 'invalid_token',
                        'description': 'User cannot be authenticated using existing tokens',
                        'message': message,
                    },
                },
            },
        )

    def _assert_no_tokens_error_response(self, rv):
        self._assert_ok_response(
            rv,
            {
                'task': {
                    'state': 'failure',
                    'runtime': ApproximateFloat(0.1),
                    'provider': 'google',
                    'reason': {
                        'type': 'external',
                        'code': 'no_tokens_found',
                        'description': 'There are no tokens for the profile',
                        'message': '',
                    },
                },
            },
        )

    def _assert_internal_error_response(self, rv):
        self._assert_ok_response(
            rv,
            {
                'task': {
                    'state': 'failure',
                    'runtime': ApproximateFloat(0.1),
                    'provider': 'google',
                    'reason': {
                        'type': 'internal',
                        'code': 'internal_error',
                        'message': 'Unhandled exception',
                        'description': 'Something went wrong',
                    },
                },
            },
            status_code=500,
        )

    def _assert_api_error_response(self, rv):
        self._assert_ok_response(
            rv,
            {
                'task': {
                    'state': 'failure',
                    'runtime': ApproximateFloat(0.1),
                    'provider': 'google',
                    'reason': {
                        'type': 'external',
                        'code': 'api_error',
                        'message': '',
                        'description': '',
                    },
                },
            },
        )


class TestGoogleWithRefreshToken(GoogleTestCase):
    def setUp(self):
        super(TestGoogleWithRefreshToken, self).setUp()

        with self._fake_db.no_recording():
            token = Token(
                application_id=GOOGLE_APPLICATION_ID1,
                value=APPLICATION_TOKEN1,
                scopes=['foo', 'bar'],
                expired=now() - timedelta(hours=1),
            )
            create_profile(
                self._fake_db.get_engine(),
                self._fake_db.get_engine(),
                UID1,
                {
                    'provider': {'code': Google.code},
                    'userid': SIMPLE_USERID1,
                },
                token,
                UNIXTIME1,
                CONSUMER1,
                YANDEXUID1,
                refresh_token=RefreshToken(value=APPLICATION_TOKEN2, expired=None, scopes=['foo', 'bar']),
            )

    def test_ok(self):
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.get_profile(),
        )
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.refresh_token(APPLICATION_TOKEN3),
        )

        rv = self._make_request_by_profile()

        self._assert_ok_response(
            rv,
            {
                'result': {
                    'account': {'userid': SIMPLE_USERID1},
                    'addresses': ['https://plus.google.com/%s' % SIMPLE_USERID1],
                },
                'task': {
                    'state': 'success',
                    'runtime': ApproximateFloat(0.1),
                    'provider': 'google',
                    'profile_id': 1,
                },
                'raw_response': google_test.GoogleApi.get_profile().value,
            },
        )

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            UpdateTokenDataQuery(
                token_id=1,
                value=APPLICATION_TOKEN3,
                scope='bar,foo',
                expired=DatetimeNow() + timedelta(seconds=APPLICATION_TOKEN_TTL1),
                profile_id=1,
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
        ])

    def test_refreshed_token_not_changed__miss_scopes(self):
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.build_invalid_token_error(),
        )
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.refresh_token(APPLICATION_TOKEN1),
        )

        rv = self._make_request_by_profile()

        self._assert_invalid_token_error_response(rv)

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            UpdateTokenDataQuery(
                token_id=1,
                value=APPLICATION_TOKEN1,
                scope='bar,foo',
                profile_id=1,
                expired=DatetimeNow() + timedelta(seconds=APPLICATION_TOKEN_TTL1),
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
        ])

    def test_miss_scopes(self):
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.build_invalid_token_error(),
        )
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.refresh_token(APPLICATION_TOKEN3),
        )

        rv = self._make_request_by_profile()

        self._assert_invalid_token_error_response(rv)

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            UpdateTokenDataQuery(
                token_id=1,
                value=APPLICATION_TOKEN3,
                scope='bar,foo',
                expired=DatetimeNow() + timedelta(seconds=APPLICATION_TOKEN_TTL1),
                profile_id=1,
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
        ])

    def test_invalid_refresh_token(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.build_invalid_grant_error(),
        )

        rv = self._make_request_by_profile()

        self._assert_invalid_token_error_response(rv, message='')

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
        ])

    def test_refresh_network_fail(self):
        self._fake_google.set_response_value('refresh_token', NetworkProxylibError())

        rv = self._make_request_by_profile()

        self._assert_api_error_response(rv)

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
        ])

    def test_refresh_unknown_fail(self):
        self._fake_google.set_response_value('refresh_token', Exception())

        rv = self._make_request_by_profile()

        self._assert_internal_error_response(rv)

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
        ])

    def test_request_by_task_id(self):
        task = Task()
        task.consumer = CONSUMER1
        task.profile = dict(userid=SIMPLE_USERID1)
        provider_info = providers.get_provider_info_by_name(Google.code)
        task.provider = build_provider_for_task(
            code=provider_info['code'],
            name=provider_info['name'],
            id=provider_info['id'],
        )
        task.access_token = dict(value=APPLICATION_TOKEN1, scope='foo,bar')
        with self._fake_db.no_recording():
            task.application = providers.get_application_by_name(GOOGLE_APPLICATION_NAME1)
        save_task_to_redis(self._fake_redis, TASK_ID1, task)

        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.build_invalid_token_error(),
        )

        rv = self._make_request_by_task_id()

        self._assert_invalid_token_error_response(rv)
        self._fake_db.assert_executed_queries_equal([
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
        ])

    def test_request_by_token(self):
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.build_invalid_token_error(),
        )

        rv = self._make_request_by_token()

        self._assert_invalid_token_error_response(rv)
        self._fake_db.assert_executed_queries_equal([
            EavSelector(application_eav_configuration, ['application_name']).index_query([GOOGLE_APPLICATION_NAME1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
        ])


class TestGoogleNoRefreshToken(GoogleTestCase):
    def setUp(self):
        super(TestGoogleNoRefreshToken, self).setUp()

        with self._fake_db.no_recording():
            token = Token(
                application_id=GOOGLE_APPLICATION_ID1,
                value=APPLICATION_TOKEN1,
                scopes=['foo', 'bar'],
                expired=now() - timedelta(hours=1),
            )
            create_profile(
                self._fake_db.get_engine(),
                self._fake_db.get_engine(),
                UID1,
                {
                    'provider': {'code': Google.code},
                    'userid': SIMPLE_USERID1,
                },
                token,
                UNIXTIME1,
                CONSUMER1,
                YANDEXUID1,
            )

    def test_ok(self):
        rv = self._make_request_by_profile()

        self._assert_no_tokens_error_response(rv)

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
        ])


class TestGoogleWithManyRefreshTokensOneTokenExpired(GoogleTestCase):
    def setUp(self):
        super(TestGoogleWithManyRefreshTokensOneTokenExpired, self).setUp()

        with self._fake_db.no_recording():
            token = Token(
                application_id=GOOGLE_APPLICATION_ID1,
                value=APPLICATION_TOKEN1,
                scopes=['foo', 'bar'],
                expired=now() - timedelta(hours=1),
            )
            create_profile(
                self._fake_db.get_engine(),
                self._fake_db.get_engine(),
                UID1,
                {
                    'provider': {'code': Google.code},
                    'userid': SIMPLE_USERID1,
                },
                token,
                UNIXTIME1 + 1,
                CONSUMER1,
                YANDEXUID1,
                refresh_token=RefreshToken(value=APPLICATION_TOKEN2, expired=None, scopes=['foo', 'bar']),
            )

            save_token(
                Token(
                    uid=UID1,
                    profile_id=1,
                    application_id=GOOGLE_APPLICATION_ID1,
                    value=APPLICATION_TOKEN3,
                    secret=None,
                    scopes=['foo'],
                    expired=None,
                    created=datetime.fromtimestamp(UNIXTIME1),
                    verified=datetime.fromtimestamp(UNIXTIME1),
                    confirmed=datetime.fromtimestamp(UNIXTIME1),
                ),
                self._fake_db.get_engine(),
            )
            save_refresh_token(
                RefreshToken(
                    token_id=2,
                    value=APPLICATION_TOKEN4,
                    expired=None,
                    scopes=['bar'],
                ),
                self._fake_db.get_engine(),
            )

    def test_refresh_token_invalid(self):
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.build_invalid_token_error(),
        )
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.build_invalid_grant_error(),
        )

        rv = self._make_request_by_profile()

        self._assert_invalid_token_error_response(rv)

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokensByTokenIdsDataQuery([1]).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
        ])

    def test_refresh_network_fail(self):
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.build_invalid_token_error(),
        )
        self._fake_google.set_response_value('refresh_token', NetworkProxylibError())

        rv = self._make_request_by_profile()

        self._assert_api_error_response(rv)

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokensByTokenIdsDataQuery([1]).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
        ])

    def _assert_ok_profile_response(self, rv):
        self._assert_ok_response(
            rv,
            {
                'result': {
                    'account': {'userid': SIMPLE_USERID1},
                    'addresses': ['https://plus.google.com/%s' % SIMPLE_USERID1],
                },
                'raw_response': google_test.GoogleApi.get_profile().value,
                'task': {
                    'state': 'success',
                    'runtime': ApproximateFloat(0.1),
                    'provider': 'google',
                    'profile_id': 1,
                },
            },
        )


class TestGoogleWithManyRefreshTokensAllTokensExpired(GoogleTestCase):
    def setUp(self):
        super(TestGoogleWithManyRefreshTokensAllTokensExpired, self).setUp()

        with self._fake_db.no_recording():
            token = Token(
                application_id=GOOGLE_APPLICATION_ID1,
                value=APPLICATION_TOKEN1,
                scopes=['foo', 'bar'],
                expired=now() - timedelta(hours=1),
            )
            create_profile(
                self._fake_db.get_engine(),
                self._fake_db.get_engine(),
                UID1,
                {
                    'provider': {'code': Google.code},
                    'userid': SIMPLE_USERID1,
                },
                token,
                UNIXTIME1 + 1,
                CONSUMER1,
                YANDEXUID1,
                refresh_token=RefreshToken(value=APPLICATION_TOKEN2, expired=None, scopes=['foo', 'bar']),
            )

            save_token(
                Token(
                    uid=UID1,
                    profile_id=1,
                    application_id=GOOGLE_APPLICATION_ID1,
                    value=APPLICATION_TOKEN3,
                    secret=None,
                    scopes=['foo'],
                    expired=now() - timedelta(hours=1),
                    created=datetime.fromtimestamp(UNIXTIME1),
                    verified=datetime.fromtimestamp(UNIXTIME1),
                    confirmed=datetime.fromtimestamp(UNIXTIME1),
                ),
                self._fake_db.get_engine(),
            )
            save_refresh_token(
                RefreshToken(
                    token_id=2,
                    value=APPLICATION_TOKEN4,
                    expired=None,
                    scopes=['bar'],
                ),
                self._fake_db.get_engine(),
            )

    def test_all_refresh_tokens_invalid(self):
        self._fake_google.set_response_values(
            'refresh_token',
            [
                google_test.GoogleApi.build_invalid_grant_error(),
                google_test.GoogleApi.build_invalid_grant_error(),
            ],
        )

        rv = self._make_request_by_profile()

        self._assert_invalid_token_error_response(rv, message='')

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokensByTokenIdsDataQuery([2, 1]).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(2).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(2).to_sql(),
        ])

    def test_last_refresh_token_valid(self):
        self._fake_google.set_response_values(
            'refresh_token',
            [
                google_test.GoogleApi.build_invalid_grant_error(),
                google_test.GoogleApi.refresh_token(APPLICATION_TOKEN3),
            ],
        )
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.get_profile(),
        )

        rv = self._make_request_by_profile()

        self._assert_ok_response(
            rv,
            {
                'result': {
                    'account': {'userid': SIMPLE_USERID1},
                    'addresses': ['https://plus.google.com/%s' % SIMPLE_USERID1],
                },
                'task': {
                    'state': 'success',
                    'runtime': ApproximateFloat(0.1),
                    'provider': 'google',
                    'profile_id': 1,
                },
                'raw_response': google_test.GoogleApi.get_profile().value,
            },
        )

        self._fake_db.assert_executed_queries_equal([
            SelectProfileByProfileIdDataQuery(1).to_sql(),
            SelectTokensForProfileDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokensByTokenIdsDataQuery([2, 1]).to_sql(),
            SelectTokenByTokenIdDataQuery(1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            SelectTokenByTokenIdDataQuery(2).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(2).to_sql(),
            UpdateTokenDataQuery(
                token_id=2,
                value=APPLICATION_TOKEN3,
                scope='foo',
                expired=DatetimeNow() + timedelta(seconds=APPLICATION_TOKEN_TTL1),
                profile_id=1,
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
        ])
