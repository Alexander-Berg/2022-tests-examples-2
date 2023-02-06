# -*- coding: utf-8 -*-
from passport.backend.perimeter.auth_api.logging_utils.formatters import mask_sensitive_fields
from passport.backend.perimeter.auth_api.test import BaseTestCase


class TestMaskSensitiveFields(BaseTestCase):
    def test_ok(self):
        data = {
            'login': 'login',
            'password': 'password',
        }
        masked_data = mask_sensitive_fields(data)
        assert masked_data['login'] == 'login'
        assert masked_data['password'].startswith('***')
        assert 'password' not in masked_data['password']

    def test_ok_with_custom_fields(self):
        data = {
            'login': 'login',
            'password': 'password',
        }
        masked_data = mask_sensitive_fields(data, fields=['login'])
        assert masked_data['login'].startswith('***')
        assert 'login' not in masked_data['login']
        assert masked_data['password'] == 'password'

    def test_nothing_to_mask(self):
        data = {
            'login': 'login',
        }
        masked_data = mask_sensitive_fields(data)
        assert masked_data == {'login': 'login'}
        assert masked_data is not data
