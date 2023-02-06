# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re

from furl import furl
from nose.tools import ok_
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
    SIMPLE_USERID1,
)
from passport.backend.social.proxylib.repo.FacebookRepo import FacebookRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_DEFAULT_USER = {
    'id': 1,
    'first_name': 'first_name',
    'last_name': 'last_name',
    'gender': 'male',
    'picture': {
        'data': {
            'url': 'http://www.facebook.com/zoooo/mbie/',
            'is_silhouette': False,
        },
    },
    'birthday': '05/13',  # '05/13/1900' or '1900' or '05/13'
    'email': 'zoom@biecti.on',
}

_DEFAULT_TOKEN_INFO = {
    'user_id': SIMPLE_USERID1,
    'scopes': ['user_birthday', 'email', 'public_profile'],
    'app_id': EXTERNAL_APPLICATION_ID1,
    'application': u'Яндекс',
    'is_valid': True,
    'issued_at': 1472735606,
    'expires_at': 1477919606,
}


_DEFAULT_PROFILE_LINK = 'https://www.facebook.com/app_scoped_user_id/abcd/'


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(FacebookRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/v10.0/me/friends':
            return 'get_friends'
        elif path == '/v10.0/me' or re.match(r'^/v10\.0/\d+$', path):
            return 'get_profile'
        elif path == '/v10.0/debug_token':
            return 'get_token_info'
        elif path == '/v10.0/oauth/access_token' and url.args['grant_type'] == 'fb_exchange_token':
            return 'exchange_token'


class GraphApi(object):
    """
    Модуль строит ответы ручек Facebook Graph API версии 10.0.
    """

    @classmethod
    def get_friends(cls, users, total_count=None):
        if total_count is None:
            total_count = len(users)
        ok_(total_count >= len(users))

        response = {
            'data': [dict(_DEFAULT_USER, **u) for u in users],
            'summary': {'total_count': total_count},
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def get_profile(cls, _id=1, **kwargs):
        response = {'id': str(_id)}
        response.update(kwargs)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def get_token_info(cls, response={}):
        response = dict(response)
        for key, default in _DEFAULT_TOKEN_INFO.iteritems():
            response.setdefault(key, default)
        return FakeResponse(json.dumps({'data': response}), 200)

    @classmethod
    def exchange_token(cls, access_token=APPLICATION_TOKEN1, expires_in=APPLICATION_TOKEN_TTL1):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
            'token_type': 'bearer',
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def get_profile_links(cls, _id=1, url=None):
        if url is None:
            url = _DEFAULT_PROFILE_LINK
        response = {
            'id': str(_id),
            'link': url,
        }
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_error(cls, _type='OAuthException', code=2500, message='Message'):
        response = {
            'error': {
                'type': _type,
                'code': code,
                'message': message,
                'fbtrace_id': 'AaawrUA92dJ',
            }
        }
        return FakeResponse(json.dumps(response), 400)
