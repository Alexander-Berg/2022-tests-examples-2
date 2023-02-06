# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.oauth.core.logs.base_tskv_logger import tskv_value
from passport.backend.oauth.core.logs.common import mask_sensitive_fields
from passport.backend.oauth.core.test.framework import BaseTestCase


class TestMaskSensitiveFields(BaseTestCase):
    def test_ok(self):
        data = {
            'login': 'login',
            'password': 'password',
            'client_secret': 'secret',
            'access_token': 'token///',
            'oauth_token': 'oken1234',
            'token_alias': 'alia',
            'refresh_token': 'rf',
            'sessionid': 'cookie',
            'otp': '1234567890',
            'track': '1234.abc',
        }
        masked_data = mask_sensitive_fields(data)
        eq_(
            masked_data,
            {
                'login': 'login',
                'password': '*****',
                'client_secret': '*****',
                'access_token': 'toke****',
                'oauth_token': 'oken****',
                'token_alias': 'a***',
                'refresh_token': 'r*',
                'sessionid': '*****',
                'otp': '*****',
                'track': '1234.***',
            },
        )

    def test_nested_ok(self):
        data = {
            'clients': [
                {
                    'name': 'test',
                    'secrets': {
                        'client_secret': 'secret',
                        'access_token': 'token',
                        'not_a_secret': 'not-a-secret',
                    },
                },
            ],
            'user_secrets': {
                'login': 'login',
                'password': 'password',
                'sessionid': 'cookie',
            },
            'secret': [1, 2, 42],
        }
        masked_data = mask_sensitive_fields(data)
        eq_(
            masked_data,
            {
                'clients': [
                    {
                        'name': 'test',
                        'secrets': {
                            'client_secret': '*****',
                            'access_token': 'to***',
                            'not_a_secret': 'not-a-secret',
                        },
                    },
                ],
                'user_secrets': {
                    'login': 'login',
                    'password': '*****',
                    'sessionid': '*****',
                },
                'secret': '*****',
            },
        )

    def test_ok_with_custom_fields(self):
        data = {
            'login': 'login',
            'password': 'password',
        }
        masked_data = mask_sensitive_fields(data, fields=['login'])
        eq_(
            masked_data,
            {
                'login': '*****',
                'password': 'password',
            },
        )

    def test_nothing_to_mask(self):
        data = {
            'login': 'login',
        }
        masked_data = mask_sensitive_fields(data)
        eq_(
            masked_data,
            {
                'login': 'login',
            },
        )
        ok_(masked_data is not data)

    def test_track_no_dots_ok(self):
        data = {
            'track': 'abc',
        }
        masked_data = mask_sensitive_fields(data)
        eq_(
            masked_data,
            {
                'track': '*****',
            },
        )

    def test_track_several_dots_ok(self):
        data = {
            'track': 'abc.def.g123.t45',
        }
        masked_data = mask_sensitive_fields(data)
        eq_(
            masked_data,
            {
                'track': 'abc.def.g123.***',
            },
        )


class TestTskvValue(BaseTestCase):
    def test_ok(self):
        eq_(tskv_value(123), '123')
        eq_(tskv_value('123'), '123')
        eq_(tskv_value(True), '1')
        eq_(tskv_value(False), '0')

    def test_invalid_encoding(self):
        eq_(tskv_value('Hello, \xc8\xc0\xd3'), 'Hello, \xc8\xc0\xd3')

    def test_truncate(self):
        eq_(tskv_value('a' * 2000), 'a' * 1000)
