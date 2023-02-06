# -*- coding: utf-8 -*-

import sys
import warnings
sys.path.append(".")

import unittest
from morda.http import task

class TestHttpTask(unittest.TestCase):
    def test_new(self):
        Task = task.Task({
            'url': 'https://yandex.ru',
            'retry': 2,
            'timeout_ms': 60,
            'headers': {
                'Host': 'yandex.ru'
            }
        })

        assert Task.url == 'https://yandex.ru'
        assert Task.retry == 2
        assert Task.headers == {'Host': 'yandex.ru'}
        assert Task.timeout_ms == 60

        assert Task.result.content == None
        assert Task.result.status_code == None
        assert Task.result.headers == None


    def test_content(self):
        Task = task.Task({
            'url': 'https://yandex.ru',
        })

        Task.result.content = 'body'
        assert Task.result.content == 'body'

        Task.result.status_code = 200
        assert Task.result.status_code == 200

        Task.result.headers = {
                        'User-Agent': 'curl',
                        'Content-type': 'text/json'
        }
        assert Task.result.headers == {
                        'User-Agent': 'curl',
                        'Content-type': 'text/json'
        }

if __name__ == 'main':
    unittest.main()
