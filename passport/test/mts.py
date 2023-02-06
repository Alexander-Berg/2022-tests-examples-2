# -*- coding: utf-8 -*-

import base64
import json

from furl import furl
from passport.backend.social.common import oauth2
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
    UNIXTIME1,
)
from passport.backend.social.proxylib.repo.MtsRepo import MtsRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_DEFAULT_USER_V2 = {
    'acr': '',
    'aud': EXTERNAL_APPLICATION_ID1,
    'aud:name': 'MUSIC',
    'auth_time': UNIXTIME1,
    'azp': EXTERNAL_APPLICATION_ID1,
    'exp': UNIXTIME1,
    'iat': UNIXTIME1,
    'iss': 'https://login.mts.ru',
    'mobile:account': 123456789000,
    'mobile:phone': 9123456789,
    'mobile:phone:foris': 'ihelper.mts.ru',
    'mobile:phone:foris_regid': 60,
    'mobile:phone:mnp:operator:code': 'mMTS',
    'mobile:phone:mnp:region:code': 77,
    'profile:realm': '/users',
    'profile:type': 'Мобильная связь',
    'sub': 'p.123456789000.u.9123456789',
    'trust': True,
    'scope': [
        'sub',
        'mobile:phone',
        'mobile:account',
        'sso',
    ],
}

_DEFAULT_USER_V3 = {
    'account:balance': '1234.1234',
    'account:foris:name': 'ihelper.mts.ru',
    'account:iccid': '1234',
    'account:number': '123456789000',
    'account:phone': '9123456789',
    'account:service_provider_code': '1234',
    'account:service_provider_name': 'МТС Москва',
    'account:tariff:id': '1234',
    'account:tariff:name': 'Отличный',
    'account:tariff:system': 'Москва - Отличный (МАСС) (SCP)',
    'account:terminal:id': '1234',
    'birth_place': 'ГОР. ГЕРОЙ МОСКВА',
    'birthday': '1986-01-01',
    'contractnumber': '1234',
    'country': 'Россия',
    'gender': 'male',
    'given_name': 'Иван',
    'imsi': '1234',
    'is_organization': 'Person',
    'is_private': '0',
    'last_name': 'Иванов',
    'middle_name': 'Иванович',
    'mnp:operator': 'mMTS',
    'mnp:region': '77',
    'name': 'Иванов Иван Иванович',
    'phone': '9123456789',
    'picture': 'https://moskva.mts.ru/upload/images/profile_default/default-avatar-107.png',
    'premium': '0',
    'profile:type': 'Мобильная связь',
    'raw_data': [],
    'sub': '9123456789',
    'updated_at': '0',
}


def build_client_token_v1(
    kwargs=None,
    exclude_attrs=None,
):
    default_kwargs = dict(
        access_token=APPLICATION_TOKEN1,
        expires_in=APPLICATION_TOKEN_TTL1,
        scope='phone profile',
        refresh_token=APPLICATION_TOKEN2,
        version=1,
    )
    kwargs = build_dict_from_standard(default_kwargs, kwargs, exclude_attrs)
    return base64.urlsafe_b64encode(json.dumps(kwargs))


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(MtsRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/oauth2/api':
            return 'get_profile'
        elif path == '/amserver/oauth2/token':
            return 'refresh_token'
        elif path == '/amserver/oauth2/realms/root/realms/users/userinfo':
            return 'get_profile'
        elif path == '/amserver/oauth2/realms/root/realms/users/access_token':
            return 'refresh_token'


class MtsApiV2(object):
    """
    Модуль строит ответы ручек МТС API.
    """

    @classmethod
    def get_profile(cls, user={}, exclude_attrs=None):
        response = build_dict_from_standard(_DEFAULT_USER_V2, user, exclude_attrs)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def refresh_token(
        cls,
        access_token=APPLICATION_TOKEN1,
        expires_in=APPLICATION_TOKEN_TTL1,
        refresh_token=APPLICATION_TOKEN2,
    ):
        return oauth2.test.oauth2_access_token_response(
            access_token=access_token,
            expires_in=expires_in,
            refresh_token=refresh_token,
        )


class MtsApiV3(object):
    """
    Модуль строит ответы ручек МТС API.
    """

    @classmethod
    def get_profile(cls, user={}, exclude_attrs=None):
        response = build_dict_from_standard(_DEFAULT_USER_V3, user, exclude_attrs)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_invalid_token_error(self):
        response = {
            'error': 'invalid_token',
            'error_description': 'The access token provided is expired, revoked, malformed, or invalid for other reasons.',
        }
        return FakeResponse(json.dumps(response), 401)

    @classmethod
    def refresh_token(
        cls,
        access_token=APPLICATION_TOKEN1,
        expires_in=APPLICATION_TOKEN_TTL1,
    ):
        return oauth2.test.oauth2_access_token_response(
            access_token=access_token,
            expires_in=expires_in,
        )
