# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

from passport.backend.social.common import (
    exception as exceptions,
    oauth2,
)
from passport.backend.social.common.application import Application
from passport.backend.social.common.providers.Esia import Esia
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN4,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
    SIMPLE_USERID1,
    TASK_ID1,
    UNIXTIME1,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.useragent import Url
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.EsiaProxy import (
    EsiaRefreshToken,
    EsiaToken,
)
from passport.backend.social.proxylib.test import esia as esia_test
from passport.backend.utils.gost.jwt import install_gost_to_jws


class EsiaTestCase(TestCase):
    def setUp(self):
        super(EsiaTestCase, self).setUp()
        install_gost_to_jws()
        self._proxy = esia_test.FakeProxy().start()
        passport.backend.social.proxylib.init()
        self._p = self.build_proxy()

    def tearDown(self):
        self._proxy.stop()
        super(EsiaTestCase, self).tearDown()

    def build_settings(self):
        settings = super(EsiaTestCase, self).build_settings()
        settings['providers'] = [
            {
                'id': Esia.id,
                'code': Esia.code,
                'name': 'esia',
            },
        ]
        settings['social_config'].update(
            esia_host='esia-portal1.test.gosuslugi.ru',
            esia_real_host='esia-portal1.test.gosuslugi.ru',
            esia_token_url='https://esia-portal1.test.gosuslugi.ru/aas/oauth2/te',
            esia_yandex_certificate=esia_test.ESIA_YANDEX_CERTIFICATE,
            esia_yandex_private_key=esia_test.ESIA_YANDEX_PRIVATE_KEY,
            esia_yandex_private_key_password=None,
        )
        return settings

    @staticmethod
    def build_id_token():
        return esia_test.EsiaApi.build_id_token(dict(sub=int(SIMPLE_USERID1)))

    @staticmethod
    def build_proxy(scope='openid'):
        return get_proxy(
            Esia.code,
            dict(
                value=EsiaToken(
                    access_token=APPLICATION_TOKEN1,
                    id_token=EsiaTestCase.build_id_token(),
                    scope=scope,
                    version=1,
                ).serialize(),
            ),
            Application(
                domain='social.yandex.net',
                id=EXTERNAL_APPLICATION_ID1,
                request_from_intranet_allowed=True,
            ),
        )


class TestGetProfile(EsiaTestCase):
    def test_openid_scope(self):
        rv = self._p.get_profile()

        self.assertEqual(
            rv,
            {
                'userid': str(int(SIMPLE_USERID1)),
            }
        )

        assert len(self._proxy.requests) == 0

    def test_god_scope(self):
        self._proxy.set_response_value(
            'get_profile',
            FakeResponse(
                json.dumps({
                    'birthDate': '18.07.1990',
                    'birthPlace': 'Москва',
                    'citizenship': 'RUS',
                    'firstName': 'ИМЯ006',
                    'inn': '864999540958',
                    'lastName': 'ФАМИЛИЯ006',
                    'middleName': 'ОТЧЕСТВО006',
                    'snils': '000-000-600 06',
                    'status': 'REGISTERED',
                    'trusted': True,
                    'contacts': {
                        'elements': [
                            {
                                'type': 'MBT',
                                'value': '+7(926)2464800',
                                'vrfStu': 'VERIFIED',
                            },
                            {
                                'type': 'EML',
                                'value': 'EsiaTest006@yandex.ru',
                                'vrfStu': 'VERIFIED',
                            },
                        ],
                    },
                    'documents': {
                        'elements': [
                            {
                                'issueDate': '12.03.2009',
                                'issuedBy': 'Отделом УФМС России по Московской области в Люблинском районе тестовый 2019',
                                'issueId': '131124',
                                'number': '222222',
                                'series': '1111',
                                'type': 'RF_PASSPORT',
                                'vrfStu': 'VERIFIED',
                            },
                        ],
                    },
                }),
                200,
            ),
        )
        god_scope = 'openid birthdate birthplace email fullname id_doc inn mobile snils'

        rv = self.build_proxy(scope=god_scope).get_profile()

        self.assertEqual(
            rv,
            {
                'birthday': '1990-07-18',
                'email': 'EsiaTest006@yandex.ru',
                'firstname': 'ИМЯ006',
                'is_verified': True,
                'lastname': 'ФАМИЛИЯ006',
                'middlename': 'ОТЧЕСТВО006',
                'phone': '+79262464800',
                'userid': str(int(SIMPLE_USERID1)),
            },
        )

        assert len(self._proxy.requests) == 1
        self.assertEqual(
            self._proxy.requests[0],
            dict(
                data=None,
                headers={
                    'Authorization': u'Bearer ' + APPLICATION_TOKEN1,
                    'accept': 'application/json; schema="https://esia-portal1.test.gosuslugi.ru/rs/model/prn/Person-3"',
                },
                url=str(Url(
                    'https://esia-portal1.test.gosuslugi.ru/rs/prns/' + str(int(SIMPLE_USERID1)),
                    params=dict(embed='(contacts.elements-1,documents.elements-1)'),
                )),
            ),
        )

    def test_invalid_token(self):
        self._proxy.set_response_value(
            'get_profile',
            FakeResponse(
                json.dumps(dict(
                    code='ESIA-005011',
                    message='SecurityErrorEnum.invalidToken',
                )),
                401,
            ),
        )

        with self.assertRaises(exceptions.InvalidTokenProxylibError):
            self.build_proxy(scope='openid bup').get_profile()


