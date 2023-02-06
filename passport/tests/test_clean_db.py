# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)

from passport.backend.core import Undefined
from passport.backend.social.common.application import application_eav_configuration
from passport.backend.social.common.chrono import (
    datetime_to_unixtime,
    now,
)
from passport.backend.social.common.db.schemas import (
    profile_table,
    refresh_token_table,
    token_table,
)
from passport.backend.social.common.eav import EavSelector
from passport.backend.social.common.exception import (
    CaptchaNeededProxylibError,
    NetworkProxylibError,
    ProviderCommunicationProxylibError,
    ProviderUnknownProxylibError,
)
from passport.backend.social.common.profile import create_profile
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import (
    find_refresh_token_by_token_id,
    save_refresh_token,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_NAME1,
    APPLICATION_NAME2,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN_TTL1,
    BUSINESS_USERID1,
    EXTERNAL_APPLICATION_ID1,
    FACEBOOK_APPLICATION_ID1,
    GOOGLE_APPLICATION_ID1,
    PROFILE_ID1,
    PROVIDER_CODE1,
    PROVIDER_ID1,
    SIMPLE_USERID1,
    UID1,
    UNIXTIME1,
    VKONTAKTE_APPLICATION_ID1,
    YANDEXUID1,
)
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
)
from passport.backend.social.common.test.sql import (
    SelectRefreshTokenByTokenIdDataQuery,
    UpdateTokenDataQuery,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import DatetimeNow
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import (
    find_token_by_token_id,
    save_token,
)
from passport.backend.social.proxylib.test import (
    facebook as facebook_test,
    google as google_test,
    vkontakte as vkontakte_test,
)
from passport.backend.social.utils.dbcleaner import clean_db
from passport.backend.social.utils.init import init


class CleanDbTestCase(TestCase):
    def setUp(self):
        super(CleanDbTestCase, self).setUp()
        self._fake_redis = FakeRedisClient()
        self._redis_patch = RedisPatch(self._fake_redis).start()
        init()

    def tearDown(self):
        self._redis_patch.stop()
        super(CleanDbTestCase, self).tearDown()

    def _build_token(self, application_id=VKONTAKTE_APPLICATION_ID1, expired=Undefined):
        if expired is Undefined:
            expired = now() - timedelta(seconds=1)

        return Token(
            uid=UID1,
            profile_id=PROFILE_ID1,
            application_id=application_id,
            value=APPLICATION_TOKEN1,
            secret=None,
            scopes=None,
            expired=expired,
            created=datetime.fromtimestamp(UNIXTIME1),
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )

    def _create_profile(self, profile_info, token, db=None, refresh_token=None):
        if db is None:
            db = self._fake_db.get_engine()
        return create_profile(
            mysql_read=db,
            mysql_write=db,
            profile_info=profile_info,
            refresh_token=refresh_token,
            timestamp=UNIXTIME1,
            token=token,
            uid=UID1,
            yandexuid=YANDEXUID1,
        )


class TestCleanDbSocialUserDisabled(CleanDbTestCase):
    def setUp(self):
        super(TestCleanDbSocialUserDisabled, self).setUp()

        profile_info = {'provider': {'code': Vkontakte.code}, 'userid': SIMPLE_USERID1}
        token = Token(
            application_id=VKONTAKTE_APPLICATION_ID1,
            value=APPLICATION_TOKEN1,
            expired=now() + timedelta(days=1),
        )
        with self._fake_db.no_recording() as db:
            self._create_profile(
                db=db,
                profile_info=profile_info,
                token=token,
            )
        self.token_id = token.token_id

        self._fake_vkontakte = vkontakte_test.FakeProxy()
        self._fake_vkontakte.start()

        self._fake_vkontakte.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.build_error(code=3610),
        )

    def tearDown(self):
        self._fake_vkontakte.stop()
        super(TestCleanDbSocialUserDisabled, self).tearDown()

    def test(self):
        clean_db(1)

        self.assertFalse(find_token_by_token_id(self.token_id, self._fake_db.get_engine()))


