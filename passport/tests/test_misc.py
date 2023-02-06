# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from nose.tools import eq_
from passport.backend.social.broker.misc import generate_retpath


class TestMisc(unittest.TestCase):
    def test_generate_retpath_ok(self):
        result = generate_retpath(
            'http://social.yandex.ru?k1=v1#k2=v2',
            'query',
            'ok',
            task_id='12345',
        )
        eq_(result, 'http://social.yandex.ru?status=ok&k1=v1&task_id=12345#k2=v2')

        result = generate_retpath(
            'http://social.yandex.ru?k1=v1#k2=v2',
            'fragment',
            'error',
        )
        eq_(result, 'http://social.yandex.ru?k1=v1#status=error&k2=v2')
