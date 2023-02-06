# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import (
    CaptchaNeededProxylibError,
    InvalidTokenProxylibError,
    UnexpectedResponseProxylibError,
    ValidationRequiredProxylibError,
)
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_SECRET2,
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
    SIMPLE_USERID1,
    SIMPLE_USERID2,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.useragent import Url
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import vkontakte as vkontakte_test
from passport.backend.social.proxylib.test.base import FakeResponse


class VkontakteTestCase(TestCase):
    def setUp(self):
        super(VkontakteTestCase, self).setUp()
        self._proxy = vkontakte_test.FakeProxy().start()
        passport.backend.social.proxylib.init()

        self._p = get_proxy(
            Vkontakte.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
                key=APPLICATION_SECRET2,
            ),
        )

    def tearDown(self):
        self._proxy.stop()
        super(VkontakteTestCase, self).tearDown()


class TestGetProfile(VkontakteTestCase):
    def test_basic(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(),
        )

        rv = self._p.get_profile()

        self.assertEqual(
            rv,
            {
                'userid': SIMPLE_USERID1,
                'firstname': 'Иван',
                'lastname': 'Иванов',
                'gender': 'm',
                'username': 'ivanivanov',
                'nickname': 'Ivan the Great',
                'birthday': '1996-10-25',
                'phone': '+16154324525',
                'country_id': 225,
                'country_code': 'RU',
                'city_id': 213,
                'city_name': 'Москва',
                'avatar': {
                    '50x50': vkontakte_test.USER_AVATAR1,
                    '100x100': vkontakte_test.USER_AVATAR1,
                    '200x200': vkontakte_test.USER_AVATAR1,
                    '200x0': vkontakte_test.USER_AVATAR1,
                    '400x0': vkontakte_test.USER_AVATAR1,
                    '0x0': vkontakte_test.USER_AVATAR1,
                },
                'universities': [
                    {
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
                    },
                ],
            },
        )

        self.assertEqual(
            self._proxy.requests,
            [
                {
                    'url': str(
                        Url(
                            'https://api.vk.com/method/users.get',
                            {
                                'access_token': 'abcdef',
                                'fields': ','.join(
                                    [
                                        'domain',
                                        'last_name',
                                        'sex',
                                        'photo_200',
                                        'mobile_phone',
                                        'photo_max_orig',
                                        'nickname',
                                        'id',
                                        'universities',
                                        'city',
                                        'first_name',
                                        'bdate',
                                        'contacts',
                                        'country',
                                        'photo_200_orig',
                                        'photo_50',
                                        'home_phone',
                                        'photo_100',
                                        'photo_400_orig',
                                    ],
                                ),
                                'v': '5.131',
                            },
                        ),
                    ),
                    'data': None,
                    'headers': None,
                },
            ],
        )

    def test_sex_female(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'sex': 1}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['gender'], 'f')

    def test_sex_male(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'sex': 2}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['gender'], 'm')

    def test_no_sex(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'sex': 0}),
        )

        rv = self._p.get_profile()

        self.assertNotIn('gender', rv)

    def test_domain(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'domain': 'heLLo'}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['username'], 'heLLo')

    def test_no_domain(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'id': '123456', 'domain': 'id123456'}),
        )

        rv = self._p.get_profile()

        self.assertNotIn('username', rv)

    def test_nickname(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'nickname': 'Kartoha man'}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['nickname'], 'Kartoha man')

    def test_no_nickname(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'nickname': ''}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['nickname'], '')

    def test_bdate(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'bdate': vkontakte_test.format_date(1997, 11, 26)}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['birthday'], '1997-11-26')

    def test_bdate__no_year(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'bdate': vkontakte_test.format_date(None, 11, 26)}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['birthday'], '0000-11-26')

    def test_hidden_bdate(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(exclude_attrs={'bdate'}),
        )

        rv = self._p.get_profile()

        self.assertNotIn('birthday', rv)

    def test_mobile_phone(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'mobile_phone': '+79259164525', 'home_phone': ''}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['phone'], '+79259164525')

    def test_home_phone(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'home_phone': '+79259164525', 'mobile_phone': ''}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['phone'], '+79259164525')

    def test_many_phones(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'home_phone': '+79259164525', 'mobile_phone': '+79026411724'}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['phone'], '+79026411724')

    def test_no_phones(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'home_phone': '', 'mobile_phone': ''}),
        )

        rv = self._p.get_profile()

        self.assertNotIn('phone', rv)

    def test_city(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'city': {'id': 1, 'title': 'Москва'}}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['city_id'], 213)
        self.assertEqual(rv['city_name'], 'Москва')

    def test_no_city(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(exclude_attrs={'city'}),
        )

        rv = self._p.get_profile()

        self.assertNotIn('city_id', rv)
        self.assertNotIn('city_name', rv)
        self.assertNotIn('country_id', rv)
        self.assertNotIn('country_code', rv)

    def test_country(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'country': {'id': 1, 'title': 'Россия'}}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['country_id'], 225)
        self.assertEqual(rv['country_code'], 'RU')

    def test_city_and_no_country(self):
        # Хоть пользовательский интерфейс ВК и не позволяет создавать таких
        # пользователей, но в дикой природе они встречаются.
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(
                {'city': {'id': 1, 'title': 'Москва'}},
                exclude_attrs={'country'},
            ),
        )

        rv = self._p.get_profile()

        self.assertNotIn('city_id', rv)
        self.assertNotIn('city_name', rv)
        self.assertNotIn('country_id', rv)
        self.assertNotIn('country_code', rv)

    def test_no_universities(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'universities': []}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['universities'], [])

    def test_university(self):
        university = {
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
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({'universities': [university]}),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['universities'], [university])

    def test_avatars(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'photo_50': 'http://cs00.vk.me/v00/00/50.jpg',
                'photo_100': 'http://cs00.vk.me/v00/00/100.jpg',
                'photo_200': 'http://cs00.vk.me/v00/00/200.jpg',
                'photo_200_orig': 'http://cs00.vk.me/v00/00/200g.jpg',
                'photo_400_orig': 'http://cs00.vk.me/v00/00/400g.jpg',
                'photo_max_orig': 'http://cs00.vk.me/v00/00/0g.jpg',
            }),
        )

        rv = self._p.get_profile()

        self.assertEqual(
            rv['avatar'],
            {
                '50x50': 'http://cs00.vk.me/v00/00/50.jpg',
                '100x100': 'http://cs00.vk.me/v00/00/100.jpg',
                '200x200': 'http://cs00.vk.me/v00/00/200.jpg',
                '200x0': 'http://cs00.vk.me/v00/00/200g.jpg',
                '400x0': 'http://cs00.vk.me/v00/00/400g.jpg',
                '0x0': 'http://cs00.vk.me/v00/00/0g.jpg',
            },
        )

    def test_no_avatars(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'photo_50': vkontakte_test.STUB_USER_AVATAR1,
                'photo_100': vkontakte_test.STUB_USER_AVATAR2,
                'photo_200': vkontakte_test.STUB_USER_AVATAR1,
                'photo_200_orig': vkontakte_test.STUB_USER_AVATAR2,
                'photo_400_orig': vkontakte_test.STUB_USER_AVATAR1,
                'photo_max_orig': vkontakte_test.STUB_USER_AVATAR2,
            }),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['avatar'], {})

    def test_avatar_is_false(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(
                {
                    'photo_50': 'http://cs00.vk.me/v00/00/50.jpg',
                    'photo_100': False,
                },
                exclude_attrs=['photo_200', 'photo_200_orig', 'photo_400_orig', 'photo_max_orig'],
            ),
        )

        rv = self._p.get_profile()

        self.assertEqual(rv['avatar'], {'50x50': 'http://cs00.vk.me/v00/00/50.jpg'})


