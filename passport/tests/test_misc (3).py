# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.execute import execute
from passport.backend.social.common.db.schemas import business_application_map_table as bamt
from passport.backend.social.common.exception import DatabaseError
from passport.backend.social.common.grants import GrantsContext
from passport.backend.social.common.misc import get_business_userid
from passport.backend.social.common.profile import create_profile
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_NAME1,
    BUSINESS_ID1,
    BUSINESS_ID2,
    BUSINESS_TOKEN1,
    BUSINESS_TOKEN2,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    SIMPLE_USERID1,
    SIMPLE_USERID2,
    UID1,
    UNIXTIME1,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import save_token
from passport.backend.social.proxy2.misc import (
    get_profile,
    get_profiles_by_provider_userids,
    get_tokens,
    simple_userids_2_business_userids,
)
from passport.backend.social.proxy2.test import TestCase
from sqlalchemy.exc import IntegrityError


class TestMisc(TestCase):
    def setUp(self):
        super(TestMisc, self).setUp()

        self.exec_method = Mock()
        self._fake_db.set_side_effect(self.exec_method)
        self._db = self._fake_db.get_engine()

    def test_execute_basic(self):
        self.exec_method.return_value = 'data'
        result = execute(self._db, 'query')
        eq_(result, 'data')

    def test_execute_retry(self):
        self.exec_method.side_effect = [
            IntegrityError(Mock(), Mock(), Mock()),
            'data1',
        ]
        result = execute(self._db, 'query', retries=2)
        eq_(result, 'data1')

    @raises(DatabaseError)
    def test_execute_retry_raises(self):
        self.exec_method.side_effect = [
            IntegrityError(Mock(), Mock(), Mock()),
            'data1',
        ]
        execute(self._db, 'query', retries=1)

    def test_get_profile_ok(self):
        self.exec_method.return_value = Mock(fetchone=Mock(return_value='data2'))
        with patch('passport.backend.social.proxy2.misc.select', Mock(return_value=Mock())):
            result = get_profile(100)
            eq_(result, 'data2')


class TestGetProfilesByProviderUserids(TestCase):
    def build_settings(self):
        settings = super(TestGetProfilesByProviderUserids, self).build_settings()
        settings['social_config'].update(
            dict(
                max_sql_in_function_values=1,
            ),
        )
        return settings

    def _create_profile(self, uid, userid):
        profile_info = dict(
            provider=providers.get_provider_info_by_name('vk'),
            userid=userid,
        )
        create_profile(
            self._fake_db.get_engine(),
            self._fake_db.get_engine(),
            uid=uid,
            profile_info=profile_info,
            token=None,
            timestamp=UNIXTIME1,
            yandexuid=None,
        )

    def test_one_profile(self):
        self._create_profile(uid=100, userid='userid1')
        self._create_profile(uid=100, userid='userid3')

        result = get_profiles_by_provider_userids(1, ['userid1', 'userid2'])

        eq_(
            result,
            {
                'userid1': [
                    dict(
                        uid=100,
                        profile_id=1,
                        userid='userid1',
                        username='',
                    ),
                ],
            },
        )

    def test_many_profiles(self):
        self._create_profile(uid=100, userid='userid1')
        self._create_profile(uid=100, userid='userid2')
        self._create_profile(uid=101, userid='userid1')

        result = get_profiles_by_provider_userids(1, ['userid1', 'userid2'])

        eq_(
            result,
            {
                'userid1': [
                    dict(
                        uid=100,
                        profile_id=1,
                        userid='userid1',
                        username='',
                    ),
                    dict(
                        uid=101,
                        profile_id=3,
                        userid='userid1',
                        username='',
                    ),
                ],
                'userid2': [
                    dict(
                        uid=100,
                        profile_id=2,
                        userid='userid2',
                        username='',
                    ),
                ],
            },
        )

    def test_no_userids(self):
        self._create_profile(uid=100, userid='userid1')

        result = get_profiles_by_provider_userids(1, [])

        eq_(result, dict())


