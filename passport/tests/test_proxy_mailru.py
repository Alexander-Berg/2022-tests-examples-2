# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common.exception import (
    InvalidTokenProxylibError,
    ProviderTemporaryUnavailableProxylibError,
)
from passport.backend.social.common.misc import dump_to_json_string
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.MailRu import MailRu
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    MAIL_RU_APPLICATION_NAME2,
    REFRESH_TOKEN1,
)
from passport.backend.social.common.test.fake_useragent import FakeUseragent
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.useragent import build_http_pool_manager
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.repo.MailRuRepo import ProfileDoesNotHaveMoiMirAccountError
from passport.backend.social.proxylib.test import mail_ru as mail_ru_test

from . import TestProxy


class TestProxyMailRu(TestProxy):
    provider_code = 'mr'
    error_profile_response = '{"error":{"error_msg":"User authorization failed: the session or uid key is invalid.","error_code":102}}'

    def test_profile(self):
        decoded_data = (
            '[{"pic_50":"http://avt.appsmail.ru/mail/user/_avatar50","friends_count":0,'
            '"pic_22":"http://avt.appsmail.ru/mail/user/_avatar22","nick":"NickName",'
            '"age":23,"is_friend":0,"is_verified":0,"is_online":0,"pic_big":"http://avt.appsmail.ru/'
            'mail/user/_avatarbig","last_name":"LName","has_pic":1,"email":"user@mail.ru",'
            '"pic_190":"http://avt.appsmail.ru/mail/user/_avatar190","referer_id":"","vip":0,'
            '"pic_32":"http://avt.appsmail.ru/mail/user/_avatar32",'
            '"birthday":"28.12.1989","referer_type":"","link":"http://my.mail.ru/mail/user/",'
            '"last_visit":"1382092306","uid":"13817221511430939912",'
            '"app_installed":1,"status_text":"","pic_128":"http://avt.appsmail.ru/mail/user'
            '/_avatar128","sex":0,"pic":"http://avt.appsmail.ru/mail/user/_avatar",'
            '"pic_small":"http://avt.appsmail.ru/mail/user/_avatarsmall","pic_180":'
            '"http://avt.appsmail.ru/mail/user/_avatar180","pic_40":"http://avt.appsmail.ru/'
            'mail/user/_avatar40","first_name":"Name"}]'
        )

        expected_dict = {u'username': u'user@mail.ru', u'firstname': u'Name', u'lastname': u'LName',
                         u'userid': '13817221511430939912', u'birthday': u'1989-12-28',
                         u'avatar': {u'600x0': u'http://avt.appsmail.ru/mail/user/_avatarbig',
                                     u'45x0': u'http://avt.appsmail.ru/mail/user/_avatarsmall',
                                     u'90x0': u'http://avt.appsmail.ru/mail/user/_avatar'},
                         u'gender': u'm', u'nickname': u'NickName', u'email': u'user@mail.ru'}

        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_profile_error(self):
        self._tst_profile_error()

    def test_profile_does_not_have_moi_mir_account(self):
        moi_mir_error_response = '{"error":{"error_msg":"empty users","error_token":"NONE","extended":null,"error_code":204}}'
        response = Mock(decoded_data=moi_mir_error_response)
        response.status = 400

        with patch('passport.backend.social.proxylib.useragent.execute_request', lambda *args, **kwargs: response):
            with self.assertRaises(ProfileDoesNotHaveMoiMirAccountError) as cm:
                proxy = get_proxy(self.provider_code, self.access_token, self.app)
                proxy.get_profile()

            self.assertEquals(cm.exception.message, 'empty users')

    def test_get_mails_unread_count_ok(self):
        decoded_data = '{"count":2}'
        self._process_single_test(
            'get_mails_unread_count',
            decoded_data,
            expected_value=2,
        )

    def test_get_mails_unread_count_invalid_data(self):
        decoded_data = '[]'
        self._process_single_test(
            'get_mails_unread_count',
            decoded_data,
            expected_value=0,
        )

    def test_get_friends(self):
        decoded_data = (
            '[{"pic_50":"http://avt.appsmail.ru/bk/nick/_avatar50","pic_22":"http://avt.appsmail.ru/bk/nick/'
            '_avatar22","nick":"Nick","age":31,"is_friend":1,"is_verified":0,"is_online":0,"pic_big":'
            '"http://avt.appsmail.ru/bk/nick/_avatarbig","last_name":"LName","has_pic":1,"pic_190":'
            '"http://avt.appsmail.ru/bk/nick/_avatar190","vip":0,"pic_32":"http://avt.appsmail.ru/bk/nick/'
            '_avatar32","birthday":"27.11.1981","link":"http://my.mail.ru/bk/nick/","last_visit":null,'
            '"location":{"country":{"name":"Россия","id":"24"},"city":{"name":"Нижний Новгород","id":"526"},'
            '"region":{"name":"Нижегородская обл.","id":"242"}},"uid":"10644135012664590000","app_installed":0,'
            '"status_text":"","pic_128":"http://avt.appsmail.ru/bk/nick/_avatar128","sex":1,"pic":'
            '"http://avt.appsmail.ru/bk/nick/_avatar","pic_small":"http://avt.appsmail.ru/bk/nick/_avatarsmall"'
            ',"pic_180":"http://avt.apsmail.ru/bk/nick/_avatar180","pic_40":"http://avt.appsmail.ru/bk/nick'
            '/_avatar40","first_name":"Name"}]'
        )

        expected_list = [
            {
                u'firstname': u'Name',
                u'lastname': u'LName',
                u'userid': u'10644135012664590000',
                u'birthday': u'1981-11-27',
                u'avatar': {
                    u'600x0': u'http://avt.appsmail.ru/bk/nick/_avatarbig',
                    u'45x0': u'http://avt.appsmail.ru/bk/nick/_avatarsmall',
                    u'90x0': u'http://avt.appsmail.ru/bk/nick/_avatar',
                },
                u'gender': u'f',
                u'nickname': u'Nick',
            },
        ]

        self._process_single_test(
            'get_friends',
            decoded_data,
            expected_list=expected_list,
        )

    def test_get_profile_links(self):
        proxy = get_proxy(self.provider_code)
        links = proxy.get_profile_links('12345', 'some_user@list.ru')
        eq_(links, [u'http://my.mail.ru/list/some_user'])

    def test_get_photo_albums(self):
        decoded_data = (
            '[{"link":"url","description":"","size":1,"aid":"myphoto","created":1382963518,"cover_pid":"1",'
            '"cover_url":"url","title":"Фото со мной","updated":1382963519,"privacy":2},{"link":"url","owner":'
            '"17296813064748254003","description":"album_description","size":0,"aid":"1","created":1392722767,'
            '"cover_pid":"","cover_url":"url","title":"album_test","updated":1392722767,"privacy":2}]'
        )
        expected_list = [
            {
                u'photo_count': 1,
                u'description': u'',
                u'title': u'\u0424\u043e\u0442\u043e \u0441\u043e \u043c\u043d\u043e\u0439',
                u'url': u'url',
                u'created': 1382963518,
                u'visibility': 'public',
                u'aid': u'myphoto',
            },
            {
                u'photo_count': 0,
                u'description': u'album_description',
                u'title': u'album_test',
                u'url': u'url',
                u'created': 1392722767,
                u'visibility': 'public',
                u'aid': u'1',
            },
        ]

        self._process_single_test(
            'get_photo_albums',
            decoded_data,
            kwargs={'userid': 1},
            expected_list=expected_list,
        )

    def test_create_photo_album(self):
        decoded_data = {
            'link': 'http://foto.mail.ru/mail/flidster/1/',
            'owner': '17296813064748254003',
            'description': 'album_description',
            'size': 0,
            'aid': '1',
            'created': 1392722767,
            'cover_pid': '',
            'cover_url': 'http://img.imgsmail.ru/r/foto2/covers/cover1.jpg',
            'title': 'album_test',
            'updated': 1392722767,
            'privacy': 2,
        }
        decoded_data = dump_to_json_string(decoded_data)

        self._process_single_test(
            'create_photo_album',
            decoded_data,
            kwargs={
                'title': 'title',
                'description': 'descr',
                'privacy': 'public',
                'userid': 1,
            },
            expected_dict={u'aid': u'1'},
        )

    def test_get_photos(self):
        decoded_data = (
            '[{"src_big":"url","thread_id":"33c3a70633c3a7060400000003000000","width":600,"owner":"17296813'
            '064748254003","src":"url2","height":281,"size":45668,"aid":"3","created":1389970664,"pid":"4","s'
            'rc_small":"url3","title":"photo title"},{"src_big":"url","thread_id":"33c3a70633c3a70607000000030'
            '00000","width":104,"owner":"17296813064748254003","src":"url2","height":48,"size":2867,"aid":'
            '"3","created":1392650524,"pid":"7","src_small":"url3","title":"dfdf"}]'
        )
        expected_list = [
            {
                u'created': 1389970664,
                u'pid': u'4',
                u'caption': u'photo title',
                u'images': [
                    {u'url': u'url3', u'width': 120, u'height': 120},
                    {u'url': u'url2', u'width': 600, u'height': 281},
                    {u'url': u'url'},
                ],
            },
            {
                u'created': 1392650524,
                u'pid': u'7',
                u'caption': u'dfdf',
                u'images': [
                    {u'url': u'url3', u'width': 104, u'height': 48},
                    {u'url': u'url2', u'width': 104, u'height': 48},
                    {u'url': u'url'},
                ],
            },
        ]

        expected_dict = {
            'result': expected_list,
        }
        self._process_single_test(
            'get_photos',
            decoded_data,
            kwargs={'aid': 'aid', 'userid': 1},
            expected_dict=expected_dict,
        )

    def test_photo_post_get_request(self):
        expected_dict = {
            u'url': u'http://www.appsmail.ru/platform/api?secure=1&app_id=%3Capp_id%3E&sig=42bb7f66aa9'
                    u'b753c9d6d656c8f8b16e0&aid=aid&session_key=%3Cacces_token%3E&method=photos.upload&name=caption',
            u'image_name': u'img_file',
        }
        self._process_single_test(
            'photo_post_get_request',
            None,
            kwargs={'aid': 'aid', 'caption': 'caption'},
            expected_dict=expected_dict,
        )

    def test_photo_post_commit(self):
        upload_response = (
            '{"src_big":"http://content-3.foto.my.mail.ru/mail/flidster/3/h-7.jpg","thread_id":"33c'
            '3a70633c3a7060700000003000000","width":104,"owner":"17296813064748254003","src":"http:/'
            '/content-7.foto.my.mail.ru/mail/flidster/3/i-7.jpg","height":48,"size":2867,"aid":"3",'
            '"created":1392650524,"pid":"7","src_small":"http://content-10.foto.my.mail.ru/mail/flid'
            'ster/3/p-7.jpg","title":"dfdf"}'
        )
        self._process_single_test(
            'photo_post_commit',
            None,
            args=(upload_response,),
            expected_dict={u'pid': u'7'},
        )


