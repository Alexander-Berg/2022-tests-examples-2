# -*- coding: utf-8 -*-
import ujson

from django.test import TestCase, RequestFactory

from passport_grants_configurator.apps.core.exceptions import (
    NetworkResolveError,
    NoDataError,
)
from passport_grants_configurator.apps.core.test.utils import (
    MockRequests,
    MockRedis,
)
from passport_grants_configurator.apps.core.views import network_suggest

TEST_MACRO_LIST = [
    '_1CAPPSRV_',
    '_1CDEVSRV_',
    '_1CDEV_',
    '_1CEXTNETS_',
    '_1CEXTSRV_',
    '_1CKEYSRVPASSP_',
    '_PASSPORTDEVNETS_',
    '_PASSPORTCORPNETS_',
]

TEST_CONDUCTOR_GROUPS_LIST = [
    '%500-testing',
    '%dev-passport',
    '%adfox-myt',
    '%passport-grantushka-stable',
]

TEST_ANOTHER_MACRO_LIST = [
    '_PASSPORT_',
    '_KOPALKA_',
]

TEST_CONDUCTOR_GROUPS_LIST_FROM_API = [
    {
        'name': '500px-testing',
        'description': '500px testing for yaskevich@',
        'created_at': '2013-12-30T15:25:06+04:00',
        'export_to_racktables': True,
    },
    {
        'name': 'dev-passport',
        'description': 'GPU для пилота Accenture по анализу изображений',
        'created_at': '2014-04-29T17:56:24+04:00',
        'export_to_racktables': True,
    },
    {
        'name': 'adfox-dev-myt',
        'description': "",
        'created_at': '2015-08-11T15:14:17+03:00',
        'export_to_racktables': True,
    },
    {
        'name': 'passport-grantushka-stable',
        'description': "",
        'created_at': '2015-08-11T15:14:17+03:00',
        'export_to_racktables': True,
    },
]


class NetworkSuggestTestCase(TestCase):

    def setUp(self):
        self.requests = MockRequests()
        self.requests.start()
        self.factory = RequestFactory()
        self.redis = MockRedis()
        self.redis.start()

    def tearDown(self):
        self.redis.stop()
        self.requests.stop()

    def make_request(self, data):
        request = self.factory.get('/grants/network/suggest/', data=data)
        return network_suggest(request)

    def expected(self, suggestions):
        return {
            'success': True,
            'suggestions': suggestions,
        }

    def test_found_in_cache(self):
        self.redis.mock.get.side_effect = [
            ujson.dumps(TEST_MACRO_LIST),
            ujson.dumps(TEST_CONDUCTOR_GROUPS_LIST),
        ]

        response = self.make_request({'keyword': u'Passp'})

        self.assertEqual(
            ujson.loads(response.content),
            self.expected([
                '_PASSPORTDEVNETS_',
                '_PASSPORTCORPNETS_',
                '_1CKEYSRVPASSP_',
                '%passport-grantushka-stable',
                '%dev-passport',
            ]),
        )
        self.assertEqual(self.redis.mock.get.call_count, 2)

    def test_from_request(self):
        """При пустом кэше кондукторных групп, обращаемся к АПИ"""
        self.redis.mock.get.side_effect = [ujson.dumps(TEST_MACRO_LIST), None]
        self.requests.response.text = ujson.dumps(TEST_CONDUCTOR_GROUPS_LIST_FROM_API)

        response = self.make_request(data={'keyword': u'Passp'})
        self.assertEqual(
            ujson.loads(response.content),
            self.expected([
                '_PASSPORTDEVNETS_',
                '_PASSPORTCORPNETS_',
                '_1CKEYSRVPASSP_',
                '%passport-grantushka-stable',
                '%dev-passport',
            ]),
        )
        self.assertEqual(self.redis.mock.get.call_count, 2)
        self.assertEqual(self.requests.mock_get.call_count, 1)

    def test_get_conductor_groups_with_empty_cache_and_trash(self):
        """При пустом кэше кондукторных групп, обращаемся к АПИ и получаем невалидный JSON"""
        self.redis.mock.get.side_effect = [ujson.dumps(TEST_MACRO_LIST), None]
        self.requests.response.text = 'not json at all'

        with self.assertRaises(NoDataError):
            self.make_request(data={'keyword': u'Passp'})

    def test_not_found_at_all(self):
        self.redis.mock.get.side_effect = [None, None]
        self.requests.raise_for_status.side_effect = NetworkResolveError()

        response = self.make_request({'keyword': u'empty'})
        self.assertEqual(ujson.loads(response.content), self.expected([]))

    def test_get_macros_only(self):
        self.redis.mock.get.side_effect = [
            ujson.dumps(TEST_MACRO_LIST),
        ]

        response = self.make_request({'keyword': u'_Passp'})

        self.assertEqual(
            ujson.loads(response.content),
            self.expected([
                '_PASSPORTDEVNETS_',
                '_PASSPORTCORPNETS_',
                '_1CKEYSRVPASSP_',
            ]),
        )
        self.assertEqual(self.redis.mock.get.call_count, 1)

    def test_c_groups_only(self):
        self.redis.mock.get.side_effect = [
            ujson.dumps(TEST_CONDUCTOR_GROUPS_LIST),
        ]

        response = self.make_request({'keyword': u'%Passp'})

        self.assertEqual(
            ujson.loads(response.content),
            self.expected([
                '%passport-grantushka-stable',
                '%dev-passport',
            ]),
        )
        self.assertEqual(self.redis.mock.get.call_count, 1)
