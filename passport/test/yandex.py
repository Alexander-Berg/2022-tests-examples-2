# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from furl import furl
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.proxylib import YandexProxy
from passport.backend.social.proxylib.repo.YandexRepo import YandexRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_DEFAULT_PROFILE = {
    'id': '12345',
    'first_name': 'Иван',
    'last_name': 'Иванов',
    'login': 'ivanov',
    'display_name': 'Ivanov the Best',
    'emails': ['ivan@yandex.ru'],
    'default_email': 'ivan@yandex.ru',
    'real_name': 'Иван Иванов',
    'birthday': '1931-05-28',
    'default_avatar_id': '4321/12345-123456',
    'sex': 'male',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(YandexRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/info':
            return 'get_profile'


class YandexApi(object):
    @classmethod
    def get_profile(cls, user={}, exclude_attrs=None):
        profile = build_dict_from_standard(_DEFAULT_PROFILE, user, exclude_attrs)
        return FakeResponse(json.dumps(profile), 200)

    @classmethod
    def build_error(cls):
        return FakeResponse('', 401)

    @classmethod
    def build_backend_error(cls):
        return FakeResponse('Service temporarily unavailable', 503)


class SocialUserinfo(object):
    def __init__(self):
        self.avatar_id = None
        self.birthday = None
        self.email = None
        self.firstname = None
        self.gender = None
        self.lastname = None
        self.userid = None
        self.username = None

    @classmethod
    def default(cls):
        userinfo = SocialUserinfo()
        userinfo.avatar_id = _DEFAULT_PROFILE['default_avatar_id']
        userinfo.birthday = _DEFAULT_PROFILE['birthday']
        userinfo.email = _DEFAULT_PROFILE['emails'][0]
        userinfo.firstname = _DEFAULT_PROFILE['first_name']
        userinfo.gender = 'm'
        userinfo.lastname = _DEFAULT_PROFILE['last_name']
        userinfo.userid = _DEFAULT_PROFILE['id']
        userinfo.username = _DEFAULT_PROFILE['display_name']
        return userinfo

    def as_dict(self):
        retval = dict(
            birthday=self.birthday,
            email=self.email,
            firstname=self.firstname,
            gender=self.gender,
            lastname=self.lastname,
            links=list(),
            provider=providers.get_provider_info_by_id(Yandex.id),
            userid=self.userid,
            username=self.username,
        )
        retval.update(
            avatar=YandexProxy.Avatars.from_avatar_id(self.avatar_id).as_dict(),
            default_avatar_id=self.avatar_id,
        )
        return retval
