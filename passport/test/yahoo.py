# -*- coding: utf-8 -*-

import json

from furl import furl
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    REFRESH_TOKEN1,
    SIMPLE_USERID1,
)
from passport.backend.social.proxylib.repo.YahooRepo import YahooRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_USERINFO_DEFAULT_PROFILE = {
    'sub': 'ABCDEFGH1JKLMNOPQRSTUVWXY7',
    'given_name': 'Joe',
    'family_name': 'Average',
    'locale': 'ru-RU',
    'email': 'averagejoe@yahoo.com',
    'email_verified': True,
    'nickname': 'Joe',
    'picture': 'https://s.yimg.com/ag/images/18598556-0dda-42c5-bb78-ddbb6cc833c8_192sq.jpg',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(YahooRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/oauth2/get_token':
            return 'refresh_token'
        elif path == '/openid/v1/userinfo':
            return 'userinfo'


class YahooApi(object):
    @classmethod
    def userinfo(cls, user={}):
        profile = _USERINFO_DEFAULT_PROFILE.copy()
        profile.update(user)
        return FakeResponse(json.dumps(profile), 200)

    @classmethod
    def refresh_token(cls, access_token=APPLICATION_TOKEN1, expires_in=APPLICATION_TOKEN_TTL1,
                      refresh_token=REFRESH_TOKEN1, user_id=SIMPLE_USERID1):
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': expires_in,
            'xoauth_yahoo_guid': user_id,
            'token_type': 'bearer',
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_invalid_token_error(cls):
        return FakeResponse('', 401)
