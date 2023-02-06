# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose.tools import eq_
from passport.backend.social.common.exception import ProviderCommunicationProxylibError
from passport.backend.social.proxylib import get_proxy

from . import TestProxy


class TestProxyOdnoklassniki(TestProxy):
    provider_code = 'ok'
    error_profile_response = '{"error_code":102,"error_data":null,"error_msg":"PARAM_SESSION_EXPIRED : Session expired"}'

    def test_profile_1(self):
        decoded_data = (
            '{"uid":"143645560158","birthday":"1987-05-02","age":26,"first_name":"Name","last_name":"LName",'
            '"name":"Name Uname","locale":"ru","gender":"male","has_email":true,'
            '"location":{"country":"RUSSIAN_FEDERATION","city":"Москва"},"online":"web",'
            '"pic_1":"http://i513.mycdn.me/res/vvvv_50x50.gif",'
            '"pic_2":"http://usd1.mycdn.me/res/stub_128x96.gif"}'
        )

        expected_dict = {
            u'firstname': u'Name',
            u'locale': u'ru',
            u'lastname': u'LName',
            u'userid': '143645560158',
            u'birthday': u'1987-05-02',
            u'avatar': {u'50x50': u'http://i513.mycdn.me/res/vvvv_50x50.gif'},
            u'gender': u'm',
            u'nickname': u'Name Uname',
            u'location': {
                u'country': u'RUSSIAN_FEDERATION',
                u'city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
            },
        }
        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_profile_2(self):
        decoded_data = (
            '[{"uid":"143645560158","birthday":"05-02","first_name":"Petr","last_name":"Teston",'
            '"name":"Petr Teston","locale":"ru","gender":"female","location":{"countryCode":"RU","country":'
            '"RUSSIAN_FEDERATION","city":"Москва"},"pic_1":"http://i508.mycdn.me/res/stub_50x50.gif","pic_2":'
            '"http://usd1.mycdn.me/res/vvvv_128x96.gif","pic_3":"http://i508.mycdn.me/res/stub_128x96.gif",'
            '"pic_4":"http://uld5.mycdn.me/res/stub_128x96.gif"}]'
        )
        expected_dict = {
            u'firstname': u'Petr',
            u'locale': u'ru',
            u'lastname': u'Teston',
            u'userid': '143645560158',
            u'birthday': u'0000-05-02',
            u'avatar': {u'50x0': u'http://usd1.mycdn.me/res/vvvv_128x96.gif'},
            u'gender': u'f',
            u'nickname': u'Petr Teston',
            u'location': {
                u'country': u'RUSSIAN_FEDERATION',
                u'countryCode': u'RU',
                u'city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
            },
        }

        self._process_single_test(
            'get_profile',
            decoded_data,
            kwargs={'userid': '143645560158'},
            expected_dict=expected_dict,
        )

    def test_profile_error(self):
        self._tst_profile_error()

    decoded_data = (
        '[{"uid":"143645560158","type":"activities","number":0,"lastId":0,"message":0,"icon":0},'
        '{"uid":"143645560158","type":"marks","number":1,"lastId":1268894287998,"message":1,"icon":1},'
        '{"uid":"143645560158","type":"guests","number":1,"lastId":1382093088174,"message":1,"icon":1},'
        '{"uid":"143645560158","type":"messages","number":3,"lastId":0,"message":0,"icon":0},'
        '{"uid":"143645560158","type":"notifications","number":2,"lastId":0,"message":0,"icon":0},'
        '{"uid":"143645560158","type":"discussions","number":0,"lastId":0,"message":0,"icon":0,'
        '"likes_count":0,"replies_count":0},'
        '{"uid":"143645560158","type":"app_events","number":0,"lastId":0,"message":0,"icon":0}]'
    )

    def test_get_marks_unread_count(self):
        self._process_single_test(
            'get_marks_unread_count',
            self.decoded_data,
            expected_value=1,
        )

    def test_get_notifications_unread_count(self):
        self._process_single_test(
            'get_notifications_unread_count',
            self.decoded_data,
            expected_value=2,
        )

    def test_get_messages_unread_count(self):
        self._process_single_test(
            'get_messages_unread_count',
            self.decoded_data,
            expected_value=3,
        )

    def test_get_friends(self):
        decoded_data = [
            '["1375719376","1915735973"]',
            (
                '[{"uid":"1375719376","birthday":"1989-11-14","first_name":"Name1","last_name":"LastName1",'
                '"name":"Name Last","locale":"ru","gender":"female","location":{"countryCode":"RU","country":'
                '"RUSSIAN_FEDERATION","city":"Жердевка"},"pic_1":"http://i500.mycdn.me/getImage?photoId=4327to'
                'Type=4&viewToken=0yQHsA","pic_2":"http://usd1.mycdn.me/getImage?photoId=43275Type=2&viewToken='
                '0yQPUfHsA","pic_3":"http://i500.mycdn.me/getImage?photoId=432otoType=5&viewToken=0yQPUs-U4fHsA",'
                '"pic_4":"http://uld7.mycdn.me/getImage?photoId=432083&photoType=0&viewToken=0yQPUsHsA"},'
                '{"uid":"1915735973","birthday":"04-18","first_name":"Name2","last_name":"LastName2","name":'
                '"Name Last2","locale":"ru","gender":"male","location":{"countryCode":"RU","country":'
                '"RUSSIAN_FEDERATION","city":"Жердевка"},"pic_1":"http://i508.mycdn.me/getImage?photoId='
                '54175506&photoType=4&viewToken=7I-OmYfE5GwQ","pic_2":"http://usd1.mycdn.me/getImage?photoId='
                '557&photoType=2&viewToken=7I-OmCGwQ","pic_3":"http://i508.mycdn.me/getImage?photoId=5417&'
                'photoType=5&viewToken=7I-OmCGnqGwQ","pic_4":"http://uld13.mycdn.me/getImage?photoId=541757&'
                'photoType=0&viewToken=7I-OmCGnqBwQ"}]'
            ),
        ]
        expected_list = [
            {
                u'firstname': u'Name1',
                u'locale': u'ru',
                u'lastname': u'LastName1',
                u'userid': '1375719376',
                u'birthday': u'1989-11-14',
                u'avatar': {
                    u'190x190': u'http://i500.mycdn.me/getImage?photoId=432otoType=5&viewToken=0yQPUs-U4fHsA',
                    u'50x50': u'http://i500.mycdn.me/getImage?photoId=4327toType=4&viewToken=0yQHsA',
                    u'50x0': u'http://usd1.mycdn.me/getImage?photoId=43275Type=2&viewToken=0yQPUfHsA',
                    u'640x0': u'http://uld7.mycdn.me/getImage?photoId=432083&photoType=0&viewToken=0yQPUsHsA',
                },
                u'gender': u'f',
                u'nickname': u'Name Last',
                u'location': {
                    u'country': u'RUSSIAN_FEDERATION',
                    u'countryCode': u'RU',
                    u'city':
                    u'\u0416\u0435\u0440\u0434\u0435\u0432\u043a\u0430',
                },
            },
            {
                u'firstname': u'Name2',
                u'locale': u'ru',
                u'lastname': u'LastName2',
                u'userid': '1915735973',
                u'birthday': u'0000-04-18',
                u'avatar': {
                    u'190x190': u'http://i508.mycdn.me/getImage?photoId=5417&photoType=5&viewToken=7I-OmCGnqGwQ',
                    u'50x50': u'http://i508.mycdn.me/getImage?photoId=54175506&photoType=4&viewToken=7I-OmYfE5GwQ',
                    u'50x0': u'http://usd1.mycdn.me/getImage?photoId=557&photoType=2&viewToken=7I-OmCGwQ',
                    u'640x0': u'http://uld13.mycdn.me/getImage?photoId=541757&photoType=0&viewToken=7I-OmCGnqBwQ',
                },
                u'gender': u'm',
                u'nickname': u'Name Last2',
                u'location': {
                    u'country': u'RUSSIAN_FEDERATION',
                    u'countryCode': u'RU',
                    u'city': u'\u0416\u0435\u0440\u0434\u0435\u0432\u043a\u0430',
                },
            },
        ]
        self._process_single_test(
            'get_friends',
            decoded_data,
            expected_list=expected_list,
        )

    def test_get_profile_links(self):
        proxy = get_proxy(self.provider_code)
        links = proxy.get_profile_links('12345', 'some_user')
        eq_(links, [u'http://odnoklassniki.ru/profile/12345'])

    def test_get_photo_albums(self):
        decoded_data = [
            (
                '{"hasMore":true,"pagingAnchor":"LTEzOTI0NTcxOTIzNTc6LTEzOTA3NzQ2MjY4NTU=","albums":[{"aid":"542'
                '075281758","title":"album1","created":"2014-01-17","photos_count":3,"type":"PUBLIC"}]}'
            ),
            (
                '{"hasMore":false,"pagingAnchor":"LTEzOTI0NTcxOTIzNTc6LTEzOTA3NzQ2MjY4NTU=","albums":[{"aid":"542'
                '075386206","title":"album2","created":"2014-01-17","photos_count":1,"type":"PUBLIC"}]}'
            ),
        ]

        expected_list = [
            {u'aid': u'542075281758', u'photo_count': 3, u'title': u'album1', u'visibility': u'public',
             u'created': 1389916800},
            {u'aid': u'542075386206', u'photo_count': 1, u'title': u'album2', u'visibility': u'public',
             u'created': 1389916800},
        ]
        self._process_single_test(
            'get_photo_albums',
            decoded_data,
            expected_list=expected_list,
        )

    def test_get_photo_albums_empty_response(self):
        decoded_data = '{"albums":[]}'
        expected_list = []
        self._process_single_test(
            'get_photo_albums',
            decoded_data,
            expected_list=expected_list,
        )

    def test_create_photo_album(self):
        decoded_data = "10203145153019471"

        self._process_single_test(
            'create_photo_album',
            decoded_data,
            kwargs={'title': 'title', 'description': 'desc', 'privacy': 'public'},
            expected_dict={'aid': '10203145153019471'},
        )

    def test_get_photos(self):
        decoded_data = [
            ('{"hasMore":true,"anchor":"LTE4OTI2Mzc2ODI6LTE4OTI2Mzc2ODI=","photos":[{"id":"542075334238","standard_w'
             'idth":603,"standard_height":286,"pic50x50":"url1","pic128x128":"url2","pic190x190":"url3","pic640x480":'
             '"url4","pic1024x768":"url5","text":""}]}'),
            ('{"hasMore":false,"anchor":"LTE4OTI2Mzc2MjY6LTE4OTI2Mzc2MjY=","photos":[{"id":"542075333982","standard_'
             'width":610,"standard_height":286,"pic50x50":"url1","pic128x128":"url2","pic190x190":"url3","pic640x480"'
             ':"url4","pic1024x768":"url5","text":""}]}'),
        ]

        expected_list = [
            {
                u'caption': u'',
                u'pid': u'542075334238',
                u'images': [
                    {'url': u'url1', 'width': 50, 'height': 50},
                    {'url': u'url2', 'width': 128, 'height': 128},
                    {'url': u'url3', 'width': 190, 'height': 190},
                    {'url': u'url5', 'width': 603, 'height': 286},
                    {'url': u'url4', 'width': 603, 'height': 286},
                ],
            },
            {
                u'caption': u'',
                u'pid': u'542075333982',
                u'images': [
                    {'url': u'url1', 'width': 50, 'height': 50},
                    {'url': u'url2', 'width': 128, 'height': 128},
                    {'url': u'url3', 'width': 190, 'height': 190},
                    {'url': u'url5', 'width': 610, 'height': 286},
                    {'url': u'url4', 'width': 610, 'height': 286},
                ],
            },
        ]
        expected_dict = {
            'result': expected_list,
            'next_token': None,
        }
        self._process_single_test(
            'get_photos',
            decoded_data,
            kwargs={'aid': 'aid'},
            expected_dict=expected_dict,
        )

    def test_photo_post_get_request(self):
        decoded_data = (
            '{"photo_ids":["/y5MDWBStoj4ArwBaoh4cwDqu5TJlhS+nDPpp27rHLIfKlfJm5lbSg=="],"upload_url":"ht'
            'tp://up.odnoklassniki.ru/uploadImage?apiToken=9uJPISOOovEPvDnmOKH0Xf6YEIAuUyQqOjUlRGq6jSs3zMxi'
            'XaOFhSaSc2z%2F1RWCimVxZvl%2BanBTFlSEc212LNRBPJpJ3Elt&photoIds=%2Fy5MDWBStoj4ArwBaoh4cwDqu5TJlh'
            'S%2BnDPpp27rHLIfKlfJm5lbSg%3D%3D","expires":"2014.02.18 12:19"}'
        )

        expected_dict = {
            u'url': u'http://up.odnoklassniki.ru/uploadImage?apiToken=9uJPISOOovEPvDnmOKH0Xf6YEIAuUyQqOjUlRGq6jSs3z'
                    u'MxiXaOFhSaSc2z%2F1RWCimVxZvl%2BanBTFlSEc212LNRBPJpJ3Elt&photoIds=%2Fy5MDWBStoj4ArwBaoh4cwDqu5'
                    u'TJlhS%2BnDPpp27rHLIfKlfJm5lbSg%3D%3D',
            u'image_name': u'pic1',
        }
        self._process_single_test(
            'photo_post_get_request',
            decoded_data,
            args=('aid',),
            expected_dict=expected_dict,
        )

    def test_photo_post_commit(self):
        upload_response = ('{"photos":{"niPIyC1EKErNWRYBmEGd5pftqBh76FaZeCR5NgLeKWFbynQbjCnwgA\u003d\u003d":{"toke'
                           'n":"NSN6S0qF9+OtSt9WaQhpH2T7Rb+DZvBIfodf31cfaUC/IMf6ylwzNKOQJrezneIfL3L6R0fyJ/0rLIb/zFm'
                           '7lAcQgHVUxQNamjFmuW0dam38svLe0R4mcplgjX3NrWK0oDAxsRhsb6dTXcqdZ+YGfA\u003d\u003d"}}}')
        decoded_data = (
            '{"photos":[{"photo_id":"eqvWJiwSf9X3ZftST2J+gmNzkFuVFl5SllSWj/QcV8NnmtKPCMRo7g==","status":"'
            'SUCCESS","assigned_photo_id":"547890607710"}],"aid":"542075281758"}'
        )

        self._process_single_test(
            'photo_post_commit',
            decoded_data,
            kwargs={'upload_response': upload_response, 'caption': 'caption'},
            expected_dict={u'pid': u'547890607710'},
        )

    def test_photo_post_commit_failed(self):
        upload_response = ('{"photos":{"niPIyC1EKErNWRYBmEGd5pftqBh76FaZeCR5NgLeKWFbynQbjCnwgA\u003d\u003d":{"toke'
                           'n":"NSN6S0qF9+OtSt9WaQhpH2T7Rb+DZvBIfodf31cfaUC/IMf6ylwzNKOQJrezneIfL3L6R0fyJ/0rLIb/zFm'
                           '7lAcQgHVUxQNamjFmuW0dam38svLe0R4mcplgjX3NrWK0oDAxsRhsb6dTXcqdZ+YGfA\u003d\u003d"}}}')
        decoded_data = (
            '{"photos":[{"photo_id":"eqvWJiwSf9X3ZftST2J+gmNzkFuVFl5SllSWj/QcV8NnmtKPCMRo7g==","status":"'
            'FAILED","assigned_photo_id":"547890607710"}],"aid":"542075281758"}'
        )

        self._process_single_test(
            'photo_post_commit',
            decoded_data,
            kwargs={'upload_response': upload_response, 'caption': 'caption'},
            expected_exception=ProviderCommunicationProxylibError,
        )

    def test_wall_post(self):
        decoded_data = '"63784035699550"'

        self._process_single_test(
            'wall_post',
            decoded_data,
            kwargs={'link': 'http://yandex.ru'},
            expected_dict={'post_id': '63784035699550'},
        )
