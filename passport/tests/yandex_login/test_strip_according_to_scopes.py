# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.api.api.yandex_login.utils import (
    strip_according_to_scopes,
    VerificationLevel,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


TEST_CLIENT_ID = 'test-client-id'
TEST_PAYMENT_AUTH_INFO = {'some-key': 'some-value'}


class StripTestCase(BaseTestCase):
    def setUp(self):
        super(StripTestCase, self).setUp()
        self.data = {
            'id': 123,
            'login': 'vasya.1',
            'client_id': TEST_CLIENT_ID,
            'normalized_login': 'vasya-1',
            'display_name': 'Vasya',
            'default_avatar_id': 1234,
            'is_avatar_empty': False,
            'real_name': 'Vasya Pupkin',
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
            'birthday': '1234-56-78',
            'default_email': 'aa@bb.cc',
            'sex': 'male',
            'emails': ['aa@bb.cc', 'aa2@bb2.cc2'],
            'old_social_login': 'uid-mmzxjnry',
            'has_yaru_sid': False,
            'has_plus': False,
            'phones': [
                {
                    'id': 1,
                    'number': '+79151234567',
                    'confirmed': 1162934050,
                },
                {
                    'id': 2,
                    'number': '+79167654321',
                    'confirmed': 1162934050,
                },
            ],
            'default_phone': {
                'id': 1,
                'number': '+79151234567',
            },
            'payment_auth_info': TEST_PAYMENT_AUTH_INFO,
            'verification_level': VerificationLevel.NO_VERIFIED,
        }

    def test_no_scopes(self):
        response = strip_according_to_scopes(self.data, [])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
            },
        )

    def test_all_scopes(self):
        response = strip_according_to_scopes(
            self.data,
            [
                'login:info',
                'login:birthday',
                'login:email',
                'login:avatar',
                'login:full_phones',
                'login:plus_subscriptions',
                'login:verification_level',
                'money:all',
            ],
        )
        self.data.pop('has_yaru_sid')
        self.data.pop('normalized_login')
        self.data.pop('old_social_login')
        self.data.pop('payment_auth_info')
        eq_(response, self.data)

    def test_scope_info(self):
        response = strip_according_to_scopes(self.data, ['login:info'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'display_name': 'Vasya',
                'real_name': 'Vasya Pupkin',
                'first_name': 'Vasya',
                'last_name': 'Pupkin',
                'sex': 'male',
            }
        )

    def test_scope_email(self):
        response = strip_according_to_scopes(self.data, ['login:email'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'default_email': 'aa@bb.cc',
                'emails': ['aa@bb.cc', 'aa2@bb2.cc2'],
            }
        )

    def test_scope_birthday(self):
        response = strip_according_to_scopes(self.data, ['login:birthday'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'birthday': '1234-56-78',
            },
        )

    def test_scope_birthday_but_no_birthday(self):
        self.data['birthday'] = None
        response = strip_according_to_scopes(self.data, ['login:birthday'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'birthday': None,
            },
        )

    def test_scope_avatar(self):
        response = strip_according_to_scopes(self.data, ['login:avatar'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'default_avatar_id': 1234,
                'is_avatar_empty': False,
            },
        )

    def test_scope_phones(self):
        response = strip_according_to_scopes(self.data, ['login:full_phones'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'phones': [
                    {
                        'id': 1,
                        'number': '+79151234567',
                        'confirmed': 1162934050,
                    },
                    {
                        'id': 2,
                        'number': '+79167654321',
                        'confirmed': 1162934050,
                    },
                ],
                'default_phone': {
                    'id': 1,
                    'number': '+79151234567',
                },
            },
        )

    def test_scope_default_phone(self):
        response = strip_according_to_scopes(self.data, ['login:default_phone'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'default_phone': {
                    'id': 1,
                    'number': '+79151234567',
                },
            },
        )

    def test_scope_plus_subscriptions(self):
        response = strip_according_to_scopes(self.data, ['login:plus_subscriptions'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'has_plus': False,
            },
        )

    def test_scope_verification_level(self):
        response = strip_according_to_scopes(self.data, ['login:verification_level'])
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'verification_level': VerificationLevel.NO_VERIFIED,
            },
        )

    def test_with_openid_identity(self):
        self.data['old_social_login'] = None
        response = strip_according_to_scopes(self.data, [], with_openid_identity=True)
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'openid_identities': [
                    'http://openid.yandex.ru/vasya-1/',
                ],
            },
        )

    def test_with_openid_identity_full(self):
        self.data['has_yaru_sid'] = True
        response = strip_according_to_scopes(self.data, [], with_openid_identity=True)
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'openid_identities': [
                    'http://openid.yandex.ru/uid-mmzxjnry/',
                    'http://openid.yandex.ru/vasya-1/',
                    'http://vasya-1.ya.ru/',
                ],
            },
        )

    def test_with_openid_identity_for_uncompleted_social(self):
        self.data['normalized_login'] = self.data['old_social_login']
        response = strip_according_to_scopes(self.data, [], with_openid_identity=True)
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'openid_identities': [
                    'http://openid.yandex.ru/uid-mmzxjnry/',
                ],
            },
        )

    def test_with_payment_auth_info(self):
        response = strip_according_to_scopes(self.data, ['money:all'], with_payment_auth_info=True)
        self.data['payment_auth_info'] = None
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'payment_auth_info': TEST_PAYMENT_AUTH_INFO,
            },
        )

    def test_with_payment_auth_info_but_no_payment_scopes(self):
        response = strip_according_to_scopes(self.data, [], with_payment_auth_info=True)
        self.data['payment_auth_info'] = None
        eq_(
            response,
            {
                'id': 123,
                'login': 'vasya.1',
                'client_id': TEST_CLIENT_ID,
                'payment_auth_info': None,
            },
        )