class TestFails(VkontakteTestCase):
    def test_authorization_failed(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.build_error(5),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.get_profile()

    def test_captcha_required(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.build_error(
                code=14,
                extra_args={
                    'captcha_sid': '384975402830',
                    'captcha_img': 'http://api.vk.com/captcha.php?sid=384975402830',
                },
            ),
        )

        with self.assertRaises(CaptchaNeededProxylibError):
            self._p.get_profile()

    def test_validation_required(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.build_error(
                code=17,
                extra_args={
                    'redirect_uri': 'https://m.vk.com/login?act=security_check&api_hash=57bd908d9c93bd5fbe',
                },
            ),
        )

        with self.assertRaises(ValidationRequiredProxylibError):
            self._p.get_profile()

    def test_unexpected_fail(self):
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.build_error(600),
        )

        with self.assertRaises(UnexpectedResponseProxylibError):
            self._p.get_profile()

    def test_not_json_value(self):
        self._proxy.set_response_value(
            'users.get',
            FakeResponse('invalid json', 200),
        )

        with self.assertRaises(UnexpectedResponseProxylibError):
            self._p.get_profile()

    def test_empty_value(self):
        self._proxy.set_response_value(
            'users.get',
            FakeResponse('', 200),
        )

        with self.assertRaises(UnexpectedResponseProxylibError):
            self._p.get_profile()


