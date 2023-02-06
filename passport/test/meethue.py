# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from furl import furl
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    APPLICATION_TOKEN_TTL2,
)
from passport.backend.social.proxylib.repo.MeethueRepo import MeethueRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(MeethueRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path.startswith('/oauth2/refresh'):
            return 'refresh_token'


class MeethueApi(object):
    @classmethod
    def refresh_token(
        cls,
        access_token=APPLICATION_TOKEN1,
        refresh_token=APPLICATION_TOKEN2,
        access_token_expires_in=APPLICATION_TOKEN_TTL1,
        refresh_token_expires_in=APPLICATION_TOKEN_TTL2,
    ):
        if access_token_expires_in:
            access_token_expires_in = str(access_token_expires_in)
        if refresh_token_expires_in:
            refresh_token_expires_in = str(refresh_token_expires_in)
        response = {
            'access_token': access_token,
            'access_token_expires_in': access_token_expires_in,
            'refresh_token': refresh_token,
            'refresh_token_expires_in': refresh_token_expires_in,
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_invalid_token_error(cls):
        response = {'ErrorCode': 'invalid_request', 'Error': 'Invalid Refresh Token'}
        return FakeResponse(json.dumps(response), 400)

    @classmethod
    def build_invalid_error_response(cls):
        return FakeResponse('Invalid json response', 400)
