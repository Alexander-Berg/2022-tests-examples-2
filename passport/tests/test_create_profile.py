# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import eq_
from passport.backend.core.db.utils import insert_with_on_duplicate_key_update
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common.application import application_eav_configuration
from passport.backend.social.common.db.schemas import (
    person_table,
    refresh_token_table,
)
from passport.backend.social.common.eav import EavSelector
from passport.backend.social.common.profile import (
    BaseProfileCreationError,
    create_profile,
    ProfileCreator,
)
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    SIMPLE_USERID1,
    UID1,
    UNIXTIME1,
    UNIXTIME2,
    VKONTAKTE_APPLICATION_ID1,
    YANDEXUID1,
)
from passport.backend.social.common.test.sql import (
    InsertOrUpdatePersonDataQuery,
    InsertOrUpdateProfileDataQuery,
    InsertOrUpdateTokenDataQuery,
    SelectProfileByUseridDataQuery,
    SelectTokenByValueForAccountDataQuery,
    UpdatePersonDataQuery,
    UpdateProfileDataQuery,
    UpdateTokenDataQuery,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import (
    find_token_by_token_id,
    save_token,
)


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self._engine = self._fake_db.get_engine()
        LazyLoader.register('slave_db_engine', lambda: self._engine)
        providers.init()

    def _create_profile(self, provider_code=Vkontakte.code, application_id=VKONTAKTE_APPLICATION_ID1,
                        application_token=APPLICATION_TOKEN1, timestamp=UNIXTIME1,
                        scope=None, secret=None, expires=None, refresh_token=None, allow_auth=None):
        profile_info = {
            'provider': {'code': provider_code},
            'userid': SIMPLE_USERID1,
        }

        token = Token(
            application_id=application_id,
            value=application_token,
            scopes=scope,
            secret=secret,
            expired=expires,
        )

        create_profile(
            mysql_read=self._engine,
            mysql_write=self._engine,
            uid=UID1,
            profile_info=profile_info,
            token=token,
            timestamp=timestamp,
            yandexuid=YANDEXUID1,
            refresh_token=refresh_token,
            allow_auth=allow_auth,
        )


class TestCreateProfileNoProfile(BaseTestCase):
    def test_minimal_token(self):
        self._create_profile(
            application_id=VKONTAKTE_APPLICATION_ID1,
            application_token=APPLICATION_TOKEN1,
            timestamp=UNIXTIME1,
        )

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(
                application_id=VKONTAKTE_APPLICATION_ID1,
                application_token=APPLICATION_TOKEN1,
                created=datetime.fromtimestamp(UNIXTIME1),
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
            ) +
            self._person_sql_queries()
        )

    def test_token_scopes(self):
        self._create_profile(scope='hello,yello')

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(scope='hello,yello') +
            self._person_sql_queries()
        )

    def test_token_secret(self):
        self._create_profile(secret='5ecre7')

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(secret='5ecre7') +
            self._person_sql_queries()
        )

    def test_timestamp_0(self):
        self._create_profile(timestamp=0)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries(
                created=datetime.fromtimestamp(0),
                verified=datetime.fromtimestamp(0),
                confirmed=datetime.fromtimestamp(0),
            ) +
            self._token_sql_queries(
                created=datetime.fromtimestamp(0),
                verified=datetime.fromtimestamp(0),
                confirmed=datetime.fromtimestamp(0),
            ) +
            self._person_sql_queries()
        )

    def test_token_expires_0(self):
        self._create_profile(expires=0)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(expired=datetime.fromtimestamp(0)) +
            self._person_sql_queries()
        )

    def test_token_expiration_time(self):
        self._create_profile(expires=UNIXTIME1)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(expired=datetime.fromtimestamp(UNIXTIME1)) +
            self._person_sql_queries()
        )

    def test_token_scope__whitespace_splitted(self):
        self._create_profile(scope='foo bar')

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(scope='bar,foo') +
            self._person_sql_queries()
        )

    def test_token_scope__odnoklassniki_valuable_access(self):
        self._create_profile(scope='valuable access,KUNG_FOO')

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(scope='KUNG_FOO,VALUABLE_ACCESS') +
            self._person_sql_queries()
        )

    def test_refresh_token(self):
        refresh_token = RefreshToken(value=APPLICATION_TOKEN2, expired=datetime.fromtimestamp(UNIXTIME1), scopes=None)
        self._create_profile(refresh_token=refresh_token)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries() +
            [
                insert_with_on_duplicate_key_update(
                    refresh_token_table,
                    ['expired', 'value'],
                )
                .values(
                    token_id=1,
                    value=APPLICATION_TOKEN2,
                    expired=datetime.fromtimestamp(UNIXTIME1),
                ),
            ] +
            self._person_sql_queries()
        )

        eq_(refresh_token.refresh_token_id, 1)
        eq_(refresh_token.token_id, 1)

    def test_refresh_token__eternal(self):
        self._create_profile(refresh_token=RefreshToken(value=APPLICATION_TOKEN2, expired=None, scopes=None))

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries() +
            [
                insert_with_on_duplicate_key_update(
                    refresh_token_table,
                    ['expired', 'value'],
                )
                .values(
                    token_id=1,
                    value=APPLICATION_TOKEN2,
                    expired='0000-00-00 00:00:00',
                ),
            ] +
            self._person_sql_queries()
        )

    def _profile_sql_queries(self, created=datetime.fromtimestamp(UNIXTIME1), verified=datetime.fromtimestamp(UNIXTIME1),
                             confirmed=datetime.fromtimestamp(UNIXTIME1)):
        return [
            SelectProfileByUseridDataQuery(Vkontakte.id, SIMPLE_USERID1, UID1).to_sql(),
            InsertOrUpdateProfileDataQuery(
                uid=UID1,
                provider_id=Vkontakte.id,
                userid=SIMPLE_USERID1,
                username='',
                created=created,
                verified=verified,
                confirmed=confirmed,
                referer=0,
                yandexuid=YANDEXUID1,
            ).to_sql(),
        ]

    def _token_sql_queries(self, application_id=VKONTAKTE_APPLICATION_ID1, application_token=APPLICATION_TOKEN1,
                           created=datetime.fromtimestamp(UNIXTIME1), verified=datetime.fromtimestamp(UNIXTIME1),
                           confirmed=datetime.fromtimestamp(UNIXTIME1), scope='',
                           secret=None, expired=None):
        insert_args = dict(
            uid=UID1,
            profile_id=1,
            application_id=application_id,
            value=application_token,
            scope=scope,
            created=created,
            verified=verified,
            confirmed=confirmed,
        )
        if secret is not None:
            insert_args['secret'] = secret
        if expired is not None:
            insert_args['expired'] = expired
        return [
            SelectTokenByValueForAccountDataQuery(UID1, application_id, application_token).to_sql(),
            InsertOrUpdateTokenDataQuery(**insert_args).to_sql(),
        ]

    def _person_sql_queries(self):
        return [
            person_table.select().where(person_table.c.profile_id == 1),
            InsertOrUpdatePersonDataQuery(profile_id=1).to_sql(),
        ]