class TestRefreshToken(EsiaTestCase):
    def test(self):
        self.fake_chrono.set_timestamp(UNIXTIME1)

        self._proxy.set_response_value(
            'refresh_token',
            esia_test.EsiaApi.refresh_token(
                access_token=APPLICATION_TOKEN3,
                expires_in=APPLICATION_TOKEN_TTL1,
                refresh_token=APPLICATION_TOKEN4,
            ),
        )

        old_refresh_token = EsiaRefreshToken(
            id_token=self.build_id_token(),
            scope='openid',
            state=TASK_ID1,
            value=APPLICATION_TOKEN2,
            version=1,
        )

        rv = self._p.refresh_token(old_refresh_token.serialize())

        access_token = EsiaToken(
            access_token=APPLICATION_TOKEN3,
            id_token=old_refresh_token.id_token,
            scope=old_refresh_token.scope,
            version=1,
        )
        refresh_token = EsiaRefreshToken(
            id_token=old_refresh_token.id_token,
            scope=old_refresh_token.scope,
            state=old_refresh_token.state,
            value=APPLICATION_TOKEN4,
            version=1,
        )

        self.assertEqual(
            rv,
            dict(
                access_token=access_token.serialize(),
                expires_in=APPLICATION_TOKEN_TTL1,
                refresh_token=refresh_token.serialize(),
            ),
        )

        assert len(self._proxy.requests) == 1

        client_secret = self._proxy.requests[0].get('data', dict()).pop('client_secret', '')

        self.assertEqual(
            self._proxy.requests[0],
            dict(
                data=dict(
                    client_id=EXTERNAL_APPLICATION_ID1,
                    grant_type='refresh_token',
                    refresh_token=old_refresh_token.value,
                    scope=old_refresh_token.scope,
                    state=old_refresh_token.state,
                    timestamp=esia_test.EsiaApi.esia_datetime_format(datetime.datetime.fromtimestamp(UNIXTIME1)),
                ),
                headers=None,
                url='https://esia-portal1.test.gosuslugi.ru/aas/oauth2/te',
            ),
        )

        esia_test.EsiaApi.assert_ok_esia_signature(self._proxy.requests[0].get('data', dict()), client_secret)

    def test_invalid_refresh_token(self):
        self._proxy.set_response_value(
            'refresh_token',
            oauth2.test.build_error('invalid_grant'),
        )

        with self.assertRaises(exceptions.InvalidTokenProxylibError):
            self._p.refresh_token(
                EsiaRefreshToken(
                    id_token=self.build_id_token(),
                    scope='bup',
                    state=TASK_ID1,
                    value=APPLICATION_TOKEN2,
                    version=1,
                ).serialize(),
            )
