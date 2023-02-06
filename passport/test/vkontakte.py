# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from furl import furl
from passport.backend.social.common.misc import (
    build_dict_from_standard,
    build_dict_list_from_standard,
)
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.test.consts import (
    EXTERNAL_APPLICATION_ID1,
    SIMPLE_USERID1,
    SIMPLE_USERID2,
)
from passport.backend.social.proxylib.repo.VkontakteRepo import VkontakteRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


def format_date(year, month, day):
    bits = [day, month]
    if year is not None:
        bits.append(year)
    return '.'.join(map(str, bits))


STUB_USER_AVATAR1 = 'http://vk.com/images/camera_a.gif'
STUB_USER_AVATAR2 = 'https://vk.com/images/camera_200.png'
USER_AVATAR1 = 'http://cs00.vk.me/v00/00/P1CtUr3HeR4.jpg'

UNIVERSITY1 = {
    'id': 413,
    'country': 1,
    'city': 37,
    'name': r'Дальрыбвтуз\r\n',
    'faculty': 6774,
    'faculty_name': 'Мореходный институт',
    'chair': 1943894,
    'chair_name': 'Инженерные дисциплины',
    'graduation': 2008,
    'education_form': 'Заочное отделение',
    'education_status': 'Адъюнкт',
}

_DEFAULT_PROFILE = {
    'id': SIMPLE_USERID1,
    'first_name': 'Иван',
    'last_name': 'Иванов',
    'is_closed': False,
    'can_access_closed': True,
    'sex': 2,
    'domain': 'ivanivanov',
    'nickname': 'Ivan the Great',
    'bdate': format_date(1996, 10, 25),

    'mobile_phone': '+16154324525',
    'home_phone': '+16154324526',

    'photo_50':  USER_AVATAR1,
    'photo_100': USER_AVATAR1,
    'photo_200': USER_AVATAR1,
    'photo_200_orig': USER_AVATAR1,
    'photo_400_orig': USER_AVATAR1,
    'photo_max_orig': USER_AVATAR1,

    'country': {'id': 1, 'title': 'Россия'},
    'city': {'id': 1, 'title': 'Москва'},

    'universities': [UNIVERSITY1],
}

_DEFAULT_APP = {
    'id': int(EXTERNAL_APPLICATION_ID1),
    'title': 'Тест-шмест',
    'type': 'site',
    'members_count': 1,
    'is_in_catalog': 0,
    'leaderboard_type': 0,
    'author_owner_id': int(SIMPLE_USERID2),
    'author_url': 'https://vk.com/id%s' % SIMPLE_USERID2,
    'installed': True,
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(VkontakteRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path.startswith('/method/'):
            return path[len('/method/'):]


class VkontakteApi(object):
    @classmethod
    def users_get(cls, user={}, exclude_attrs=None):
        profile = build_dict_from_standard(_DEFAULT_PROFILE, user, exclude_attrs)
        response = {'response': [profile]}
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def friends_get(cls, profile_args_list, count=None):
        profiles = build_dict_list_from_standard(_DEFAULT_PROFILE, profile_args_list)
        if count is None:
            count = len(profiles)
        response = {'response': {'count': count, 'items': profiles}}
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def account_get_app_permissions(cls, scope_mask):
        return FakeResponse(json.dumps({'response': scope_mask}), 200)

    @classmethod
    def apps_get(cls, app_args_list, count=None):
        profiles = build_dict_list_from_standard(_DEFAULT_APP, app_args_list)
        if count is None:
            count = len(profiles)
        response = {'response': {'count': count, 'items': profiles}}
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_error(cls, code, message='Message', extra_args={}):
        response = {
            'error_code': int(code),
            'error_msg': message,
        }
        if extra_args:
            response.update(extra_args)
        return FakeResponse(json.dumps({'error': response}), 200)

    @classmethod
    def build_rate_limit_exceeded_error(cls):
        return cls.build_error(code=6)


class SocialUserinfo(object):
    def __init__(self):
        self.avatar_url = None
        self.birthday = None
        self.city_id = None
        self.city_name = None
        self.country_code = None
        self.country_id = None
        self.firstname = None
        self.gender = None
        self.lastname = None
        self.nickname = None
        self.phone = None
        self.universities = None
        self.userid = None
        self.username = None

    @classmethod
    def default(cls):
        userinfo = SocialUserinfo()
        userinfo.birthday = '1996-10-25'
        userinfo.city_id = 213
        userinfo.city_name = _DEFAULT_PROFILE['city']['title']
        userinfo.country_code = 'RU'
        userinfo.country_id = 225
        userinfo.firstname = _DEFAULT_PROFILE['first_name']
        userinfo.gender = 'm'
        userinfo.lastname = _DEFAULT_PROFILE['last_name']
        userinfo.nickname = _DEFAULT_PROFILE['nickname']
        userinfo.phone = _DEFAULT_PROFILE['mobile_phone']
        userinfo.universities = [UNIVERSITY1]
        userinfo.userid = _DEFAULT_PROFILE['id']
        userinfo.username = _DEFAULT_PROFILE['domain']
        userinfo.avatar_url = USER_AVATAR1
        return userinfo

    def as_dict(self):
        retval = dict(
            avatar={
                '0x0': self.avatar_url,
                '100x100': self.avatar_url,
                '200x0': self.avatar_url,
                '200x200': self.avatar_url,
                '400x0': self.avatar_url,
                '50x50': self.avatar_url,
            },
            birthday=self.birthday,
            city_id=self.city_id,
            city_name=self.city_name,
            country_code=self.country_code,
            country_id=self.country_id,
            firstname=self.firstname,
            gender=self.gender,
            lastname=self.lastname,
            links=[
                'https://vk.com/id%s' % self.userid,
                'https://vk.com/%s' % self.username,
            ],
            nickname=self.nickname,
            phone=self.phone,
            provider=providers.get_provider_info_by_id(Vkontakte.id),
            universities=self.universities,
            userid=self.userid,
            username=self.username,
        )
        return retval
