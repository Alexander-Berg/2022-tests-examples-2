# -*- coding: utf-8 -*-

from datetime import datetime
from itertools import groupby
import json
import time

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.misc import parse_userid
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.test.consts import SIMPLE_USERID1

from .base_test_data import (
    TEST_BUSINESS_ID,
    TEST_BUSINESS_ID_2,
    TEST_BUSINESS_TOKEN,
    TEST_BUSINESS_TOKEN_2,
    TEST_BUSINESS_USERID,
    TEST_BUSINESS_USERID_2,
    TEST_SIMLE_USERID,
)
from .common import (
    default_sids,
    error_in_json,
    get_json_response_without_errors,
    profiles,
    subscriptions,
    TestApiViewsCase,
)


APPLICATIONS_CONF = [
    dict(
        provider_id=2,
        application_id=20,
        application_name='facebook',
        default='1',
        provider_client_id='facebook-share',
        secret='facebook-share',
        tld='ru;kz;ua;by',
    ),
    dict(
        provider_id=2,
        application_id=21,
        application_name='facebook-share1',
        provider_client_id='facebook-share1',
        secret='facebook-share',
    ),
    dict(
        provider_id=2,
        application_id=22,
        application_name='facebook-wdgt',
        provider_client_id='facebook-wdgt',
        secret='facebook-wdgt',
    ),
]


