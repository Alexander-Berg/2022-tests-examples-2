# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from furl import furl
from passport.backend.social.common import oauth2
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
)
from passport.backend.social.proxylib.repo.XiaomiRepo import XiaomiRepo
from passport.backend.social.proxylib.XiaomiProxy import OA_INVALID_REFRESHTOKEN

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(XiaomiRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path.startswith('/oauth2/refresh'):
            return 'refresh_token'


class XiaomiApi(object):
    @classmethod
    def refresh_token(
        cls,
        access_token=APPLICATION_TOKEN1,
        refresh_token=APPLICATION_TOKEN2,
    ):
        response = oauth2.test.oauth2_access_token_response(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        return response

    @classmethod
    def build_invalid_token_error(cls):
        response = {'error': OA_INVALID_REFRESHTOKEN, 'error_description': 'Invalid Refresh Token'}
        return FakeResponse(json.dumps(response), 400)

    @classmethod
    def build_invalid_error_response(cls):
        return FakeResponse('Invalid json response', 400)
