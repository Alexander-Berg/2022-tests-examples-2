# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.broker.tests.communicators import TestCommunicator
from passport.backend.social.common.misc import dump_to_json_string


class TestGoogle(TestCommunicator):
    code = '4/vj44tfOCfKKL3jNT994ShTeJaeBA.Apv7joyI1rsSsNf4jSVKMpbwtZIXgAI'
    access_token = 'ya29.AHES6ZQrXNGoCYM7TDv_H23hiACjiNm2IDOm0dtY1J6x7OTlyBbQKh0'
    refresh_token = 'refresh-ya29.AHES6ZQrXNGoCYM7TDv_H23hiACjiNm2IDOm0dtY1J6x7OTlyBbQKh0'
    normal_access_token_response = {
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 3598,
        'id_token': 'ey...FmRw',
        'refresh_token': refresh_token,
    }
    normal_access_token_response = dump_to_json_string(normal_access_token_response)
    error_access_token_response = (400, '{"error":"invalid_grant","error_description":"Code is invalid or expired."}')

    user_denied_response = {'error': 'access_denied'}

    provider_code = 'gg'

    def setUp(self):
        super(TestGoogle, self).setUp()
        self.patcher = patch(
            'passport.backend.social.proxylib.GoogleProxy.GoogleProxy.get_profile',
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
        super(TestGoogle, self).tearDown()
        self.patcher.stop()

    def check_request_url(self, request, handler=None, data_in=None, **kwargs):
        eq_(request.method, 'POST')
        eq_(request.url, handler.communicator.OAUTH_ACCESS_TOKEN_URL)
        eq_(request.data.get('code'), self.code)
        eq_(request.data.get('redirect_uri'), 'https://social.yandex.ru/broker/redirect')
        ok_('client_id' in request.data, request.data)
        ok_('client_secret' in request.data, request.data)
        eq_(request.data.get('grant_type'), 'authorization_code')

    def test_full_gg_ok(self):
        self.check_basic()
