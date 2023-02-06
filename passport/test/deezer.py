# -*- coding: utf-8 -*-

import json

from furl import furl
from passport.backend.social.common.test.consts import (
    EMAIL1,
    SIMPLE_USERID1,
    USERNAME1,
)
from passport.backend.social.proxylib.repo.DeezerRepo import DeezerRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_DEFAULT_USER = {
    'id': SIMPLE_USERID1,
    'name': USERNAME1,
    'lastname': 'Иванов',
    'firstname': 'Иван',
    'email': EMAIL1,
    'birthday': '1931-05-28',
    'gender': 'M',
    'link': 'https://www.deezer.com/profile/' + SIMPLE_USERID1,
    'picture': 'https://api.deezer.com/user/%s/image' % SIMPLE_USERID1,
    'picture_small': 'https://cdns-images.dzcdn.net/images/user/hash/56x56-000000-80-0-0.jpg',
    'picture_medium': 'https://cdns-images.dzcdn.net/images/user/hash/250x250-000000-80-0-0.jpg',
    'picture_big': 'https://cdns-images.dzcdn.net/images/user/hash/500x500-000000-80-0-0.jpg',
    'picture_xl': 'https://cdns-images.dzcdn.net/images/user/hash/1000x1000-000000-80-0-0.jpg',
    'country': 'RU',
    'lang': 'RU',
    'status': 0,
    'inscription_date': '2016-07-08',
    'is_kid': False,
    'tracklist': 'https://api.deezer.com/user/%s/flow' % SIMPLE_USERID1,
    'type': 'user',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(DeezerRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/user/me':
            return 'get_profile'


class DeezerApi(object):
    """
    Модуль строит ответы ручек Deezer API.
    """

    @classmethod
    def get_profile(cls, user={}, exclude_attrs=None):
        response = dict(_DEFAULT_USER, **user)

        if exclude_attrs is None:
            exclude_attrs = []
        for attr in exclude_attrs:
            del response[attr]

        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_error(cls, code=200):
        # Перечень кодов здесь http://developers.deezer.com/api/errors
        response = {
            'error': {
                'code': code,
                'type': 'OloloException',
                'message': 'Blabla blablabla labla alabla',
            },
        }
        return FakeResponse(json.dumps(response), 200)