class TestCleanDbTokenExpired(CleanDbTestCase):
    def setUp(self):
        super(TestCleanDbTokenExpired, self).setUp()
        with self._fake_db.no_recording():
            save_token(
                Token(
                    uid=UID1,
                    profile_id=PROFILE_ID1,
                    application_id=VKONTAKTE_APPLICATION_ID1,
                    value=APPLICATION_TOKEN1,
                    secret=None,
                    scopes=None,
                    expired=now() - timedelta(seconds=1),
                    created=datetime.fromtimestamp(UNIXTIME1),
                    verified=datetime.fromtimestamp(UNIXTIME1),
                    confirmed=datetime.fromtimestamp(UNIXTIME1),
                ),
                self._fake_db.get_engine(),
            )

    def test_ok(self):
        clean_db(1)

        tt = token_table
        rtt = refresh_token_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([VKONTAKTE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([VKONTAKTE_APPLICATION_ID1]),
            rtt.delete().where(rtt.c.token_id.in_([1])),
            tt.delete().where(tt.c.token_id.in_([1])),
        ])


class TestCleanDbTokenLinkedWithMissingProfile(CleanDbTestCase):
    def setUp(self):
        super(TestCleanDbTokenLinkedWithMissingProfile, self).setUp()
        with self._fake_db.no_recording():
            save_token(
                Token(
                    uid=UID1,
                    profile_id=PROFILE_ID1,
                    application_id=VKONTAKTE_APPLICATION_ID1,
                    value=APPLICATION_TOKEN1,
                    secret=None,
                    scopes=None,
                    expired=None,
                    created=datetime.fromtimestamp(UNIXTIME1),
                    verified=datetime.fromtimestamp(UNIXTIME1),
                    confirmed=datetime.fromtimestamp(UNIXTIME1),
                ),
                self._fake_db.get_engine(),
            )

    def test_ok(self):
        clean_db(1)

        tt = token_table
        pt = profile_table
        rtt = refresh_token_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([VKONTAKTE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([VKONTAKTE_APPLICATION_ID1]),
            pt.select().where(pt.c.profile_id == PROFILE_ID1),
            rtt.delete().where(rtt.c.token_id.in_([1])),
            tt.delete().where(tt.c.token_id.in_([1])),
        ])


