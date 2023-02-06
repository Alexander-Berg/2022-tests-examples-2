# -*- coding: utf-8 -*-

import json

from furl import furl
from passport.backend.social.common.chrono import now
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    EMAIL1,
    EXTERNAL_APPLICATION_ID1,
    SIMPLE_USERID1,
)
from passport.backend.social.proxylib.repo.GoogleRepo import GoogleRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


DEFAULT_TOKEN_INFO = {
    'sub': SIMPLE_USERID1,
    'aud': EXTERNAL_APPLICATION_ID1,
    'scope': ' '.join([
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
    ]),
    'email': EMAIL1,
    'email_verified': 'true',
    'access_type': 'offline',
    'expires_in': '3538',
    'exp': '1472662858',
    'azp': EXTERNAL_APPLICATION_ID1,
}


DEFAULT_PROFILE_INFO = {
    'sub': SIMPLE_USERID1,
    'email': EMAIL1,
    'name': 'Ivan Ivanov',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(GoogleRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/oauth2/v3/token':
            grant_type = request.get('data', dict()).get('grant_type')
            if grant_type == 'refresh_token':
                return 'refresh_token'
            elif grant_type == 'authorization_code':
                return 'exchange_authorization_code_to_token'
        elif path == '/oauth2/v3/userinfo':
            return 'get_profile'
        elif path == '/oauth2/v3/tokeninfo':
            return 'get_token_info'
        elif path.startswith('/data/feed/api/user/default/albumid/'):
            return 'get_photos'


class GoogleApi(object):
    @classmethod
    def refresh_token(cls, access_token=APPLICATION_TOKEN1, expires_in=APPLICATION_TOKEN_TTL1):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
            'token_type': 'Bearer',
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def exchange_auth_code_to_token(cls, access_token=APPLICATION_TOKEN1,
                                    expires_in=APPLICATION_TOKEN_TTL1,
                                    refresh_token=None):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
            'token_type': 'Bearer',
        }
        if refresh_token is not None:
            response['refresh_token'] = refresh_token
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def get_token_info(cls, response={}):
        # https://developers.google.com/identity/protocols/OAuth2UserAgent#validatetoken
        response = dict(response)
        response.setdefault('expires_in', DEFAULT_TOKEN_INFO['expires_in'])
        expires_at = now.i() + int(response['expires_in'])
        response.setdefault('exp', str(expires_at))
        for key, default in DEFAULT_TOKEN_INFO.iteritems():
            response.setdefault(key, default)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def get_token_info__fail(cls):
        response = {'error_description': 'Invalid Value'}
        return FakeResponse(json.dumps(response), 400)

    @classmethod
    def get_profile(cls, response={}):
        response = dict(response)
        for key, default in DEFAULT_PROFILE_INFO.iteritems():
            response.setdefault(key, default)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_error(cls,
                    error='invalid_token',
                    error_description='The access token provided is invalid',
                    http_status_code=401):
        response = {'error': error}
        if error_description is not None:
            response['error_description'] = error_description
        return FakeResponse(json.dumps(response), http_status_code)

    @classmethod
    def build_invalid_token_error(cls):
        return cls.build_error(error='invalid_token', error_description='Invalid Credentials', http_status_code=401)

    @classmethod
    def build_invalid_grant_error(cls):
        return cls.build_error(error='invalid_grant', error_description='Bad Request', http_status_code=400)

    @classmethod
    def build_backend_error(cls):
        return FakeResponse(json.dumps({'error_description': 'Backend Error'}), 503)

    @classmethod
    def build_internal_failure_error(cls):
        return FakeResponse(json.dumps({'error': 'internal_failure'}), 500)


class SocialUserinfo(object):
    def __init__(self):
        self.userid = None

    @classmethod
    def default(cls):
        userinfo = SocialUserinfo()
        userinfo.userid = DEFAULT_PROFILE_INFO['sub']
        return userinfo

    def as_dict(self):
        retval = dict(
            links=[
                'https://plus.google.com/%s' % self.userid,
            ],
            provider=providers.get_provider_info_by_id(Google.id),
            userid=self.userid,
        )
        return retval