class MailRuO2TestCase(TestCase):
    def setUp(self):
        super(MailRuO2TestCase, self).setUp()
        self._proxy = mail_ru_test.FakeProxy().start()

        LazyLoader.register('slave_db_engine', lambda: self._fake_db.get_engine())

        passport.backend.social.proxylib.init()

        mail_ru_o2_app = providers.get_application_by_name(MAIL_RU_APPLICATION_NAME2)
        self._p = get_proxy(
            MailRu.code,
            {'value': APPLICATION_TOKEN1},
            mail_ru_o2_app,
        )

    def tearDown(self):
        LazyLoader.flush()
        self._proxy.stop()
        super(MailRuO2TestCase, self).tearDown()


class TestMailRuO2Fails(MailRuO2TestCase):
    def test_tnt_error(self):
        # Недокументированный отказ, будем считать за временный, пока не
        # доказано обратного.
        self._proxy.set_response_value(
            'get_profile',
            mail_ru_test.MailRuO2Api.build_error(
                error='tnt error',
                error_code=5,
                error_description='tnt request failed',
                http_status_code=500,
            ),
        )

        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            self._p.get_profile()


class TestDeepMailRuO2Fails(TestCase):
    def setUp(self):
        super(TestDeepMailRuO2Fails, self).setUp()

        self._fake_useragent = FakeUseragent().start()

        LazyLoader.register('slave_db_engine', self._fake_db.get_engine)
        LazyLoader.register('http_pool_manager', build_http_pool_manager)

        passport.backend.social.proxylib.init()

        mail_ru_o2_app = providers.get_application_by_name(MAIL_RU_APPLICATION_NAME2)
        self._p = get_proxy(
            MailRu.code,
            {'value': APPLICATION_TOKEN1},
            mail_ru_o2_app,
        )

    def tearDown(self):
        self._fake_useragent.stop()
        LazyLoader.flush()
        super(TestDeepMailRuO2Fails, self).tearDown()

    def test_refresh_token_not_found(self):
        self._fake_useragent.set_response_value(
            mail_ru_test.MailRuO2Api.build_error(
                error='token not found',
                error_code=6,
                error_description='token not found',
                http_status_code=200,
            ),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.refresh_token(REFRESH_TOKEN1)


class TestMailRuO2NoUserid(MailRuO2TestCase):
    def test(self):
        self._proxy.set_response_value(
            'get_profile',
            mail_ru_test.MailRuO2Api.get_profile(exclude_attrs={'id'}),
        )

        userinfo = self._p.get_profile()

        self.assertNotIn('userid', userinfo)