class TestCleanDbTokenFacebookToken(CleanDbTestCase):
    def setUp(self):
        super(TestCleanDbTokenFacebookToken, self).setUp()

        self._fake_facebook = facebook_test.FakeProxy()
        self._fake_facebook.start()

        self._token_expiration_unixtime = datetime_to_unixtime(now() + timedelta(hours=1))

        profile_info = {'provider': {'code': 'fb'}, 'userid': BUSINESS_USERID1}
        token = Token(
            application_id=FACEBOOK_APPLICATION_ID1,
            value=APPLICATION_TOKEN1,
            scopes=['hello'],
            expired=datetime.fromtimestamp(self._token_expiration_unixtime),
        )
        with self._fake_db.no_recording() as db:
            self._create_profile(
                db=db,
                profile_info=profile_info,
                token=token,
            )

    def tearDown(self):
        self._fake_facebook.stop()
        super(TestCleanDbTokenFacebookToken, self).tearDown()

    def test_ok(self):
        self._fake_facebook.set_response_value(
            'get_token_info',
            facebook_test.GraphApi.get_token_info({
                'scopes': ['hello'],
                'expires_at': self._token_expiration_unixtime,
            }),
        )

        clean_db(1)

        tt = token_table
        pt = profile_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([FACEBOOK_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([FACEBOOK_APPLICATION_ID1]),
            pt.select().where(pt.c.profile_id == PROFILE_ID1),
        ])

    def test_different_expiration_time_and_scopes(self):
        expiration_unixtime = datetime_to_unixtime(now() + timedelta(hours=2))
        self._fake_facebook.set_response_value(
            'get_token_info',
            facebook_test.GraphApi.get_token_info({
                'scopes': ['foo', 'yello'],
                'expires_at': expiration_unixtime,
            }),
        )

        clean_db(1)

        tt = token_table
        pt = profile_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([FACEBOOK_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([FACEBOOK_APPLICATION_ID1]),
            pt.select().where(pt.c.profile_id == PROFILE_ID1),
            UpdateTokenDataQuery(
                scope='foo,yello',
                expired=datetime.fromtimestamp(expiration_unixtime),
                token_id=1,
                value=APPLICATION_TOKEN1,
                profile_id=PROFILE_ID1,
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
        ])

    def test_different_expiration_time(self):
        expiration_time = datetime_to_unixtime(now() + timedelta(hours=2))
        self._fake_facebook.set_response_value(
            'get_token_info',
            facebook_test.GraphApi.get_token_info({
                'scopes': ['hello'],
                'expires_at': expiration_time,
            }),
        )

        clean_db(1)

        tt = token_table
        pt = profile_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([FACEBOOK_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([FACEBOOK_APPLICATION_ID1]),
            pt.select().where(pt.c.profile_id == PROFILE_ID1),
            UpdateTokenDataQuery(
                expired=datetime.fromtimestamp(expiration_time),
                token_id=1,
                value=APPLICATION_TOKEN1,
                profile_id=PROFILE_ID1,
                scope='hello',
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
        ])

    def test_different_scopes(self):
        self._fake_facebook.set_response_value(
            'get_token_info',
            facebook_test.GraphApi.get_token_info({
                'scopes': ['foo', 'yello'],
                'expires_at': self._token_expiration_unixtime,
            }),
        )

        clean_db(1)

        tt = token_table
        pt = profile_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([FACEBOOK_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([FACEBOOK_APPLICATION_ID1]),
            pt.select().where(pt.c.profile_id == PROFILE_ID1),
            UpdateTokenDataQuery(
                scope='foo,yello',
                token_id=1,
                value=APPLICATION_TOKEN1,
                expired=datetime.fromtimestamp(self._token_expiration_unixtime),
                profile_id=PROFILE_ID1,
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
        ])

    def test_network_fail(self):
        self._fake_facebook.set_response_value('get_token_info', NetworkProxylibError())
        clean_db(1)

    def test_unexpected_response(self):
        self._fake_facebook.set_response_value('get_token_info', ProviderCommunicationProxylibError())
        clean_db(1)

    def test_provider_unknown(self):
        self._fake_facebook.set_response_value('get_token_info', ProviderUnknownProxylibError())
        clean_db(1)

    def test_captcha_needed(self):
        self._fake_facebook.set_response_value('get_token_info', CaptchaNeededProxylibError())
        clean_db(1)

    def test_unexpected_exception(self):
        self._fake_facebook.set_response_value('get_token_info', Exception())
        clean_db(1)


class TestCleanDbTokenExpiredWithRefreshToken(CleanDbTestCase):
    def setUp(self):
        super(TestCleanDbTokenExpiredWithRefreshToken, self).setUp()
        self._fake_google = google_test.FakeProxy()
        self._fake_google.start()

        profile_info = {'provider': {'code': 'gg'}, 'userid': SIMPLE_USERID1}
        token = Token(
            application_id=GOOGLE_APPLICATION_ID1,
            value=APPLICATION_TOKEN1,
            expired=now() - timedelta(seconds=1),
        )
        refresh_token = RefreshToken(
            value=APPLICATION_TOKEN2,
            expired=None,
            scopes=None,
        )
        with self._fake_db.no_recording() as db:
            self._create_profile(
                db=db,
                profile_info=profile_info,
                token=token,
                refresh_token=refresh_token,
            )

    def tearDown(self):
        self._fake_google.stop()
        super(TestCleanDbTokenExpiredWithRefreshToken, self).tearDown()

    def test_refresh_token_invalid(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.build_invalid_grant_error(),
        )

        clean_db(1)

        tt = token_table
        rtt = refresh_token_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            rtt.delete().where(rtt.c.token_id.in_([1])),
            tt.delete().where(tt.c.token_id.in_([1])),
        ])

    def test_refresh_token_valid(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.refresh_token(APPLICATION_TOKEN3),
        )
        self._fake_google.set_response_value(
            'get_profile',
            google_test.GoogleApi.get_profile(),
        )

        clean_db(1)

        tt = token_table
        pt = profile_table
        self._fake_db.assert_executed_queries_equal([
            tt.select().where(tt.c.token_id > 0).order_by(tt.c.token_id).limit(1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([GOOGLE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([GOOGLE_APPLICATION_ID1]),
            SelectRefreshTokenByTokenIdDataQuery(1).to_sql(),
            UpdateTokenDataQuery(
                token_id=1,
                value=APPLICATION_TOKEN3,
                scope='',
                expired=DatetimeNow() + timedelta(seconds=APPLICATION_TOKEN_TTL1),
                profile_id=PROFILE_ID1,
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                created=datetime.fromtimestamp(UNIXTIME1),
            ).to_sql(),
            pt.select().where(pt.c.profile_id == PROFILE_ID1),
        ])


class TestCleanDbTokenRequestFromIntranetDenied(CleanDbTestCase):
    def build_settings(self):
        settings = super(TestCleanDbTokenRequestFromIntranetDenied, self).build_settings()
        settings['applications'] = [
            dict(
                application_id=APPLICATION_ID1,
                application_name=APPLICATION_NAME1,
                provider_client_id=EXTERNAL_APPLICATION_ID1,
                domain='social.yandex.net',
                refresh_token_url='https://refresh/'
            ),
            dict(
                application_id=APPLICATION_ID2,
                application_name=APPLICATION_NAME2,
                provider_client_id=EXTERNAL_APPLICATION_ID1,
                domain='social.yandex.net',
            ),
        ]
        return settings

    def test_expired_refreshable_token(self):
        with self._fake_db.no_recording() as db:
            token1 = self._build_token(application_id=APPLICATION_ID1, expired=now() - timedelta(seconds=1))
            save_token(token1, db)
            refresh_token = RefreshToken(token_id=token1.token_id, value=APPLICATION_TOKEN2)
            save_refresh_token(refresh_token, db)

        clean_db(1)

        db = self._fake_db.get_engine()
        token2 = find_token_by_token_id(token1.token_id, db)
        self.assertTrue(token2)
        # Пока нельзя ходить в Zora из скриптов, не подновляем токен, но и не
        # удаляем его.
        self.assertEqual(DatetimeNow(timestamp=token1.expired), token2.expired)
        self.assertTrue(find_refresh_token_by_token_id(token1.token_id, db))

    def test_expired_not_refreshable_token(self):
        with self._fake_db.no_recording() as db:
            token = self._build_token(application_id=APPLICATION_ID2, expired=now() - timedelta(seconds=1))
            save_token(token, db)
            refresh_token = RefreshToken(token_id=token.token_id, value=APPLICATION_TOKEN2)
            save_refresh_token(refresh_token, db)

        clean_db(1)

        db = self._fake_db.get_engine()
        self.assertFalse(find_token_by_token_id(token.token_id, db))
        self.assertFalse(find_refresh_token_by_token_id(token.token_id, db))


class TestCleanDbTokenLinkedWithMissingApplication(CleanDbTestCase):
    def setUp(self):
        super(TestCleanDbTokenLinkedWithMissingApplication, self).setUp()

        token = Token(application_id=APPLICATION_ID1, value=APPLICATION_TOKEN1)
        with self._fake_db.no_recording() as db:
            self._create_profile(
                db=db,
                profile_info=dict(provider=dict(code='vk'), userid=SIMPLE_USERID1),
                token=token,
            )
            self.token_id = token.token_id

    def build_settings(self):
        settings = super(TestCleanDbTokenLinkedWithMissingApplication, self).build_settings()
        settings.update(applications=list())
        return settings

    def test(self):
        clean_db(1)

        self.assertFalse(find_token_by_token_id(self.token_id, self._fake_db.get_engine()))


class TestCleanDbTokenLinkedWithMissingProvider(CleanDbTestCase):
    def setUp(self):
        super(TestCleanDbTokenLinkedWithMissingProvider, self).setUp()

        token = Token(application_id=APPLICATION_ID1, value=APPLICATION_TOKEN1)
        with self._fake_db.no_recording() as db:
            self._create_profile(
                db=db,
                profile_info=dict(provider=dict(code=PROVIDER_CODE1), userid=SIMPLE_USERID1),
                token=token,
            )
            self.token_id = token.token_id

    def build_settings(self):
        settings = super(TestCleanDbTokenLinkedWithMissingProvider, self).build_settings()
        settings.update(
            applications=[
                dict(
                    application_id=APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    domain='social.yandex.net',
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    provider_id=PROVIDER_ID1,
                ),
            ],
            providers=[
                dict(
                    code=PROVIDER_CODE1,
                    display_name=dict(default=PROVIDER_CODE1),
                    id=PROVIDER_ID1,
                    name=PROVIDER_CODE1,
                ),
            ],
        )
        return settings

    def test(self):
        settings = self.build_settings()
        settings = dict(settings)
        settings.update(providers=list())

        with self.settings_context(settings):
            clean_db(1)

        self.assertFalse(find_token_by_token_id(self.token_id, self._fake_db.get_engine()))
