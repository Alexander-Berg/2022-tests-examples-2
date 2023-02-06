# -*- coding: utf-8 -*-

from copy import copy
import datetime
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core import Undefined
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.api.app import create_app
from passport.backend.social.common.db.schemas import (
    business_application_map_table as bamt,
    person_table as pert,
    profile_table as pt,
    sub_table as st,
    token_table as tt,
)
from passport.backend.social.common.grants import GrantsConfig
from passport.backend.social.common.limits import QLimits
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.test.fake_gpt import FakeGpt
from passport.backend.social.common.test.fake_other import FakeBuildRequestId
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
)
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import (
    TestCase,
    TvmTestCaseMixin,
)
from passport.backend.social.common.test_client import FlaskTestClient
from passport.backend.social.common.token.db import TokenRecord
import passport.backend.social.proxylib
from passport.backend.social.proxylib.test import facebook as facebook_test
from sqlalchemy.sql.expression import (
    insert,
    select,
)

from .base_test_data import (
    TEST_APP_ID,
    TEST_BUSINESS_ID,
    TEST_BUSINESS_TOKEN,
    TEST_BUSINESS_USERID,
    TEST_SIMLE_USERID,
    TEST_TASK_FINISHED_DT,
    TEST_UID,
)


def is_json(response):
    eq_(response.headers['Content-Type'], 'application/json')


def get_json_response_without_errors(response):
    is_json(response)
    json_response = json.loads(response.data)
    ok_('error' not in json_response, json_response)
    return json_response


def is_not_found(response):
    eq_(response.status_code, 404, response.data)


def is_not_found_json(response, **kwargs):
    is_not_found(response)
    json_response = json.loads(response.data)
    ok_('error' in json_response)
    error_response = json_response['error']
    for key, val in kwargs.items():
        ok_(key in error_response)
        eq_(error_response[key], val)


def error_in_json(response, code=400, **kwargs):
    eq_(response.status_code, code, response.data)
    json_response = json.loads(response.data)
    ok_('error' in json_response)
    error_response = json_response['error']
    for key, val in kwargs.items():
        ok_(key in error_response)
        eq_(error_response[key], val)

    return json_response


now = int(time.time())


def build_profiles():
    # NOTE - при добавлении профилей сюда не забывать добавлять запись в person.
    return [
        {'profile_id': 1, 'uid': 1, 'provider_id': 1, 'userid': 1, 'username': 'inkvi', 'yandexuid': 123,
            'created': now - 5, 'verified': now - 5},
        {
            'profile_id': 2,
            'uid': 2,
            'provider_id': 2,
            'userid': 2,
            'username': 'spleenjack',
            'yandexuid': 234,
            'created': now,
        },
        {'profile_id': 3, 'uid': 1, 'provider_id': 3, 'userid': 3, 'username': 'zzhanka', 'yandexuid': 345,
            'created': now},
        {'profile_id': 4, 'uid': 3, 'provider_id': 1, 'userid': 4, 'username': 'inkvionair', 'yandexuid': 456,
            'created': now - 5, 'verified': now - 5},
        {'profile_id': 5, 'uid': 4, 'provider_id': 2, 'userid': 5, 'username': 'twee', 'yandexuid': 567,
            'created': now - 5, 'verified': now - 5},
        {'profile_id': 6, 'uid': 4, 'provider_id': 2, 'userid': 'bt:1:abc', 'username': 'business_user', 'yandexuid': 567,
            'created': now - 5, 'verified': now - 5},
        {'profile_id': 7, 'uid': 5, 'provider_id': 2, 'userid': 'bt:1:gtj', 'username': 'business_user2', 'yandexuid': 567,
            'created': now - 5, 'verified': now - 5},
    ]

profiles = build_profiles()