class TestGetTokens(TestCase):
    def setUp(self):
        super(TestGetTokens, self).setUp()
        self._fake_grants_config.add_consumer(
            consumer=CONSUMER1,
            grants=['no-cred-use-token'],
            networks=[CONSUMER_IP1],
        )
        self.request_ctx.grants_context = GrantsContext(CONSUMER_IP1, CONSUMER1)

    def build_settings(self):
        settings = super(TestGetTokens, self).build_settings()
        settings.update(dict(
            applications=[dict(
                application_id=APPLICATION_ID1,
                application_name=APPLICATION_NAME1,
                provider_client_id=EXTERNAL_APPLICATION_ID1,
            )],
        ))
        return settings

    def test_basic(self):
        future = datetime.fromtimestamp(now.i()) + timedelta(hours=1)
        token = Token(
            uid=UID1,
            profile_id=100,
            application_id=APPLICATION_ID1,
            value='value',
            secret='secret',
            scopes=['scope'],
            expired=future,
            created=future,
            verified=future,
            confirmed=future,
        )
        save_token(token, self._fake_db.get_engine())

        tokens = get_tokens(profile_id=100)

        assert len(tokens) == 1
        self.assertEqual(tokens[0], token)


class TestSimpleUserIds2BusinessUserids(TestCase):
    def test_has_business_userid(self):
        self._given_business_token()

        business_userids, unknown_userids = simple_userids_2_business_userids([SIMPLE_USERID1])

        eq_(business_userids[SIMPLE_USERID1], get_business_userid(BUSINESS_ID1, BUSINESS_TOKEN1))
        eq_(unknown_userids, [])

    def test_has_no_business_userid(self):
        self._given_business_token()

        business_userids, unknown_userids = simple_userids_2_business_userids([SIMPLE_USERID2])

        from sqlalchemy.sql import and_
        from passport.backend.social.common.db.schemas import business_application_map_table
        from passport.backend.social.common.test.db import eq_sql_queries
        eq_sql_queries(
            self._fake_db.executed_queries,
            [
                (
                    business_application_map_table.insert()
                    .values(
                        business_id=BUSINESS_ID1,
                        business_token=BUSINESS_TOKEN1,
                        application_id=APPLICATION_ID1,
                        userid=SIMPLE_USERID1,
                    )
                ),
                (
                    business_application_map_table.select()
                    .where(
                        and_(
                            business_application_map_table.c.userid.in_([SIMPLE_USERID2]),
                            business_application_map_table.c.business_id == BUSINESS_ID1,
                        ),
                    )
                ),
            ],
        )

        eq_(business_userids, {})
        eq_(unknown_userids, [SIMPLE_USERID2])

    def test_userid_in_many_apps_of_business(self):
        self._given_business_token()
        execute(
            self._fake_db.get_engine(),
            bamt.insert().values({
                'business_id': BUSINESS_ID1,
                'business_token': BUSINESS_TOKEN1,
                'application_id': APPLICATION_ID2,
                'userid': SIMPLE_USERID1,
            }),
        )

        business_userids, unknown_userids = simple_userids_2_business_userids([SIMPLE_USERID1])

        eq_(business_userids[SIMPLE_USERID1], get_business_userid(BUSINESS_ID1, BUSINESS_TOKEN1))
        eq_(unknown_userids, [])

    def test_userid_in_many_businesses(self):
        # Для простоты пользуемся только 1-м buiseness_id.
        self._given_business_token()
        execute(
            self._fake_db.get_engine(),
            bamt.insert().values({
                'business_id': BUSINESS_ID2,
                'business_token': BUSINESS_TOKEN2,
                'application_id': APPLICATION_ID2,
                'userid': SIMPLE_USERID1,
            }),
        )

        business_userids, unknown_userids = simple_userids_2_business_userids([SIMPLE_USERID1])

        eq_(business_userids[SIMPLE_USERID1], get_business_userid(BUSINESS_ID1, BUSINESS_TOKEN1))
        eq_(unknown_userids, [])

    def _given_business_token(self):
        execute(
            self._fake_db.get_engine(),
            bamt.insert().values({
                'business_id': BUSINESS_ID1,
                'business_token': BUSINESS_TOKEN1,
                'application_id': APPLICATION_ID1,
                'userid': SIMPLE_USERID1,
            }),
        )
