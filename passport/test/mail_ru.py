# -*- coding: utf-8 -*-

import json

from furl import furl
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    REFRESH_TOKEN1,
    SIMPLE_USERID1,
)
from passport.backend.social.proxylib.repo.MailRuRepo import MailRuRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_O1_HOSTNAME = 'www.appsmail.ru'
_O2_HOSTNAME = 'o2.mail.ru'

_O2_DEFAULT_PROFILE = {
    'id': SIMPLE_USERID1,
    'email': 'ivanov@mail.ru',
    'name': 'Иван Иванов',
    'first_name': 'Иван',
    'last_name': 'Иванов',
    'gender': 'm',
    'locale': 'ru_RU',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(MailRuRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if url.host == _O2_HOSTNAME and path == '/userinfo':
            return 'get_profile'
        elif (url.host == _O1_HOSTNAME and path == '/oauth/token' or
              url.host == _O2_HOSTNAME and path == '/token'):
            return 'refresh_token'


class MailRuApi(object):
    @classmethod
    def refresh_token(cls, access_token=APPLICATION_TOKEN1, expires_in=APPLICATION_TOKEN_TTL1,
                      refresh_token=REFRESH_TOKEN1):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
            'refresh_token': refresh_token,
            'x_mailru_vid': '12345678912345678912',
        }
        return FakeResponse(json.dumps(response), 200)


class MailRuO2Api(object):
    @classmethod
    def get_profile(cls, user={}, exclude_attrs=None):
        profile = build_dict_from_standard(_O2_DEFAULT_PROFILE, user, exclude_attrs)
        return FakeResponse(json.dumps(profile), 200)

    @classmethod
    def refresh_token(cls, access_token=APPLICATION_TOKEN1, expires_in=APPLICATION_TOKEN_TTL1):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_error(cls, error='token not found', error_code=6,
                    error_description='token not found', http_status_code=200):
        response = {
            'error': error,
            'error_code': error_code,
            'error_description': error_description,
        }
        return FakeResponse(json.dumps(response), http_status_code)