class TestGetFriends(VkontakteTestCase):
    def test_no_friends(self):
        self._proxy.set_response_value(
            'friends.get',
            vkontakte_test.VkontakteApi.friends_get([]),
        )

        rv = self._p.get_friends()

        self.assertEqual(rv, [])

        self.assertEqual(
            self._proxy.requests,
            [
                {
                    'url': str(
                        Url(
                            'https://api.vk.com/method/friends.get',
                            {
                                'access_token': 'abcdef',
                                'fields': ','.join(
                                    [
                                        'domain',
                                        'last_name',
                                        'sex',
                                        'photo_200',
                                        'mobile_phone',
                                        'photo_max_orig',
                                        'nickname',
                                        'id',
                                        'universities',
                                        'city',
                                        'first_name',
                                        'bdate',
                                        'contacts',
                                        'country',
                                        'photo_200_orig',
                                        'photo_50',
                                        'home_phone',
                                        'photo_100',
                                        'photo_400_orig',
                                    ],
                                ),
                                'v': '5.131',
                            },
                        ),
                    ),
                    'data': None,
                    'headers': None,
                },
            ],
        )

    def test_one_friend(self):
        self._proxy.set_response_value(
            'friends.get',
            vkontakte_test.VkontakteApi.friends_get([{}]),
        )

        rv = self._p.get_friends()

        self.assertEqual(
            rv,
            [
                {
                    'userid': SIMPLE_USERID1,
                    'firstname': 'Иван',
                    'lastname': 'Иванов',
                    'gender': 'm',
                    'username': 'ivanivanov',
                    'nickname': 'Ivan the Great',
                    'birthday': '1996-10-25',
                    'phone': '+16154324525',
                    'country_id': 225,
                    'country_code': 'RU',
                    'city_id': 213,
                    'city_name': 'Москва',
                    'avatar': {
                        '50x50': vkontakte_test.USER_AVATAR1,
                        '100x100': vkontakte_test.USER_AVATAR1,
                        '200x200': vkontakte_test.USER_AVATAR1,
                        '200x0': vkontakte_test.USER_AVATAR1,
                        '400x0': vkontakte_test.USER_AVATAR1,
                        '0x0': vkontakte_test.USER_AVATAR1,
                    },
                    'universities': [
                        {
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
                        },
                    ],
                },
            ],
        )

    def test_many_friends(self):
        self._proxy.set_response_value(
            'friends.get',
            vkontakte_test.VkontakteApi.friends_get([
                {},
                {
                    'values': {
                        'id': SIMPLE_USERID2,
                        'first_name': 'Пётр',
                        'last_name': 'Петров',
                        'domain': 'id' + SIMPLE_USERID2,
                        'nickname': '',
                        'universities': [],
                    },
                    'exclude_attrs': {'city', 'country'},
                },
            ]),
        )

        rv = self._p.get_friends()

        self.assertEqual(
            rv,
            [
                {
                    'userid': SIMPLE_USERID1,
                    'firstname': 'Иван',
                    'lastname': 'Иванов',
                    'gender': 'm',
                    'username': 'ivanivanov',
                    'nickname': 'Ivan the Great',
                    'birthday': '1996-10-25',
                    'phone': '+16154324525',
                    'country_id': 225,
                    'country_code': 'RU',
                    'city_id': 213,
                    'city_name': 'Москва',
                    'avatar': {
                        '50x50': vkontakte_test.USER_AVATAR1,
                        '100x100': vkontakte_test.USER_AVATAR1,
                        '200x200': vkontakte_test.USER_AVATAR1,
                        '200x0': vkontakte_test.USER_AVATAR1,
                        '400x0': vkontakte_test.USER_AVATAR1,
                        '0x0': vkontakte_test.USER_AVATAR1,
                    },
                    'universities': [
                        {
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
                        },
                    ],
                },
                {
                    'userid': SIMPLE_USERID2,
                    'firstname': 'Пётр',
                    'lastname': 'Петров',
                    'gender': 'm',
                    'nickname': '',
                    'birthday': '1996-10-25',
                    'phone': '+16154324525',
                    'avatar': {
                        '50x50': vkontakte_test.USER_AVATAR1,
                        '100x100': vkontakte_test.USER_AVATAR1,
                        '200x200': vkontakte_test.USER_AVATAR1,
                        '200x0': vkontakte_test.USER_AVATAR1,
                        '400x0': vkontakte_test.USER_AVATAR1,
                        '0x0': vkontakte_test.USER_AVATAR1,
                    },
                    'universities': [],
                },
            ],
        )

    def test_no_universities(self):
        self._proxy.set_response_value(
            'friends.get',
            vkontakte_test.VkontakteApi.friends_get([
                {
                    'exclude_attrs': {'universities'},
                },
            ]),
        )

        rv = self._p.get_friends()

        self.assertNotIn('universities', rv[0])

    def test_public_only__with_userid(self):
        self._proxy.set_response_value(
            'friends.get',
            vkontakte_test.VkontakteApi.friends_get([]),
        )

        rv = self._p.get_friends(SIMPLE_USERID1, public_only=True)

        self.assertEqual(rv, [])

        self.assertEqual(len(self._proxy.requests), 1)
        request = self._proxy.requests[0]
        check_url_equals(
            request['url'],
            str(
                Url(
                    'https://api.vk.com/method/friends.get',
                    params={
                        'user_id': str(SIMPLE_USERID1),
                        'fields': ','.join(
                            [
                                'domain',
                                'last_name',
                                'sex',
                                'photo_200',
                                'mobile_phone',
                                'photo_max_orig',
                                'nickname',
                                'id',
                                'universities',
                                'city',
                                'first_name',
                                'bdate',
                                'contacts',
                                'country',
                                'photo_200_orig',
                                'photo_50',
                                'home_phone',
                                'photo_100',
                                'photo_400_orig',
                            ],
                        ),
                        'v': '5.131',
                        'access_token': APPLICATION_SECRET2,
                    },
                ),
            ),
        )
        self.assertIsNone(request['data'])
        self.assertIsNone(request['headers'])

    def test_public_only__no_userid(self):
        self._proxy.set_response_value(
            'friends.get',
            vkontakte_test.VkontakteApi.friends_get([]),
        )
        self._proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(),
        )

        rv = self._p.get_friends(None, public_only=True)

        self.assertEqual(rv, [])

        self.assertEqual(len(self._proxy.requests), 2)
        request1 = self._proxy.requests[0]
        check_url_equals(
            request1['url'],
            str(
                Url(
                    'https://api.vk.com/method/users.get',
                    params={
                        'access_token': APPLICATION_TOKEN1,
                        'fields': ','.join(
                            [
                                'domain',
                                'last_name',
                                'sex',
                                'photo_200',
                                'mobile_phone',
                                'photo_max_orig',
                                'nickname',
                                'id',
                                'universities',
                                'city',
                                'first_name',
                                'bdate',
                                'contacts',
                                'country',
                                'photo_200_orig',
                                'photo_50',
                                'home_phone',
                                'photo_100',
                                'photo_400_orig',
                            ],
                        ),
                        'v': '5.131',
                    },
                ),
            ),
        )
        self.assertIsNone(request1['data'])
        self.assertIsNone(request1['headers'])
        request2 = self._proxy.requests[1]
        check_url_equals(
            request2['url'],
            str(
                Url(
                    'https://api.vk.com/method/friends.get',
                    params={
                        'user_id': str(SIMPLE_USERID1),
                        'fields': ','.join(
                            [
                                'domain',
                                'last_name',
                                'sex',
                                'photo_200',
                                'mobile_phone',
                                'photo_max_orig',
                                'nickname',
                                'id',
                                'universities',
                                'city',
                                'first_name',
                                'bdate',
                                'contacts',
                                'country',
                                'photo_200_orig',
                                'photo_50',
                                'home_phone',
                                'photo_100',
                                'photo_400_orig',
                            ],
                        ),
                        'v': '5.131',
                        'access_token': APPLICATION_SECRET2,
                    },
                ),
            ),
        )
        self.assertIsNone(request2['data'])
        self.assertIsNone(request2['headers'])

    def test_private__with_userid(self):
        self._proxy.set_response_value(
            'friends.get',
            vkontakte_test.VkontakteApi.friends_get([]),
        )

        rv = self._p.get_friends(SIMPLE_USERID1)

        self.assertEqual(rv, [])

        self.assertEqual(
            self._proxy.requests,
            [
                {
                    'url': str(
                        Url(
                            'https://api.vk.com/method/friends.get',
                            {
                                'access_token': 'abcdef',
                                'fields': ','.join(
                                    [
                                        'domain',
                                        'last_name',
                                        'sex',
                                        'photo_200',
                                        'mobile_phone',
                                        'photo_max_orig',
                                        'nickname',
                                        'id',
                                        'universities',
                                        'city',
                                        'first_name',
                                        'bdate',
                                        'contacts',
                                        'country',
                                        'photo_200_orig',
                                        'photo_50',
                                        'home_phone',
                                        'photo_100',
                                        'photo_400_orig',
                                    ],
                                ),
                                'v': '5.131',
                            },
                        ),
                    ),
                    'data': None,
                    'headers': None,
                },
            ],
        )


