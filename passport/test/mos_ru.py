# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from furl import furl
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
)
from passport.backend.social.proxylib.repo.MosRuRepo import MosRuRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_DEFAULT_PERSON_PROFILE = {
    'guid': '9843497619896145379',
    'FirstName': 'Иван',
    'LastName': 'Иванов',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(MosRuRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        data = request.get('data', {})
        if path.startswith('/auth/authenticationWS/getUserData'):
            return 'get_user_data'
        elif path == '/sps/oauth/oauth20/token' and data.get('grant_type') == 'refresh_token':
            return 'refresh_token'


class MosRuApi(object):
    @classmethod
    def get_user_data_for_person(cls, user={}, exclude_attrs=None):
        response = build_dict_from_standard(_DEFAULT_PERSON_PROFILE, user, exclude_attrs)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def refresh_token(cls, access_token=APPLICATION_TOKEN1, refresh_token=APPLICATION_TOKEN1,
                      expires_in=APPLICATION_TOKEN_TTL1):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
            'scope': '',
            'token_type': 'bearer',
            'refresh_token': refresh_token,
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_error(cls, http_status_code=401):
        return FakeResponse('', http_status_code)

    @classmethod
    def build_invalid_token_error(cls):
        response = {'error': 'invalid_request', 'error_description': ''}
        return FakeResponse(json.dumps(response), 401)
