# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from urllib import urlencode

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.time_utils.time_utils import TimeSpan
from passport.backend.social.broker.tests.communicators import TestCommunicator


class TestVkontakte(TestCommunicator):
    code = 'ad39fc9328361b4acd'
    normal_access_token_response = '{"access_token":"d37524b3dc4d18d91f0d5db3ff2093fce62e15f4126b7adfe8d1ded179e0d86f59f49516fda74463d1c51","expires_in":0,"user_id":197299775,"email":"test@mail.tld"}'
    access_token = 'd37524b3dc4d18d91f0d5db3ff2093fce62e15f4126b7adfe8d1ded179e0d86f59f49516fda74463d1c51'
    error_access_token_response = (400, '{"error":"invalid_grant","error_description":"Code is invalid or expired."}')
    user_denied_response = {'error': 'access_denied'}

    provider_code = 'vk'

    def setUp(self):
        super(TestVkontakte, self).setUp()
        self.patcher = patch(
            'passport.backend.social.proxylib.VkontakteProxy.VkontakteProxy.get_profile',
            Mock(
                return_value={
                    'userid': 100,
                    'firstname': 'Petr',
                    'lastname': 'Testov',
                    'username': 'luigi',
                },
            ),
        )
        self.patcher.start()

    def tearDown(self):
        super(TestVkontakte, self).tearDown()
        self.patcher.stop()

    def get_statbox_saved_data(self):
        statbox_data = {
            'action': 'saved',
            'userid': '100',
            'elapsed_seconds': TimeSpan(0),
            'email': 'test@mail.tld',
        }
        return statbox_data

    def check_request_url(self, request, handler=None, data_in=None, **kwargs):
        eq_(request.method, 'GET')
        eq_(request.url, handler.communicator.OAUTH_ACCESS_TOKEN_URL)
        eq_(request.query.get('code'), self.code)

        expected_callback_url = 'https://socialdev-1.yandex.ru/broker2/%s/callback' % (data_in['task_id'])
        expected_redirect_uri = (
            'https://social.yandex.ru/broker/redirect?' +
            urlencode({'url': expected_callback_url})
        )
        eq_(request.query.get('redirect_uri'), expected_redirect_uri)

        ok_('client_id' in request.query, request.query)
        ok_('client_secret' in request.query, request.query)

    def test_full_vk_ok(self):
        self.check_basic()