class TestGetApi(TestApiViewsCase):
    need_fixture = True

    def setUp(self):
        super(TestGetApi, self).setUp()
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'profile-read',
                'profile-list',
            ],
        )

    def build_settings(self):
        settings = super(TestGetApi, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings

    def test_get_profile(self):
        for profile in profiles:
            # По  profile_id
            response = self.app_client.get('/api/profile/%s' % profile['profile_id'])
            self.correspondence_response_profile(response, profile)

            # По  profile_id  с включенными подписками
            response = self.app_client.get('/api/profile/%s' % profile['profile_id'], query_string={'include': 'subscriptions'})
            self.correspondence_response_profile(response, profile)

            response = self.app_client.get('/api/profile/%s' % profile['profile_id'], query_string={'include': 'person'})
            ok_('person' in response.data)
            self.correspondence_response_profile(response, profile)

            response = self.app_client.get(
                '/api/profile/%s' % profile['profile_id'],
                query_string={'expand': 'provider'},
            )
            self.correspondence_response_profile(response, profile, self.check_expanded_provider)

        # отсутствующий profile id
        response = self.app_client.get('/api/profile/100500')
        error_in_json(response, 404, name='profile-not-found')

    def check_profiles(self, key, entities):
        keyfunc = lambda entity: entity[key]
        for group_key, grouped_entities in groupby(sorted(entities, key=keyfunc), keyfunc):
            response = self.app_client.get('/api/profiles', query_string={key: group_key})
            self.correspondence_response_profiles(response, grouped_entities)

    def check_expanded_provider(self, profile_response, profile_inserted):
        provider_info = providers.get_provider_info_by_id(
            profile_inserted['provider_id'], include_provider_class=True
        )
        eq_(profile_response['provider'],
            {
                'code': provider_info['code'],
                'id': provider_info['id'],
                'name': provider_info['name']
            })

    def test_get_profiles_by_uid(self):
        self.check_profiles('uid', profiles)
        response = self.app_client.get('/api/profiles', query_string={'uid': '100500'})
        self.correspondence_response_profiles(response, [])

        inserted_profiles = filter(lambda p: p.get('uid') == 1, profiles)

        response = self.app_client.get('/api/profiles', query_string={'uid': '1'})
        eq_(response.status_code, 200)
        self.correspondence_response_profiles(response, inserted_profiles)

        response = self.app_client.get('/api/profiles', query_string={'uid': '1', 'expand': 'provider'})
        self.correspondence_response_profiles(response, inserted_profiles, self.check_expanded_provider)

    def test_include_subscriptions(self):
        inserted_profiles = filter(lambda p: p.get('uid') == 1, profiles)
        response = self.app_client.get('/api/profiles', query_string={'uid': '1', 'include': 'subscriptions'})
        eq_(response.status_code, 200)
        profiles_response = self.correspondence_response_profiles(response, inserted_profiles)

        for profile in profiles_response['profiles']:
            profile_id = profile['profile_id']
            sids = set(x['sid'] for x in profile['subscriptions'])
            inserted_sids = set(p['sid'] for p in subscriptions if p['profile_id'] == profile_id)
            eq_(sids, inserted_sids.union(default_sids))

    def test_include_userid_map_and_addresses(self):
        inserted_profiles = filter(lambda p: p.get('username', '') == 'business_user', profiles)
        profile = inserted_profiles[0]

        response = self.app_client.get('/api/profiles', query_string={'uid': profile['uid']})
        eq_(response.status_code, 200)
        response = get_json_response_without_errors(response)

        response_profile = [p for p in response['profiles'] if p['profile_id'] == profile['profile_id']][0]
        found = dict((item['application_id'], item['userid']) for item in response_profile['userid_map'])
        expected = {
            20: '111',
            21: '222',
            22: '111',
            2222: '111999',
        }

        eq_(found, expected)
        eq_(response_profile['addresses'], list())

    def test_batch_include_userid_map_and_addresses(self):
        profile_simple_data = self.get_profile_data(uid=1000, profile_id=100, userid=TEST_SIMLE_USERID)
        profile_business_1_data = self.get_profile_data(uid=1000, profile_id=200, userid=TEST_BUSINESS_USERID)
        profile_business_2_data = self.get_profile_data(uid=2000, profile_id=300, userid=TEST_BUSINESS_USERID_2)

        self.add_profile_to_db(profile_simple_data)
        self.add_profile_to_db(profile_business_1_data)
        self.add_profile_to_db(profile_business_2_data)

        self.add_business_userid_to_db(TEST_BUSINESS_ID, TEST_BUSINESS_TOKEN, 111, 20)
        self.add_business_userid_to_db(TEST_BUSINESS_ID, TEST_BUSINESS_TOKEN, 222, 21)
        self.add_business_userid_to_db(TEST_BUSINESS_ID_2, TEST_BUSINESS_TOKEN_2, 333, 22)
        # Не относящиеся к делу данные, которые не должны попасть в ответ:
        self.add_business_userid_to_db(TEST_BUSINESS_ID, TEST_BUSINESS_TOKEN_2, 444, 23)
        self.add_business_userid_to_db(TEST_BUSINESS_ID_2, TEST_BUSINESS_TOKEN, 555, 20)

        response = self.app_client.get('/api/profiles', query_string={'uids': '1000,2000'})
        eq_(response.status_code, 200)
        response = get_json_response_without_errors(response)
        profiles = response['profiles']
        eq_(len(profiles), 3)
        profile_simple, profile_business_1, profile_business_2 = sorted(profiles, key=lambda p: p['profile_id'])
        eq_(profile_simple['userid_map'], [])
        eq_(
            sorted(profile_business_1['userid_map'], key=lambda item: item['application_id']),
            [
                {
                    'application': 'facebook',
                    'business_token': TEST_BUSINESS_TOKEN,
                    'application_id': 20,
                    'business_id': TEST_BUSINESS_ID,
                    'userid': '111',
                },
                {
                    'application': 'facebook-share1',
                    'business_token': TEST_BUSINESS_TOKEN,
                    'application_id': 21,
                    'business_id': TEST_BUSINESS_ID,
                    'userid': '222',
                },
            ],
        )

        eq_(
            sorted(profile_business_2['userid_map'], key=lambda item: item['application_id']),
            [
                {
                    'application': 'facebook-wdgt',
                    'business_token': TEST_BUSINESS_TOKEN_2,
                    'application_id': 22,
                    'business_id': TEST_BUSINESS_ID_2,
                    'userid': '333',
                },
            ],
        )

        eq_(profile_business_1['addresses'], list())
        eq_(profile_business_2['addresses'], list())

    def test_get_profiles_by_userid_without_business(self):
        profile = [p for p in profiles if p['provider_id'] == 1][0]
        response = self.app_client.get('/api/profiles', query_string={'userid': profile['userid'], 'provider_id': '1'})
        self.correspondence_response_profiles(response, [profile])

    def test_get_profiles_by_userid_with_business_by_userid(self):
        """
        Получаем профиль, у которого в базе составной userid,
        передаем только userid.
        """
        profile = [p for p in profiles if str(p['userid']).startswith('bt:')][0]

        response = self.app_client.get('/api/profiles', query_string={'userid': profile['userid'], 'provider_id': '2'})
        self.correspondence_response_profiles(response, [profile])

    def test_get_profiles_by_userid_with_business_by_business_token(self):
        """
        Получаем профиль, у которого в базе составной userid,
        передаем только числовой userid и бизнесс-данные.
        """
        profile = [p for p in profiles if str(p['userid']).startswith('bt:')][0]

        _, (business_id, business_token) = parse_userid(profile['userid'])

        response = self.app_client.get(
            '/api/profiles',
            query_string={'userid': profile['userid'], 'provider_id': '2', 'business_id': business_id, 'business_token': business_token},
        )
        self.correspondence_response_profiles(response, [profile])


class TestGetProfiles(TestApiViewsCase):
    need_fixture = True

    def setUp(self):
        super(TestGetProfiles, self).setUp()
        self.grants_config.add_consumer('dev', networks=['127.0.0.1'], grants=['profile-list'])

    def build_settings(self):
        settings = super(TestGetProfiles, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings

    def _make_request(self, **kwargs):
        return self.app_client.get('/api/profiles', **kwargs)

    def test_many_uids(self):
        rv = self.app_client.get('/api/profiles', query_string={'uids': '1,2'})

        eq_(rv.status_code, 200)

        expected_profiles = [
            {'username': 'inkvi', 'uid': 1, 'profile_id': 1},
            {'username': 'spleenjack', 'uid': 2, 'profile_id': 2},
            {'username': 'zzhanka', 'uid': 1, 'profile_id': 3},
        ]
        actual_profiles = json.loads(rv.data)['profiles']
        for actual, expected in zip(actual_profiles, expected_profiles):
            [eq_(actual[k], expected[k]) for k in expected]

    def test_uids(self):
        rv = self.app_client.get('/api/profiles', query_string={'uids': 2})
        self._assert_response_is_ok(rv)

    def test_uid(self):
        rv = self.app_client.get('/api/profiles', query_string={'uid': 2})
        self._assert_response_is_ok(rv)

    def test_provider_and_userid(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={'provider': Facebook.code, 'userid': 2},
        )
        self._assert_response_is_ok(rv)

    def test_provider_and_userid_and_uid(self):
        """
        Условия комбинируется через логическое И.
        """
        rv = self.app_client.get(
            '/api/profiles',
            query_string={'provider': Facebook.code, 'userid': 2, 'uid': 1},
        )

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'profiles': []})

    def test_provider_id_does_not_equal_to_provider(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={
                'provider': Facebook.code,
                'provider_id': Vkontakte.id,
                'userid': 2,
            },
        )

        eq_(rv.status_code, 403)
        rv = json.loads(rv.data)
        eq_(rv['error']['name'], 'invalid-attributes')
        eq_(rv['error']['description'], '`provider_id` conflicts with `provider`')

    def test_provider_id_only(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={'provider_id': Vkontakte.id},
        )

        eq_(rv.status_code, 403)
        rv = json.loads(rv.data)
        eq_(rv['error']['name'], 'missing-attributes')
        eq_(
            rv['error']['description'],
            'Both "userid" and ("provider_id" or "provider") or none of them should be set',
        )

    def test_user_id_only(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={'userid': 2},
        )

        eq_(rv.status_code, 403)
        rv = json.loads(rv.data)
        eq_(rv['error']['name'], 'missing-attributes')
        eq_(
            rv['error']['description'],
            'Both "userid" and ("provider_id" or "provider") or none of them should be set',
        )

    def test_no_args(self):
        rv = self.app_client.get('/api/profiles')

        eq_(rv.status_code, 403)
        rv = json.loads(rv.data)
        eq_(rv['error']['name'], 'missing-attributes')
        eq_(
            rv['error']['description'],
            'Missed required attribute `uid` or `uids` or both `userid` and `provider_id`',
        )

    def test_uid_and_uids(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={'uids': '1', 'uid': '2'},
        )

        eq_(rv.status_code, 200)
        eq_(len(json.loads(rv.data)['profiles']), 3)

    def test_include_tokens(self):
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'profile-list',
                'token-read',
                'no-cred-read-token-application:facebook',
            ],
        )

        rv = self.app_client.get(
            '/api/profiles',
            query_string={
                'uids': 2,
                'include': 'tokens',
            },
        )

        eq_(rv.status_code, 200)
        profiles = json.loads(rv.data)['profiles']
        eq_(len(profiles), 1)

        timestamp = datetime(1970, 1, 1)
        unixtime = int(time.mktime(timestamp.timetuple()))
        eq_(
            profiles[0]['tokens'],
            [
                {
                    'token_id': 2,
                    'uid': 2,
                    'profile_id': 2,
                    'value': 'values',
                    'application': 'facebook',
                    'secret': 's',
                    'scope': 'video',
                    'created': str(timestamp),
                    'created_ts': unixtime,
                    'expired': None,
                    'expired_ts': None,
                    'confirmed': None,
                    'confirmed_ts': None,
                    'verified': str(timestamp),
                    'verified_ts': unixtime,
                },
            ],
        )

    def test_include_subscriptions(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={
                'uids': 2,
                'include': 'subscriptions',
            },
        )

        eq_(rv.status_code, 200)
        profiles = json.loads(rv.data)['profiles']
        eq_(len(profiles), 1)
        eq_(
            profiles[0]['subscriptions'],
            [{'sid': 2}, {'sid': 102}, {'sid': 4}],
        )

    def test_include_person(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={
                'uids': 2,
                'include': 'person',
            },
        )

        eq_(rv.status_code, 200)
        profiles = json.loads(rv.data)['profiles']
        eq_(len(profiles), 1)
        eq_(
            profiles[0]['person'],
            {
                'profile_id': 2,
                'firstname': 'Evg',
                'lastname': 'A',
                'gender': '',
                'nickname': '',
                'birthday': None,
                'phone_number': '',
                'email': '',
            },
        )

    def test_include_many(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={
                'uids': 2,
                'include': 'person,tokens',
            },
        )

        eq_(rv.status_code, 200)
        profiles = json.loads(rv.data)['profiles']
        eq_(len(profiles), 1)
        ok_('person' in profiles[0])
        ok_('tokens' in profiles[0])

    def test_expand_provider(self):
        rv = self.app_client.get(
            '/api/profiles',
            query_string={
                'uids': 2,
                'expand': 'provider',
            },
        )

        eq_(rv.status_code, 200)
        profiles = json.loads(rv.data)['profiles']
        eq_(
            profiles[0]['provider'],
            {'code': Facebook.code, 'id': Facebook.id, 'name': 'facebook'},
        )

    def test_removed_provider_profile(self):
        self._fake_db.get_engine().execute(
            profile_table
            .insert()
            .values(
                provider_id=100500,
                uid=2,
                userid=SIMPLE_USERID1,
            ),
        )

        rv = self._make_request(query_string={'uids': '2'})

        self._assert_response_is_ok(rv)

    def _assert_response_is_ok(self, rv):
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'profiles':  [
                    {
                        'username': 'spleenjack',
                        'uid': 2,
                        'profile_id': 2,
                        'userid': '2',
                        'allow_auth': False,
                        'provider': 'facebook',
                        'provider_code': 'fb',
                        'userid_map': [],
                        'addresses': [],
                    },
                ],
            },
        )
