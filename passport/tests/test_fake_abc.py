# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.builders.abc import ABC
from passport.backend.core.builders.abc.faker import (
    abc_cursor_paginated_response,
    abc_service_member,
    FakeABC,
)
from passport.backend.core.test.test_utils import with_settings


TEST_OAUTH_TOKEN = 'token'


@with_settings(
    ABC_URL='http://localhost/',
    ABC_TIMEOUT=3,
    ABC_RETRIES=2,
)
class FakeABCTestCase(TestCase):
    def setUp(self):
        self.faker = FakeABC()
        self.faker.start()
        self.abc = ABC()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_get_service_members(self):
        self.faker.set_response_value(
            'get_service_members',
            abc_cursor_paginated_response([abc_service_member()]),
        )
        eq_(
            self.abc.get_service_members(oauth_token=TEST_OAUTH_TOKEN),
            [
                {
                    'id': 1,
                    'state': 'approved',
                    'person': {
                        'id': 11,
                        'login': 'login',
                        'first_name': 'Name',
                        'last_name': 'Surname',
                        'uid': '123',
                    },
                    'service': {
                        'id': 14,
                        'slug': 'service_slug',
                        'name': {
                            'ru': u'Имя сервиса',
                            'en': 'Service name',
                        },
                        'parent': 848,
                    },
                    'role': {
                        'id': 8,
                        'name': {
                            'ru': u'Имя роли',
                            'en': 'Role name',
                        },
                        'service': None,
                        'scope': {
                            'slug': 'some_scope',
                            'name': {
                                'ru': u'Имя скоупа',
                                'en': 'Scope name',
                            },
                        },
                        'code': 'developer',
                    },
                    'created_at': '2017-12-11T16:38:18.500000Z',
                    'modified_at': '2017-12-11T16:38:18.600000Z',
                },
            ],
        )