class TestGetTokenInfo(VkontakteTestCase):
    def test_basic(self):
        self._proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(scope_mask=123456),
        )
        self._proxy.set_response_value(
            'apps.get',
            vkontakte_test.VkontakteApi.apps_get([{'id': 12345}]),
        )

        rv = self._p.get_token_info()

        self.assertEqual(
            rv,
            {
                'client_id': '12345',
                'scopes': ['questions', 'wall', 'ads', 'offline'],
            },
        )
        self.assertEqual(
            self._proxy.requests,
            [
                {
                    'url': 'https://api.vk.com/method/apps.get?access_token=abcdef&v=5.131',
                    'data': None,
                    'headers': None,
                },
                {
                    'url': 'https://api.vk.com/method/account.getAppPermissions?access_token=abcdef&v=5.131',
                    'data': None,
                    'headers': None,
                },
            ],
        )

    def test_client_id_not_required(self):
        self._proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(scope_mask=123456),
        )

        rv = self._p.get_token_info(need_client_id=False)

        self.assertEqual(rv, {'scopes': ['questions', 'wall', 'ads', 'offline']})
        self.assertEqual(
            self._proxy.requests,
            [
                {
                    'url': 'https://api.vk.com/method/account.getAppPermissions?access_token=abcdef&v=5.131',
                    'data': None,
                    'headers': None,
                },
            ],
        )


class TestGetProfileLinks(VkontakteTestCase):
    def test_basic(self):
        links = self._p.get_profile_links('12345', 'some_user')
        self.assertEqual(
            set(links),
            set(['https://vk.com/some_user', 'https://vk.com/id12345']),
        )
