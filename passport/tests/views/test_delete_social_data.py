# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date

from passport.backend.social.api.test import ApiV3TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.execute import execute
from passport.backend.social.common.db.schemas import (
    person_table,
    profile_table,
)
from passport.backend.social.common.profile import ProfileCreator
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import (
    find_refresh_token_by_token_id,
    save_refresh_token,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_NAME1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    CITY1,
    CONSUMER1,
    CONSUMER_IP1,
    COUNTRY1,
    EMAIL1,
    EMAIL2,
    EXTERNAL_APPLICATION_ID1,
    FIRSTNAME1,
    LASTNAME1,
    NICKNAME1,
    PROFILE_ID1,
    PROFILE_ID2,
    SIMPLE_USERID1,
    UID1,
    UNIXTIME1,
    USERNAME1,
    USERNAME2,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import (
    find_token_by_token_id,
    save_token,
)
from sqlalchemy import select


class TestDeleteSocialData(ApiV3TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/api/delete_social_data'
    REQUEST_QUERY = {'consumer': CONSUMER1}
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
    }

    def setUp(self):
        super(TestDeleteSocialData, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['delete-social-data'],
        )

    def build_settings(self):
        settings = super(TestDeleteSocialData, self).build_settings()
        settings.update(dict(
            applications=[
                dict(
                    application_id=APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                ),
            ],
        ))
        return settings

    def _create_profile(self, birthday='2018-03-05', city=CITY1, country=COUNTRY1,
                        email=EMAIL1, firstname=FIRSTNAME1, gender='m', lastname=LASTNAME1,
                        nickname=NICKNAME1, phone='+79259164525', username=USERNAME1):
        userinfo = dict(
            birthday=birthday,
            city=city,
            country=country,
            email=email,
            firstname=firstname,
            gender=gender,
            lastname=lastname,
            nickname=nickname,
            phone=phone,
            provider={'code': 'gg'},
            userid=SIMPLE_USERID1,
            username=username,
        )
        creator = ProfileCreator(
            self._fake_db.get_engine(),
            self._fake_db.get_engine(),
            UID1,
            social_userinfo=userinfo,
            token=None,
            timestamp=UNIXTIME1,
        )
        return creator.create()

    def _assert_profile_contains(self, profile_id, attributes):
        attributes = dict(
            attributes,
            uid=UID1,
            userid=SIMPLE_USERID1,
        )
        query = select([profile_table]).where(profile_table.c.profile_id == profile_id)
        results = execute(self._fake_db.get_engine(), query).fetchall()

        self.assertEqual(len(results), 1)
        profile = results[0]

        for attr_name, attr_value in attributes.items():
            self.assertEqual(profile[attr_name], attr_value)

    def _assert_person_contains(self, profile_id, attributes):
        query = select([person_table]).where(person_table.c.profile_id == profile_id)
        results = execute(self._fake_db.get_engine(), query).fetchall()

        self.assertEqual(len(results), 1)
        profile = results[0]

        for attr_name, attr_value in attributes.items():
            self.assertEqual(profile[attr_name], attr_value)

    def _create_token_and_refresh_token(self, profile_id, value):
        token = Token(
            application_id=APPLICATION_ID1,
            profile_id=profile_id,
            value=value,
            secret=None,
            scopes=['foo', 'bar'],
            expired=None,
            created=now(),
            verified=None,
            confirmed=None,
            uid=UID1,
        )
        save_token(token, self._fake_db.get_engine())
        refresh_token = RefreshToken(
            value=value,
            expired=None,
            scopes=token.scopes,
            token_id=token.token_id,
        )
        save_refresh_token(refresh_token, self._fake_db.get_engine())
        return token

    def _assert_token_not_exist(self, token_id):
        token = find_token_by_token_id(token_id, self._fake_db.get_engine())
        self.assertIsNone(token)

    def _assert_refresh_token_not_exist(self, token_id):
        token = find_refresh_token_by_token_id(token_id, self._fake_db.get_engine())
        self.assertIsNone(token)

    def _assert_token_exists(self, token_id):
        token = find_token_by_token_id(token_id, self._fake_db.get_engine())
        self.assertIsNotNone(token)

    def _assert_refresh_token_exists(self, token_id):
        token = find_refresh_token_by_token_id(token_id, self._fake_db.get_engine())
        self.assertIsNotNone(token)

    def test_no_profile_ids(self):
        profile_id = self._create_profile(username=USERNAME1, firstname=FIRSTNAME1)

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_profile_contains(
            profile_id,
            {
                'username': USERNAME1,
            },
        )
        self._assert_person_contains(
            profile_id,
            {
                'firstname': FIRSTNAME1,
            },
        )

    def test_empty_profile_ids(self):
        self._create_profile()
        rv = self._make_request(data={'profile_ids': ''})
        self._assert_ok_response(rv)

    def test_single_profile_id(self):
        profile_id = self._create_profile(
            birthday='2018-03-05',
            city=CITY1,
            country=COUNTRY1,
            email=EMAIL1,
            firstname=FIRSTNAME1,
            gender='m',
            lastname=LASTNAME1,
            nickname=NICKNAME1,
            phone='+79259164525',
            username=USERNAME1,
        )

        rv = self._make_request(data={'profile_ids': str(profile_id)})

        self._assert_ok_response(rv)
        self._assert_profile_contains(
            profile_id,
            {
                'username': '',
            },
        )
        self._assert_person_contains(
            profile_id,
            {
                'birthday': None,
                'city': '',
                'country': '',
                'email': '',
                'firstname': '',
                'gender': '',
                'lastname': '',
                'nickname': '',
                'phone': '',
            },
        )

    def test_many_profile_ids(self):
        profile_id1 = self._create_profile(email=EMAIL1, username=USERNAME1)
        profile_id2 = self._create_profile(email=EMAIL2, username=USERNAME2)

        profile_ids = ','.join(map(str, [profile_id1, profile_id2]))
        rv = self._make_request(data={'profile_ids': profile_ids})

        self._assert_ok_response(rv)
        self._assert_profile_contains(profile_id1, {'username': ''})
        self._assert_person_contains(profile_id1, {'email': ''})
        self._assert_profile_contains(profile_id2, {'username': ''})
        self._assert_person_contains(profile_id2, {'email': ''})

    def test_profile_not_found(self):
        profile_id = self._create_profile(
            birthday='2018-03-05',
            city=CITY1,
            country=COUNTRY1,
            email=EMAIL1,
            firstname=FIRSTNAME1,
            gender='m',
            lastname=LASTNAME1,
            nickname=NICKNAME1,
            phone='+79259164525',
            username=USERNAME1,
        )

        assert profile_id != 5558
        rv = self._make_request(data={'profile_ids': '5558'})

        self._assert_ok_response(rv)
        self._assert_profile_contains(profile_id, {'username': USERNAME1})
        self._assert_person_contains(
            profile_id,
            {
                'birthday': date(2018, 3, 5),
                'city': CITY1,
                'country': COUNTRY1,
                'email': EMAIL1,
                'firstname': FIRSTNAME1,
                'gender': 'm',
                'lastname': LASTNAME1,
                'nickname': NICKNAME1,
                'phone': '+79259164525',
            },
        )

    def test_many_tokens(self):
        token1 = self._create_token_and_refresh_token(PROFILE_ID1, APPLICATION_TOKEN1)
        token2 = self._create_token_and_refresh_token(PROFILE_ID1, APPLICATION_TOKEN2)

        rv = self._make_request(data={'profile_ids': str(PROFILE_ID1)})

        self._assert_ok_response(rv)
        self._assert_token_not_exist(token1.token_id)
        self._assert_refresh_token_not_exist(token1.token_id)
        self._assert_token_not_exist(token2.token_id)
        self._assert_refresh_token_not_exist(token2.token_id)

    def test_token_not_found(self):
        token = self._create_token_and_refresh_token(PROFILE_ID1, APPLICATION_TOKEN1)

        rv = self._make_request(data={'profile_ids': str(PROFILE_ID2)})

        self._assert_ok_response(rv)
        self._assert_token_exists(token.token_id)
        self._assert_refresh_token_exists(token.token_id)
