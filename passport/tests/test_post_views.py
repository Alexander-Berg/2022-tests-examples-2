# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.social.common.db.schemas import sub_table
from passport.backend.social.common.test.consts import (
    APPLICATION_NAME1,
    BUSINESS_TOKEN1,
    PROFILE_ID1,
)
from passport.backend.social.proxylib.test import facebook as facebook_test

from .common import (
    build_profiles,
    error_in_json,
    TestApiViewsCase,
    tokens,
)


APPLICATIONS_CONF = [
    dict(
        provider_id=1,
        application_id=10,
        application_name='vkontakte',
        default='1',
        provider_client_id='vkonakte',
        secret='',
    ),
    dict(
        provider_id=2,
        application_id=20,
        application_name='facebook',
        default='1',
        provider_client_id='facebook',
        secret='',
    ),
    dict(
        provider_id=3,
        application_id=30,
        application_name='twitter',
        default='1',
        provider_client_id='twitter',
        secret='',
    ),
]


class TestPostApi(TestApiViewsCase):
    need_fixture = True

    def setUp(self):
        super(TestPostApi, self).setUp()
        self.fake_facebook.set_response_value(
            'get_profile',
            facebook_test.GraphApi.get_profile(
                _id=2,
                token_for_business=BUSINESS_TOKEN1,
            ),
        )
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'profile-delete',
                'profile-update',
                'subscription-create',
                'subscription-delete',
                'token-create',
                'token-delete',
                'token-update',
                'no-cred-update-token-application:facebook',
                'no-cred-update-token-application:twitter',
                'no-cred-update-token-application:vkontakte',
            ],
        )
        self.profiles = build_profiles()

    def build_settings(self):
        settings = super(TestPostApi, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings

    def last_id(self, key, entities):
        return max([e.get(key, None) for e in entities])

    def last_profile_id(self):
        return max([int(p['profile_id']) for p in self.profiles])

    def test_delete_profile(self):
        for profile in self.profiles:
            res = self.app_client.delete('/api/profile', query_string=profile)
            eq_(res.status_code, 200)
            eq_(res.data, '')

    def test_edit_profile(self):
        for profile in self.profiles:
            profile['username'] = 'vasisualiy'

            res = self.app_client.put('/api/profile', data=profile)

            self.correspondence_response_profile(res, profile)

        # TODO добавить тесты для случаев с confirmed, verified

    def test_create_token(self):
        # пытаемся создать существующие токены
        for token in tokens:
            args = token.copy()
            args['application'] = token['application_id']  # нельзя так делать

            res = self.app_client.post('/api/token', data=args)

            eq_(res.status_code, 200)
            self.correspondence_response_token(res, token)

        # создаем реально новый токен
        token = tokens[0].copy()
        token['value'] = 'yet another value'
        args = token.copy()
        args['application'] = token['application_id']  # нельзя так делать
        token['token_id'] = self.last_id('token_id', tokens)+1

        res = self.app_client.post('/api/token', data=args)

        eq_(res.status_code, 201)
        self.correspondence_response_token(res, token)

        # Пустой токен
        args = {
            'profile_id': str(PROFILE_ID1),
            'application': APPLICATION_NAME1,
            'value': '',
            'secret': '',
        }
        res = self.app_client.post('/api/token', data=args)

        error_in_json(res, 400, name='value-empty')

    def test_edit_token(self):
        # редактируем все токены
        for token in tokens:
            res = self.app_client.put('/api/token', data=token)
            self.correspondence_response_token(res, token)

    def test_delete_token(self):
        # удаляем все токены
        for token in tokens:
            res = self.app_client.delete('/api/token', query_string=token)

            eq_(res.status_code, 200)
            eq_(res.data, '')

        # пытаемся удалить токен, которого не существует
        res = self.app_client.delete('/api/token', query_string=tokens[0])
        error_in_json(res, 404, name='token-not-found')

    def test_create_subscription_exists_in_db_0_dafault_0(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=1, value=0))
        res = self.app_client.put('/api/profile/5/subscription/1')
        eq_(res.status_code, 201)

    def test_create_subscription_exists_in_db_1_dafault_0(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=1, value=1))
        res = self.app_client.put('/api/profile/5/subscription/1')
        error_in_json(res, 409, name='subscription-exists')

    def test_create_subscription_exists_in_db_0_dafault_1(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=2, value=0))
        res = self.app_client.put('/api/profile/5/subscription/2')
        eq_(res.status_code, 201)

    def test_create_subscription_exists_in_db_1_dafault_1(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=2, value=1))
        res = self.app_client.put('/api/profile/5/subscription/2')
        error_in_json(res, 409, name='subscription-exists')

    def test_create_subscription_exists_not_in_db_dafault_0(self):
        res = self.app_client.put('/api/profile/5/subscription/1')
        eq_(res.status_code, 201)

    def test_create_subscription_exists_not_in_db_dafault_1(self):
        res = self.app_client.put('/api/profile/5/subscription/2')
        error_in_json(res, 409, name='subscription-exists')

    def test_create_subscription_profile_not_found(self):
        res = self.app_client.put('/api/profile/54321/subscription/2')
        error_in_json(res, 404, name='profile-not-found')

    def test_delete_subscription_profile_not_found(self):
        res = self.app_client.delete('/api/profile/54321/subscription/5')
        error_in_json(res, 404, name='profile-not-found')

    def test_delete_subscription_exists_in_db_0_dafault_0(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=1, value=0))
        res = self.app_client.delete('/api/profile/5/subscription/1')
        error_in_json(res, 404, name='subscription-not-found')

    def test_delete_subscription_exists_in_db_1_dafault_0(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=1, value=1))
        res = self.app_client.delete('/api/profile/5/subscription/1')
        eq_(res.data, '')

    def test_delete_subscription_exists_in_db_0_dafault_1(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=2, value=0))
        res = self.app_client.delete('/api/profile/5/subscription/2')
        error_in_json(res, 404, name='subscription-not-found')

    def test_delete_subscription_exists_in_db_1_dafault_1(self):
        self.engine.execute(sub_table.insert().values(profile_id=5, sid=2, value=1))
        res = self.app_client.delete('/api/profile/5/subscription/2')
        eq_(res.data, '')

    def test_delete_subscription_exists_not_in_db_dafault_0(self):
        res = self.app_client.delete('/api/profile/5/subscription/1')
        error_in_json(res, 404, name='subscription-not-found')

    def test_delete_subscription_exists_not_in_db_dafault_1(self):
        res = self.app_client.delete('/api/profile/5/subscription/2')
        eq_(res.data, '')
