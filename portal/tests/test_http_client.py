# -*- coding: utf-8 -*-

import sys
sys.path.append(".")
from morda.http import client

import unittest
import os

SKIP_REASON = 'FIXME: do NOT use real hosts for testing http clients, if you really want to run such tests please pass enviroment variable FULL_TEST_HTTP_CLIENT'
SKIP_TESTS = 'FULL_TEST_HTTP_CLIENT' not in os.environ


class TestHttpClient(unittest.TestCase):

    def test_add(self):
        Client = client.Client()
        req = {
            "url": 'http://yandex.ru',
            'timeout_ms': 100,
        }

        result = Client.add('', '')
        self.assertFalse(result)

        result = Client.add('myreq', req)
        self.assertTrue(result)

        result = Client.add('myreq', req)
        self.assertFalse(result)

    @unittest.skipIf(SKIP_TESTS, SKIP_REASON)
    def test_get(self):
        Client = client.Client()
        req = {
            "url": 'https://yandex.ru',
            'verbose': 0,
        }

        response = Client.get(req)
        assert len(response.content) > 0
        assert response.status_code == 200
        assert response.is_success() == True

    @unittest.skipIf(SKIP_TESTS, SKIP_REASON)
    def test_post(self):
        Client = client.Client()
        req = {
            'url': 'http://clop-2.wdevx.yandex.net/write/event/add',
            'headers': [
                'Host: events.portal.yandex.net',
                'content_type: application/json',
            ],
            'data': '{"name": "stocks", "geo": 2, "locale": "ru", "msg": "Курс доллара вырос"}',
            'verbose': 1,
        }

        response = Client.post(req)
        assert len(response.content) > 0
        assert response.status_code == 200
        assert response.is_success() == True

    @unittest.skipIf(SKIP_TESTS, SKIP_REASON)
    def test_unicode_post(self):
        Client = client.Client()
        req = {
            'url': 'http://clop-2.wdevx.yandex.net/write/event/add',
            'headers': [
                'Host: events.portal.yandex.net',
                'content_type: application/json',
            ],
            'data': u'{"name": "stocks", "geo": 2, "locale": "ru", "msg": "Курс доллара вырос"}',
            'verbose': 1,
        }

        response = Client.post(req)
        assert len(response.content) > 0
        assert response.status_code == 200
        assert response.is_success() == True

    @unittest.skip("FIXME: This test does nothing")
    def test_add_rcv(self):
        Client = client.Client()

        req = {"url": 'https://5.255.255.5'}
        result = Client.add('myreq0', req)

        for i in (range(1, 1)):
            req = {"url": 'https://yandex.ru', }
            result = Client.add('myreq' + str(i), req)

        Client.wait()

    @unittest.skipIf(SKIP_TESTS, SKIP_REASON)
    def test_failed(self):
        Client = client.Client()
        req = {
            "url": 'https://yandex.ru',
            'verbose': 0,
            'timeout_ms': 10,
            'retry': 2,
        }

        response = Client.get(req)
        assert response.is_success() == False
        assert response.status_code == 502

    @unittest.skipIf(SKIP_TESTS, SKIP_REASON)
    def test_zero_retry(self):
        Client = client . Client()
        req = {
            "url": 'https://yandex.ru:555',
            'verbose': 0,
            'timeout_ms': 300,
        }

        response = Client.get(req)
        assert response.status_code == 502
        assert response.is_success() == False

    def test_compression(self):
        client_object = client.Client()
        req = {
            "url": 'https://yandex.ru/',
            'verbose': 0,
            'use_gzip': True,
        }

        response = client_object.get(req)
        assert len(response.content) > 0
        assert response.status_code == 200
        assert response.is_success() == True

if __name__ == 'main':
    unittest.main()