class TestCreateProfileProfileExists(BaseTestCase):
    def setUp(self):
        super(TestCreateProfileProfileExists, self).setUp()
        with self._fake_db.no_recording():
            self._create_profile(scope='hello,yello')

    def test_minimal_token(self):
        self._create_profile(
            application_id=VKONTAKTE_APPLICATION_ID1,
            application_token=APPLICATION_TOKEN1,
            timestamp=UNIXTIME1,
        )

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(
                application_id=VKONTAKTE_APPLICATION_ID1,
                application_token=APPLICATION_TOKEN1,
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
            ) +
            self._person_sql_queries()
        )

    def test_token_scopes(self):
        self._create_profile(scope='hello,bye')

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries(scope='bye,hello,yello') +
            self._person_sql_queries()
        )

    def test_refresh_token__does_not_exist(self):
        self._create_profile(refresh_token=RefreshToken(value=APPLICATION_TOKEN2, expired=datetime.fromtimestamp(UNIXTIME1), scopes=None))

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries() +
            [
                insert_with_on_duplicate_key_update(
                    refresh_token_table,
                    ['expired', 'value'],
                )
                .values(
                    token_id=1,
                    value=APPLICATION_TOKEN2,
                    expired=datetime.fromtimestamp(UNIXTIME1),
                ),
            ] +
            self._person_sql_queries()
        )

    def test_disable_allow_auth(self):
        self._create_profile(allow_auth=False)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries(allow_auth=False) +
            self._token_sql_queries() +
            self._person_sql_queries()
        )

    def test_enable_allow_auth(self):
        self._create_profile(allow_auth=True)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries(allow_auth=True) +
            self._token_sql_queries() +
            self._person_sql_queries()
        )

    def _profile_sql_queries(self, verified=datetime.fromtimestamp(UNIXTIME1),
                             confirmed=datetime.fromtimestamp(UNIXTIME1), allow_auth=False):
        return [
            SelectProfileByUseridDataQuery(Vkontakte.id, SIMPLE_USERID1, UID1).to_sql(),
            UpdateProfileDataQuery(
                profile_id=1,
                uid=UID1,
                provider_id=Vkontakte.id,
                userid=SIMPLE_USERID1,
                username='',
                verified=verified,
                confirmed=confirmed,
                referer=0,
                yandexuid=YANDEXUID1,
                allow_auth=allow_auth,
            ).to_sql(),
        ]

    def _token_sql_queries(self, application_id=VKONTAKTE_APPLICATION_ID1, application_token=APPLICATION_TOKEN1,
                           verified=datetime.fromtimestamp(UNIXTIME1), confirmed=datetime.fromtimestamp(UNIXTIME1),
                           scope='hello,yello'):
        update_args = dict(
            token_id=1,
            value=application_token,
            scope=scope,
            profile_id=1,
            verified=verified,
            confirmed=confirmed,
            created=datetime.fromtimestamp(UNIXTIME1),
        )
        return [
            SelectTokenByValueForAccountDataQuery(UID1, application_id, application_token).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([application_id]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([application_id]),
            UpdateTokenDataQuery(**update_args).to_sql(),
        ]

    def _person_sql_queries(self):
        return [
            person_table.select().where(person_table.c.profile_id == 1),
            UpdatePersonDataQuery(profile_id=1).to_sql(),
        ]


class TestCreateProfileProfileWithRefreshTokenExists(BaseTestCase):
    def setUp(self):
        super(TestCreateProfileProfileWithRefreshTokenExists, self).setUp()
        with self._fake_db.no_recording():
            self._create_profile(
                scope='',
                refresh_token=RefreshToken(value=APPLICATION_TOKEN2, expired=datetime.fromtimestamp(UNIXTIME1), scopes=None),
            )

    def test_refresh_token__same(self):
        self._create_profile(refresh_token=RefreshToken(value=APPLICATION_TOKEN2, expired=datetime.fromtimestamp(UNIXTIME1), scopes=None))

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries() +
            [
                insert_with_on_duplicate_key_update(
                    refresh_token_table,
                    ['expired', 'value'],
                )
                .values(
                    token_id=1,
                    value=APPLICATION_TOKEN2,
                    expired=datetime.fromtimestamp(UNIXTIME1),
                ),
            ] +
            self._person_sql_queries()
        )

    def test_refresh_token__different(self):
        self._create_profile(refresh_token=RefreshToken(value=APPLICATION_TOKEN1, expired=datetime.fromtimestamp(UNIXTIME2), scopes=None))

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries() +
            self._token_sql_queries() +
            [
                insert_with_on_duplicate_key_update(
                    refresh_token_table,
                    ['expired', 'value'],
                )
                .values(
                    token_id=1,
                    value=APPLICATION_TOKEN1,
                    expired=datetime.fromtimestamp(UNIXTIME2),
                ),
            ] +
            self._person_sql_queries()
        )

    def _profile_sql_queries(
        self,
        verified=datetime.fromtimestamp(UNIXTIME1),
        confirmed=datetime.fromtimestamp(UNIXTIME1),
    ):
        return [
            SelectProfileByUseridDataQuery(Vkontakte.id, SIMPLE_USERID1, UID1).to_sql(),
            UpdateProfileDataQuery(
                profile_id=1,
                uid=UID1,
                provider_id=Vkontakte.id,
                userid=SIMPLE_USERID1,
                username='',
                verified=verified,
                confirmed=confirmed,
                referer=0,
                yandexuid=YANDEXUID1,
            ).to_sql(),
        ]

    def _token_sql_queries(self, application_id=VKONTAKTE_APPLICATION_ID1, application_token=APPLICATION_TOKEN1,
                           verified=datetime.fromtimestamp(UNIXTIME1), confirmed=datetime.fromtimestamp(UNIXTIME1),
                           scope=''):
        update_args = dict(
            token_id=1,
            value=application_token,
            scope=scope,
            profile_id=1,
            verified=verified,
            confirmed=confirmed,
            created=datetime.fromtimestamp(UNIXTIME1),
        )
        return [
            SelectTokenByValueForAccountDataQuery(UID1, application_id, application_token).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([application_id]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([application_id]),
            UpdateTokenDataQuery(**update_args).to_sql(),
        ]

    def _person_sql_queries(self):
        return [
            person_table.select().where(person_table.c.profile_id == 1),
            UpdatePersonDataQuery(profile_id=1).to_sql(),
        ]


class TestCreateProfileProfileAllowsAuthz(BaseTestCase):
    def setUp(self):
        super(TestCreateProfileProfileAllowsAuthz, self).setUp()
        with self._fake_db.no_recording():
            self._create_profile(allow_auth=True)

    def test_enable_allow_auth(self):
        self._create_profile(allow_auth=True)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries(allow_auth=True) +
            self._token_sql_queries() +
            self._person_sql_queries()
        )

    def test_disable_allow_auth(self):
        self._create_profile(allow_auth=False)

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries(allow_auth=False) +
            self._token_sql_queries() +
            self._person_sql_queries()
        )

    def test_omit_allow_auth(self):
        self._create_profile()

        self._fake_db.assert_executed_queries_equal(
            self._profile_sql_queries(allow_auth=True) +
            self._token_sql_queries() +
            self._person_sql_queries()
        )

    def _profile_sql_queries(self, allow_auth=False):
        return [
            SelectProfileByUseridDataQuery(Vkontakte.id, SIMPLE_USERID1, UID1).to_sql(),
            UpdateProfileDataQuery(
                profile_id=1,
                uid=UID1,
                provider_id=Vkontakte.id,
                userid=SIMPLE_USERID1,
                username='',
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
                referer=0,
                yandexuid=YANDEXUID1,
                allow_auth=allow_auth,
            ).to_sql(),
        ]

    def _token_sql_queries(self):
        update_args = dict(
            token_id=1,
            value=APPLICATION_TOKEN1,
            scope='',
            profile_id=1,
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
            created=datetime.fromtimestamp(UNIXTIME1),
        )
        return [
            SelectTokenByValueForAccountDataQuery(UID1, VKONTAKTE_APPLICATION_ID1, APPLICATION_TOKEN1).to_sql(),
            EavSelector(application_eav_configuration, ['application_id']).index_query([VKONTAKTE_APPLICATION_ID1]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([VKONTAKTE_APPLICATION_ID1]),
            UpdateTokenDataQuery(**update_args).to_sql(),
        ]

    def _person_sql_queries(self):
        return [
            person_table.select().where(person_table.c.profile_id == 1),
            UpdatePersonDataQuery(profile_id=1).to_sql(),
        ]


class TestCreateProfileGarbageToken(BaseTestCase):
    def setUp(self):
        super(TestCreateProfileGarbageToken, self).setUp()
        with self._fake_db.no_recording() as db:
            token = Token(
                uid=UID1,
                profile_id=2,
                application_id=VKONTAKTE_APPLICATION_ID1,
                value=APPLICATION_TOKEN1,
                secret=None,
                scopes=None,
                expired=None,
                created=datetime.fromtimestamp(UNIXTIME1),
                verified=datetime.fromtimestamp(UNIXTIME1),
                confirmed=datetime.fromtimestamp(UNIXTIME1),
            )
            save_token(token, db)
            assert token.token_id == 1

    def test_ok(self):
        self._create_profile()

        token = find_token_by_token_id(1, self._fake_db.get_engine())
        self.assertIsNotNone(token)
        self.assertEqual(token.profile_id, 1)

        token = find_token_by_token_id(2, self._fake_db.get_engine())
        self.assertIsNone(token)


class TestProfileCreatorNoUserid(BaseTestCase):
    def _build_profile_creator(self, userinfo):
        return ProfileCreator(
            mysql_read=self._engine,
            mysql_write=self._engine,
            uid=UID1,
            social_userinfo=userinfo,
            timestamp=UNIXTIME1,
            token=None,
        )

    def _build_userinfo_with_none_userid(self):
        return {
            'provider': {'code': Vkontakte.code},
            'userid': None,
        }

    def _build_userinfo_without_userid(self):
        return {
            'provider': {'code': Vkontakte.code},
            'userid': None,
        }

    def test_create__userid_none(self):
        with self.assertRaises(BaseProfileCreationError):
            creator = self._build_profile_creator(self._build_userinfo_with_none_userid())
            creator.create()

    def test_check_profile_possible__userid_none(self):
        with self.assertRaises(BaseProfileCreationError):
            creator = self._build_profile_creator(self._build_userinfo_with_none_userid())
            creator.check_profile_possible()

    def test_create__no_userid(self):
        with self.assertRaises(BaseProfileCreationError):
            creator = self._build_profile_creator(self._build_userinfo_without_userid())
            creator.create()

    def test_check_profile_possible__no_userid(self):
        with self.assertRaises(BaseProfileCreationError):
            creator = self._build_profile_creator(self._build_userinfo_without_userid())
            creator.check_profile_possible()
