# -*- coding: utf-8 -*-

from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.grants import get_grants_config
from passport.backend.core.grants.faker.grants import (
    FakeGrants,
    mock_grants,
)


class FakeGrantsTestCase(TestCase):
    def setUp(self):
        self.fake_grants = FakeGrants()
        self.fake_grants.start()

    def tearDown(self):
        self.fake_grants.stop()
        del self.fake_grants

    def test_set_grants_return_value(self):
        eq_(self.fake_grants._mock.call_count, 0)
        self.fake_grants.set_grants_return_value({})
        eq_(get_grants_config().config, {})
        eq_(self.fake_grants._mock.call_count, 1)

    def test_set_grants_side_effect(self):
        eq_(self.fake_grants._mock.call_count, 0)
        self.fake_grants.set_grants_side_effect(ValueError)
        with assert_raises(ValueError):
            get_grants_config().config
        eq_(self.fake_grants._mock.call_count, 1)

    def test_set_grant_list(self):
        self.fake_grants.set_grant_list(['foo.bar', 'foo.spam', 'bar.spam'])
        eq_(
            get_grants_config().config,
            {
                'dev': {
                    'grants': {
                        'foo': ['bar', 'spam'],
                        'bar': ['spam'],
                    },
                    'networks': ['127.0.0.1'],
                    'client': {},
                },
            },
        )


class TestMockGrants(TestCase):
    def test_default_values(self):
        eq_(
            mock_grants(),
            {
                'dev': {
                    'grants': {
                        # гранты для новых ручек
                        'karma': ['*'],
                        'account': ['*'],
                        'session': ['*'],
                        'password': ['*'],
                        'subscription': ['*'],
                        'person': ['*'],
                        'ignore_stoplist': ['*'],
                        'captcha': ['*'],
                        'cookies': ['*'],
                        'control_questions': ['*'],
                        'questions': ['*'],
                        'country': ['*'],
                        'timezone': ['*'],
                        'gender': ['*'],
                        'language': ['*'],
                        'login': ['*'],
                        'name': ['*'],
                        'phone_number': ['*'],
                        'retpath': ['*'],
                        'statbox': ['*'],
                        'track': ['*'],
                        'phone_bundle': ['*'],
                        'auth_password': ['*'],
                        'auth_multi': ['*'],
                        'auth_social': ['*'],
                        'auth_oauth': ['*'],
                        'auth_key': ['*'],
                        'auth_by_token': ['*'],
                        'auth_forwarding': ['*'],
                        'restore': ['*'],
                        'login_restore': ['*'],
                        'internal': ['*'],
                        'session_karma': ['*'],
                        'otp': ['*'],
                        'lastauth': ['*'],
                        'social_profiles': ['*'],
                        'security': ['*'],
                        'allow_yakey_backup': ['*'],
                        'billing': ['*'],
                        'challenge': ['*'],
                        'oauth_client': ['*'],
                        'account_suggest': ['*'],
                        'auth_by_sms': ['*'],
                        'experiments': ['*'],
                        'phonish': ['*'],
                        'takeout': ['*'],
                        # гранты для старых ручек
                        'admchangereg': ['*'],
                    },
                    'networks': ['127.0.0.1'],
                    'client': {},
                },
            },
        )

    def test_specified_values(self):
        consumer = mock.Mock()
        grants = mock.Mock()
        networks = mock.Mock()
        client_id = mock.Mock()
        eq_(
            mock_grants(consumer=consumer, grants=grants, networks=networks, client_id=client_id),
            {consumer: {'grants': grants, 'networks': networks, 'client': {'client_id': client_id}}},
        )
