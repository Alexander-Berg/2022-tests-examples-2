# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.logging_utils.request_id import (
    get_request_id,
    RequestIdManager,
)


class TestRequestIdManager(unittest.TestCase):
    def tearDown(self):
        if 'request_ids' in RequestIdManager.thread_data.__dict__:
            del RequestIdManager.thread_data.__dict__['cached_request_id']
            del RequestIdManager.thread_data.__dict__['request_ids']

    def test_nothing_pushed(self):
        eq_(get_request_id(), '')

    def test_push_request_id(self):
        RequestIdManager.push_request_id(1)
        eq_(get_request_id(), '@1')

        RequestIdManager.push_request_id(2)
        eq_(get_request_id(), '@1,2')

    def test_multiple_push_request_id(self):
        RequestIdManager.push_request_id(1, 2, 3)
        eq_(get_request_id(), '@1,2,3')

        RequestIdManager.push_request_id(4, 5, None)
        eq_(get_request_id(), '@1,2,3,4,5,None')

    def test_pop_request_id(self):
        RequestIdManager.push_request_id(1, 2)
        RequestIdManager.pop_request_id()

        eq_(get_request_id(), '@1')

        RequestIdManager.pop_request_id()
        RequestIdManager.pop_request_id()

        eq_(get_request_id(), '')

    def test_clear_request_id(self):
        RequestIdManager.push_request_id(1, 2)
        RequestIdManager.clear_request_id()

        eq_(get_request_id(), '')

        RequestIdManager.push_request_id(1, 2)
        eq_(get_request_id(), '@1,2')

    def test_push_request_id_with_unicode(self):
        RequestIdManager.push_request_id(1, u'fdп')
        eq_(get_request_id(), u'@1,fd\u043f')
