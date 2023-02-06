# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from furl import furl
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
)
from passport.backend.social.proxylib.repo.DnevnikRuRepo import DnevnikRuRepo
from passport.backend.utils.string import smart_str

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_DEFAULT_PERSON_PROFILE = {
    'id': '9843497619896145379',
    'firstName': 'Иван',
    'lastName': 'Иванов',
    'shortName': 'ИваИва',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(DnevnikRuRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        data = request.get('data', {})
        if path.startswith('/v2.0/users/me'):
            return 'get_user_data'
        elif path == '/v2.0/authorizations' and data.get('grant_type') == 'RefreshToken':
            return 'refresh_token'
        else:
            return 'Unresolved method for path={} and grant_type={}'.format(
                path,
                data.get('grant_type'),
            )


class DnevnikRuApi(object):
    @classmethod
    def get_user_data_for_person(cls, user={}, exclude_attrs=None):
        response = build_dict_from_standard(_DEFAULT_PERSON_PROFILE, user, exclude_attrs)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def refresh_token(
        cls, access_token=APPLICATION_TOKEN1, refresh_token=APPLICATION_TOKEN1,
        expires_in=APPLICATION_TOKEN_TTL1,
    ):
        response = {
            'accessToken': access_token,
            'expiresIn': expires_in,
            'expiresIn_str': smart_str(expires_in),
            'refreshToken': refresh_token,
            'scope': '',
            'user': 12345,
            'user_str': '12345',
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def access_token(
        cls, access_token=APPLICATION_TOKEN1, expires_in=APPLICATION_TOKEN_TTL1,
    ):
        response = {
            'accessToken': access_token,
            'expiresIn': expires_in,
            'expiresIn_str': smart_str(expires_in),
            'scope': 'string',
            'user': 12345,
            'user_str': '12345'
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_token_request_error(
        cls, status=403, error_type='invalid_client', description='Invalid client',
    ):
        response = {
            'type': error_type,
            'description': description,
        }
        return FakeResponse(json.dumps(response), status)

    @classmethod
    def build_error(cls, http_status_code=401):
        return FakeResponse('', http_status_code)

    @classmethod
    def build_invalid_token_error(cls):
        response = {'error': 'invalid_request', 'error_description': ''}
        return FakeResponse(json.dumps(response), 401)
