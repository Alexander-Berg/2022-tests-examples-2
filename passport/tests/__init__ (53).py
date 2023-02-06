# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from passport.backend.social.common.exception import InvalidTokenProxylibError
from passport.backend.social.common.test.test_case import TestCase
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy


class TestProxy(TestCase):
    def setUp(self):
        super(TestProxy, self).setUp()
        passport.backend.social.proxylib.init()

        self.app = Mock()
        self.app.id = '<app_id>'
        self.app.custom_provider_client_id = None
        self.app.key = '<app_key>'
        self.app.secret = '<app_secret>'
        self.app.app_server_key = None
        self.access_token = {'value': '<acces_token>', 'secret': '<token_secret>'}

        self.proxy = get_proxy(self.provider_code, self.access_token, self.app)
        self.response_mock = Mock()

    def _tst_profile_error(self, error_response=None):
        response = Mock(decoded_data=error_response or self.error_profile_response)
        response.status = 200

        with patch('passport.backend.social.proxylib.useragent.execute_request', lambda *args, **kwargs: response):
            with self.assertRaises(InvalidTokenProxylibError):
                proxy = get_proxy(self.provider_code, self.access_token, self.app)
                proxy.get_profile()

    def _process_single_test(self, processor_name, response_data, args=None,
                             kwargs=None, expected_dict=None, expected_list=None,
                             expected_value=None, expected_exception=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        self.response_mock.reset_mock()

        if isinstance(response_data, list):
            expected_calls_count = len(response_data)
            responses = [Mock(status=200, decoded_data=r, data=r) for r in response_data]
            self.response_mock.side_effect = responses
        else:
            expected_calls_count = 0 if response_data is None else 1
            response = Mock(status=200, decoded_data=response_data, data=response_data)
            self.response_mock.return_value = response

        with patch('passport.backend.social.proxylib.useragent.execute_request', self.response_mock):
            method = getattr(self.proxy, processor_name)
            try:
                response = method(*args, **kwargs)
            except Exception as ex:
                if expected_exception:
                    self.assert_(isinstance(ex, expected_exception))
                    return response
                else:
                    raise

        self.assertEquals(self.response_mock.call_count, expected_calls_count)
        if expected_dict is not None:
            self.assertDictEqual(response, expected_dict, response)
        if expected_list is not None:
            self.assertListEqual(response, expected_list, response)
        if expected_value is not None:
            self.assertEquals(response, expected_value, response)
        return response