tokens = [
    {
        'token_id': 1,
        'uid': 1,
        'profile_id': 1,
        'application_id': 10,
        'secret': 's',
        'value': 'values',
        'scope': 'offline',
    },
    {
        'token_id': 2,
        'uid': 2,
        'profile_id': 2,
        'application_id': 20,
        'secret': 's',
        'value': 'values',
        'scope': 'video',
    },
    {
        'token_id': 3,
        'uid': 1,
        'profile_id': 3,
        'application_id': 30,
        'secret': 's',
        'value': 'values',
        'scope': 'pictures',
    },
    {
        'token_id': 4,
        'uid': 3,
        'profile_id': 4,
        'application_id': 10,
        'secret': 's',
        'value': 'values',
        'scope': 'offline, email',
    },
]
for token in tokens:
    token['value_hash'] = TokenRecord.eval_value_hash(token['value'])

persons = [
    {'profile_id': 1, 'firstname': 'Alex', 'lastname': 'E'},
    {'profile_id': 2, 'firstname': 'Evg', 'lastname': 'A'},
    {'profile_id': 3, 'firstname': 'Zz', 'lastname': 'K'},
    {'profile_id': 4, 'firstname': u'Александр', 'lastname': 'E'},
    {'profile_id': 5, 'firstname': 'Twi', 'lastname': 'T'},
    {'profile_id': 6, 'firstname': 'First_6', 'lastname': 'Last_6'},
    {'profile_id': 7, 'firstname': 'First_7', 'lastname': 'Last_7'},
]

subscriptions = [
    {'profile_id': 1, 'sid': 1, 'value': 1},
    {'profile_id': 1, 'sid': 2, 'value': 1},
    {'profile_id': 2, 'sid': 4, 'value': 1},
    {'profile_id': 3, 'sid': 3, 'value': 1},
]


business_application_data = [
    {'business_id': 1, 'business_token': 'abc', 'application_id': 20, 'userid': 111},
    {'business_id': 2, 'business_token': 'abc', 'application_id': 2222, 'userid': 111888},
    {'business_id': 1, 'business_token': 'abc', 'application_id': 2222, 'userid': 111999},
    {'business_id': 1, 'business_token': 'abc', 'application_id': 21, 'userid': 222},
    {'business_id': 1, 'business_token': 'abc', 'application_id': 22, 'userid': 111},
    {'business_id': 1, 'business_token': 'gtj', 'application_id': 20, 'userid': 555},
]

services_config = {
    '1': {
        'name': '1_disabled',
        'sid': 1,
        'default_value': 0,
    },
    '2': {
        'name': '2_enabled',
        'sid': 2,
        'default_value': 1,
    },
    '101': {
        'name': '101_disabled',
        'sid': 101,
        'default_value': 0,
    },
    '102': {
        'name': '102_enabled',
        'sid': 102,
        'default_value': 1,
    },
}
default_sids = [2, 102]


def get_default_sids():
    return default_sids[:]


def insert_records(engine, table, records, convert_timestamps=True):
    """
    convert_timestamps: в новой алхимии нельзя пихать лишние стобцы в запрос, они теперь не игнорируются
    """
    for record in records:
        r = copy(record)
        if convert_timestamps:
            r['created'] = datetime.date.fromtimestamp(r.get('created', 0))
            r['verified'] = datetime.date.fromtimestamp(r.get('verified', 0))
        engine.execute(table.insert(r))


def load_fixture(engine):
    insert_records(engine, pt, build_profiles())
    insert_records(engine, tt, tokens)
    insert_records(engine, pert, persons, convert_timestamps=False)
    insert_records(engine, st, subscriptions, convert_timestamps=False)
    insert_records(engine, bamt, business_application_data, convert_timestamps=False)


class TestApiAppCase(
    TvmTestCaseMixin,
    TestCase,
):
    def setUp(self):
        super(TestApiAppCase, self).setUp()

        self._fake_request_id = FakeBuildRequestId().start()
        self.grants_config = FakeGrantsConfig()

        self.__patches = [
            self._fake_request_id,
            self.grants_config,
        ]
        for patch in self.__patches:
            patch.start()

        self.app = create_app()
        self.app.testing = True

        self.app.test_client_class = FlaskTestClient
        self.app_client = self.app.test_client()
        self.app_client.set_context({'consumer': 'dev'})

        self.ctx = self.app.test_request_context()
        self.ctx.push()

        grants_config = GrantsConfig('social-api', mock.Mock(name='tvm_credentials_manager'))
        LazyLoader.register('grants_config', lambda: grants_config)

    def tearDown(self):
        try:
            self.ctx.pop()
        except AssertionError:
            pass
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestApiAppCase, self).tearDown()


