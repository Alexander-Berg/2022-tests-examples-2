# -*- coding: utf-8 -*-
import json

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.historydb.converter import AuthChallengeEntryConverter
from passport.backend.core.historydb.entry import AuthChallengeEntry
from passport.backend.core.historydb.exceptions import RequiredAttributeError
import six

from .base import TestEntryCase


class TestAuthChallengeEntryConverter(TestEntryCase):
    def setUp(self):
        self.converter = AuthChallengeEntryConverter()

    def test_convert(self):
        env = {
            'yandexuid': '123',
            'UserAgent': 'curl',
            'user_ip': '123',
        }

        entry = AuthChallengeEntry(
            'updated',
            123,
            '5972577a-8208-11e5-9f79-843a4bcee9c4',
            env,
            None,
        )
        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = u'1 %s updated 123 5972577a-8208-11e5-9f79-843a4bcee9c4 %s `%s` -' % (
            time,
            '-',
            json.dumps(env),
        )
        eq_(actual_log_msg, expected_log_msg)

    def test_convert_with_comment(self):
        entry = AuthChallengeEntry(
            'updated',
            123,
            '5972577a-8208-11e5-9f79-843a4bcee9c4',
            {},
            u'abc=какая-то дичь``\x00',
        )
        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = u'1 %s updated 123 5972577a-8208-11e5-9f79-843a4bcee9c4 - {} `abc=какая-то дичь````\x00`' % (
            time,
        )
        if six.PY2:
            expected_log_msg = expected_log_msg.encode('utf8')
        eq_(actual_log_msg, expected_log_msg)

    def test_convert_invalid_env(self):
        if six.PY3:
            return

        bad_ua = 'Mozilla/5.0 (Linux; U; Android 5.5; en-US; 9999+(\xa0:H) Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/10.8.0.718 U3/0.8.0 Mobile Safari/534.30'
        env = {
            'yandexuid': '123',
            'user_agent': bad_ua,
            'user_ip': '123',
        }

        entry = AuthChallengeEntry(
            'updated',
            123,
            '5972577a-8208-11e5-9f79-843a4bcee9c4',
            env,
            None,
        )
        with assert_raises(RequiredAttributeError):
            self.converter.convert(entry)
