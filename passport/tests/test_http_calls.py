# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_

from .common import (
    get_json_response_without_errors,
    is_not_found_json,
    TestApiViewsCase,
)


APPLICATIONS_CONF = [
    dict(
        provider_id=1,
        application_id=10,
        application_name='vkontakte',
        default='1',
        provider_client_id='vkontakte',
        secret='',
    ),
    dict(
        provider_id=10,
        application_id=100,
        application_name='livejournal',
        default='1',
        provider_client_id='livejournal',
        secret='livejournal',
    ),
]


class TestApiCase(TestApiViewsCase):
    need_fixture = True

    def setUp(self):
        super(TestApiCase, self).setUp()
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'profile-list',
                'profile-read',
                'token-read',
                'no-cred-read-token-application:livejournal',
                'no-cred-read-token-application:vkontakte',
            ],
        )

    def build_settings(self):
        settings = super(TestApiCase, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings

    def test_no_consumer(self):
        self.app_client = self.app.test_client()
        r = self.app_client.get('/api/profile/1')
        get_json_response_without_errors(r)

    def test_get_profile(self):
        rv = self.app_client.get(r'/api/profile/0123')
        is_not_found_json(rv, name='profile-not-found')

        r = self.app_client.get('/api/profile/1')
        get_json_response_without_errors(r)

    def test_get_profiles_by_uid(self):
        rv = self.app_client.get('/api/profiles', query_string={'uid': '0312312'})
        json_response = get_json_response_without_errors(rv)
        eq_(json_response['profiles'], [])
        get_json_response_without_errors(
            self.app_client.get('/api/profiles', query_string={'uid': 1}),
        )

    def test_get_token(self):
        rv = self.app_client.get('/api/token', query_string={'token_id': '0123'})
        is_not_found_json(rv, name='token-not-found')
        get_json_response_without_errors(
            self.app_client.get('/api/token', query_string={'token_id': 1}),
        )

    def test_get_tokens_newest(self):
        query_string = {'profile_id': 1}
        rv = self.app_client.get(
            '/api/token/newest',
            query_string=dict(query_string, application_id=100),
        )
        is_not_found_json(rv, name='token-not-found')
        get_json_response_without_errors(
            self.app_client.get(
                '/api/token/newest',
                query_string=dict(query_string, application_id=10),
            ),
        )

    def test_get_tokens_newest_and_scope(self):
        query_string = {'profile_id': 1, 'scope': 'offline'}
        rv = self.app_client.get(
            '/api/token/newest',
            query_string=dict(query_string, application_id=100),
        )
        is_not_found_json(rv, name='token-not-found')
        get_json_response_without_errors(
            self.app_client.get(
                '/api/token/newest',
                query_string=dict(query_string, application_id=10),
            ),
        )

if __name__ == '__main__':
    unittest.main()
