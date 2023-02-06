# -*- coding: utf-8 -*-

import json

from furl import furl
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    REFRESH_TOKEN1,
    SIMPLE_USERID1,
)
from passport.backend.social.proxylib.repo.MicrosoftRepo import MicrosoftRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(MicrosoftRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/oauth20_token.srf':
            return 'refresh_token'


class MicrosoftApi(object):
    @classmethod
    def refresh_token(cls, access_token=APPLICATION_TOKEN1, expires_in=APPLICATION_TOKEN_TTL1,
                      refresh_token=REFRESH_TOKEN1, user_id=SIMPLE_USERID1):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'token_type': 'bearer',
            'scope': 'wl.basic wl.birthday wl.offline_access',
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_server_error(
        cls,
        error='server_error',
        http_status_code=200,
    ):
        response = {'error': error}
        return FakeResponse(json.dumps(response), http_status_code)
