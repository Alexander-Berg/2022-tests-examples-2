# -*- coding: utf-8 -*-
from datetime import datetime
import json

from passport.backend.core.builders.blackbox.blackbox import parse_blackbox_oauth_response
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.oauth.api.api.yandex_login.utils import (
    parse_blackbox_response,
    VerificationLevel,
)
from passport.backend.oauth.core.test.framework import BaseTestCase
from passport.backend.oauth.core.test.utils import iter_eq


TEST_META = 'meta'
TEST_CLIENT_NAME = 'client-name'
TEST_CONTEXT_ID = 'context-id'
TEST_SCOPE_ADDENDUM = '{some-json}'


class ParseBlackboxResponseTestCase(BaseTestCase):
    def setUp(self):
        super(ParseBlackboxResponseTestCase, self).setUp()
        self.kwargs = {
            'uid': 123,
            'display_name': {'name': 'Vasya'},
            'default_avatar_key': 1234,
            'subscribed_to': [4, 46],
            'dbfields': {
                'subscription.login.8': 'Vasya.1',
            },
            'attributes': {
                'account.normalized_login': 'vasya-1',
                'person.firstname': 'Vasya',
                'person.lastname': 'Pupkin',
                'person.gender': 'm',
                'person.birthday': '1234-56-79',
            },
            'aliases': {
                'social': 'uid-mmzxjnry',
            },
            'emails': [
                {
                    'address': 'aa@bb.cc',
                    'default': True,
                    'validated': True,
                    'native': True,
                },
                {
                    'address': 'aa2@bb2.cc2',
                    'default': False,
                    'validated': True,
                    'native': False,
                },
            ],
            'phones': [
                {
                    'number': '+79151234567',
                    'id': 1,
                    'bound': datetime.fromtimestamp(100),
                    'secured': datetime.fromtimestamp(101),
                    'is_default': True,
                },
                {
                    'number': '+79167654321',
                    'id': 2,
                    'bound': datetime.fromtimestamp(101),
                    'admitted': datetime.fromtimestamp(200),
                },
                {
                    'number': '+79167654322',
                    'id': 3,
                    'bound': datetime.fromtimestamp(102),
                    'confirmed': datetime.fromtimestamp(200),
                },
                {
                    'number': '+79167654323',
                    'id': 4,
                    'confirmed': datetime.fromtimestamp(300),
                },
            ],
            'scope': 'login:info login:email money:scope1 money:scope2',
            'oauth_token_info': {
                'client_name': TEST_CLIENT_NAME,
                'meta': TEST_META,
                'payment_auth_context_id': TEST_CONTEXT_ID,
                'payment_auth_scope_addendum': TEST_SCOPE_ADDENDUM,
            },
        }
        self.expected = {
            'id': '123',
            'login': 'Vasya.1',
            'client_id': 'fake_clid',
            'display_name': 'Vasya',
            'default_avatar_id': 1234,
            'is_avatar_empty': False,
            'real_name': 'Vasya Pupkin',
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
            'birthday': '1234-56-79',
            'default_email': 'aa@bb.cc',
            'sex': 'male',
            'emails': ['aa@bb.cc'],
            'old_social_login': 'uid-mmzxjnry',
            'normalized_login': 'vasya-1',
            'has_yaru_sid': False,
            'has_plus': False,
            'verification_level': VerificationLevel.LOW_VERIFIED,
            'phones': [
                {
                    'id': 1,
                    'number': '+79151234567',
                    'confirmed': 100,
                },
                {
                    'id': 2,
                    'number': '+79167654321',
                    'confirmed': 200,
                },
                {
                    'id': 3,
                    'number': '+79167654322',
                    'confirmed': 200,
                },
            ],
            'default_phone': {
                'id': 1,
                'number': '+79151234567',
            },
            'payment_auth_info': {
                'scopes': ['money:scope1', 'money:scope2'],
                'client_name': TEST_CLIENT_NAME,
                'meta': TEST_META,
                'context_id': TEST_CONTEXT_ID,
                'scope_addendum': TEST_SCOPE_ADDENDUM,
            },
        }

    def make_and_parse_blackbox_response(self):
        data = parse_blackbox_oauth_response(json.loads(blackbox_oauth_response(**self.kwargs)))
        return parse_blackbox_response(data)

    def test_ok(self):
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_no_avatar(self):
        self.kwargs.update(
            default_avatar_key='0/0-0',
            is_avatar_empty=True,
        )
        self.expected.update(
            default_avatar_id='0/0-0',
            is_avatar_empty=True,
        )
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_reversed_emails(self):
        self.kwargs['emails'] = reversed(self.kwargs['emails'])
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_gender_female(self):
        self.kwargs['attributes']['person.gender'] = 'f'
        self.expected['sex'] = 'female'
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_gender_unknown(self):
        self.kwargs['attributes']['person.gender'] = '?'
        self.expected['sex'] = None
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_gender_none(self):
        self.kwargs['attributes']['person.gender'] = None
        self.expected['sex'] = None
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_returns_empty_list_if_no_emails(self):
        self.kwargs['emails'] = []
        self.expected['emails'] = []
        self.expected['default_email'] = ''
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_returns_empty_list_if_no_phones(self):
        self.kwargs['phones'] = []
        self.expected['phones'] = []
        self.expected['default_phone'] = None
        self.expected['verification_level'] = VerificationLevel.NO_VERIFIED
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_yaru_sid(self):
        self.kwargs['attributes']['subscription.37'] = '1'
        self.expected['has_yaru_sid'] = True
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_plus_subscriptions(self):
        self.kwargs['attributes']['account.have_plus'] = '1'
        self.expected['has_plus'] = True
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_no_default_phone(self):
        self.kwargs['phones'][0].pop('secured')
        self.expected['default_phone'] = None
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_has_secure_phone(self):
        self.kwargs['phones'][0]['secured'] = datetime.fromtimestamp(100)
        self.kwargs['phones'][0]['confirmed'] = datetime.fromtimestamp(100)
        self.expected['verification_level'] = VerificationLevel.HIGH_VERIFIED
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )

    def test_without_payment_auth(self):
        self.kwargs['scope'] = 'login:info login:email'
        self.kwargs['oauth_token_info']['meta'] = ''
        del self.kwargs['oauth_token_info']['payment_auth_context_id']
        del self.kwargs['oauth_token_info']['payment_auth_scope_addendum']
        self.expected['payment_auth_info'] = {
            'scopes': [],
            'client_name': TEST_CLIENT_NAME,
            'meta': '',
            'context_id': None,
            'scope_addendum': None,
        }
        iter_eq(
            self.make_and_parse_blackbox_response(),
            self.expected,
        )