class TestApiViewsCase(TestApiAppCase):
    need_fixture = False

    def setUp(self):
        super(TestApiViewsCase, self).setUp()

        self.engine = self._fake_db.get_engine()

        self._fake_redis = self.redis = FakeRedisClient()
        self._redis_patch = RedisPatch(self._fake_redis)

        self.fake_facebook = facebook_test.FakeProxy()

        self._fake_gpt = FakeGpt()

        self.__patches = [
            mock.patch('passport.backend.social.common.services_settings.Services._Services__services', services_config),
            mock.patch('passport.backend.social.common.services_settings.Services.get_default_sids', mock.Mock(side_effect=get_default_sids)),
            self.fake_facebook,
            self._redis_patch,
            self._fake_gpt,
        ]

        for patch in self.__patches:
            patch.start()

        LazyLoader.register('slave_db_engine', self._fake_db.get_engine)
        LazyLoader.register('master_db_engine', self._fake_db.get_engine)
        LazyLoader.register('redis', lambda: self._fake_redis)

        LazyLoader.register('http_pool_manager', lambda: mock.Mock(name='http_pool_manager'))
        LazyLoader.register('qlimits', QLimits)

        providers.init()

        if self.need_fixture:
            load_fixture(self.engine)

        passport.backend.social.proxylib.init()

    def tearDown(self):
        LazyLoader.flush()
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestApiViewsCase, self).tearDown()

    def correspondence_between_profiles(self, profile_response, profile_inserted, test_func=None):
        """
        Соответствие между двумя профилями
        :param profile_response: профиль полученный в качестве ответа
        :param profile_inserted: профиль вставленный в базу в начале теста
        """
        eq_(profile_response['profile_id'], profile_inserted['profile_id'])
        eq_(profile_response.get('username', None), profile_inserted.get('username', None))
        ok_('provider' in profile_response)
        ok_(profile_response['provider'] != profile_inserted['provider_id'])

        if test_func:
            test_func(profile_response, profile_inserted)

        if 'person' in profile_response:
            person_inserted = filter(lambda s: s['profile_id'] == profile_response['profile_id'], persons)[0]
            eq_(person_inserted.get('birthday', None), profile_response['person']['birthday'])
            eq_(person_inserted.get('firstname', ''), profile_response['person']['firstname'])
            eq_(person_inserted.get('lastname', ''), profile_response['person']['lastname'])
            eq_(person_inserted.get('nickname', ''), profile_response['person']['nickname'])
            eq_(person_inserted.get('gender', ''), profile_response['person']['gender'])
            eq_(person_inserted['profile_id'], profile_response['person']['profile_id'])

    def correspondence_between_tokens(self, token_response, token_inserted, test_func=None):
        """
        Соответствие между двумя токенами
        :param token_response: токен полученный в качестве ответа
        :param token_inserted: токен вставленный в начале теста
        """
        eq_(token_response['token_id'], token_inserted['token_id'])
        eq_(token_response['profile_id'], token_inserted['profile_id'])
        eq_(token_response['value'], token_inserted['value'])
        ok_('application' in token_response)
        app = providers.get_application_by_id(token_inserted['application_id'])
        eq_(token_response['application'], app.name)
        if test_func:
            test_func(token_response, token_inserted)

    def correspondence_response_entity(self, response, profile_inserted, entity, test_func=None):
        """
        Соответствие ответа сущности
        :param response:
        :param profile_inserted:
        :param entity: имя сущности
        """
        json_response = get_json_response_without_errors(response)
        ok_(entity in json_response)
        method_name = 'correspondence_between_%ss' % entity
        getattr(self, method_name)(json_response[entity], profile_inserted, test_func=test_func)
        return json_response

    def correspondence_response_profile(self, response, profile_inserted, test_func=None):
        return self.correspondence_response_entity(response, profile_inserted, 'profile', test_func=test_func)

    def correspondence_response_token(self, response, token_inserted, test_func=None):
        return self.correspondence_response_entity(response, token_inserted, 'token', test_func=test_func)

    def correspondence_response_profiles(self, response, profiles_inserted, test_func=None):
        json_response = get_json_response_without_errors(response)
        ok_('profiles' in json_response)
        profiles_response = json_response['profiles']
        keyfunc = lambda profile: profile['profile_id']
        profiles_inserted = sorted(profiles_inserted, key=keyfunc)
        profiles_response = sorted(profiles_response, key=keyfunc)
        eq_(len(profiles_inserted), len(profiles_response))
        for p1, p2 in zip(profiles_response, profiles_inserted):
            self.correspondence_between_profiles(p1, p2)
            if test_func:
                test_func(p1, p2)
        return json_response

    def correspondence_response_tokens(self, response, tokens_inserted, test_func=None):
        json_response = get_json_response_without_errors(response)
        ok_('tokens' in json_response)
        tokens_response = json_response['tokens']
        keyfunc = lambda profile: profile['token_id']
        tokens_inserted = sorted(tokens_inserted, key=keyfunc)
        tokens_response = sorted(tokens_response, key=keyfunc)
        eq_(len(tokens_inserted), len(tokens_response))
        for p1, p2 in zip(tokens_response, tokens_inserted):
            self.correspondence_between_tokens(p1, p2)
            if test_func:
                test_func(p1, p2)
        return json_response

    def get_profile_from_db(self, profile_id):
        return self.engine.execute(select([pt]).where(pt.c.profile_id == profile_id)).fetchone()

    def get_profile_dict_from_db(self, profile_id):
        item = self.get_profile_from_db(profile_id)
        ok_(item)
        return dict(item)

    def get_business_map(self, token=TEST_BUSINESS_TOKEN):
        items = self.engine.execute(select([bamt]).where(bamt.c.business_token == token)).fetchall()
        return items

    def check_business_mapping(self, expected):
        items = self.get_business_map()
        map_in_db = dict((item.application_id, item.userid) for item in items)
        eq_(expected, map_in_db)

    def add_business_userid_to_db(self, id_=TEST_BUSINESS_ID, token=TEST_BUSINESS_TOKEN,
                                  userid=TEST_SIMLE_USERID, app_id=TEST_APP_ID):
        self.engine.execute(insert(bamt).values(
            business_id=id_,
            business_token=token,
            userid=userid,
            application_id=app_id,
        ))

    def get_profile_data(self, uid=TEST_UID, profile_id=None, userid=TEST_BUSINESS_USERID):
        data = {
            'uid': uid,
            'profile_id': profile_id,
            'provider_id': 2,
            'userid': userid,
            'username': 'UserName',
            'allow_auth': 0,
            'created': TEST_TASK_FINISHED_DT,
            'verified': TEST_TASK_FINISHED_DT,
            'confirmed': TEST_TASK_FINISHED_DT,
            'referer': 0,
            'yandexuid': '',
        }
        return data

    def add_profile_to_db(self, profile_data):
        self.engine.execute(insert(pt).values(
            **profile_data
        ))

    def _assert_ok_response(self, rv, expected, status_code=200):
        eq_(rv.status_code, status_code)
        rv = json.loads(rv.data)
        eq_(rv, expected)

    def _assert_error_response(self, rv, error_name, status_code=200,
                               description=Undefined):
        eq_(rv.status_code, status_code)
        rv = json.loads(rv.data)
        self.assertIn('error', rv)
        eq_(rv['error']['name'], error_name)
        if description is not Undefined:
            eq_(rv['error']['description'], description)
