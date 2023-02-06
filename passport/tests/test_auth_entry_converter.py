# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.authtypes import authtypes
from passport.backend.core.historydb.converter import AuthEntryConverter
from passport.backend.core.historydb.entry import AuthEntry
from passport.backend.core.historydb.statuses import (
    SESSION_CREATE,
    SESSION_UPDATE,
)
import six

from .base import TestEntryCase


class TestAuthEntryConverter(TestEntryCase):
    def setUp(self):
        self.converter_cls = AuthEntryConverter
        entry_cls = AuthEntry
        self.fields = dict(
            host_id=0x7F,
            client_name='fake',
            type=authtypes.AUTH_TYPE_WEB,
            status=SESSION_CREATE,
        )
        super(TestAuthEntryConverter, self).setUp(self.converter_cls, entry_cls, self.fields)

    def test_flag(self):
        self.fields['status'] = SESSION_UPDATE
        entry = AuthEntry(**self.fields)
        log_msg = self.converter.convert(entry)
        status = self.get_new_field_from_log('status', self.converter_cls, log_msg)
        eq_(status, str(SESSION_UPDATE))

    def test_convert(self):
        entry = AuthEntry(
            host_id=0x7F,
            client_name='passport',
            uid=11808007,
            user_ip='77.88.3.85',
            yandexuid='1602732171323096171',
            type=authtypes.AUTH_TYPE_WEB,
            status=SESSION_CREATE,
            login='test-phones',
            comment='ssl=1;aid=1323180826908:1297613653:127;ttl=0',
            useragent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0) Gecko/20100101 Firefox/4.0',
            retpath='http://passportdev-7.yandex.ru/passport?mode=passport',
        )

        actual_log_msg = self.converter.convert(entry)
        expected_msg = '''1 %s 7F passport 11808007 test-phones - web ses_create ssl=1;aid=1323180826908:1297613653:127;ttl=0 77.88.3.85 - 1602732171323096171 - %s `%s`''' % (
            entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03'),
            entry.retpath,
            entry.useragent,
        )
        eq_(actual_log_msg, expected_msg)
        eq_(str(entry), expected_msg)
        if six.PY2:
            eq_(six.text_type(entry), expected_msg.decode('utf-8'))

    def test_convert_with_comment(self):
        entry = AuthEntry(
            host_id=0x7F,
            client_name='passport',
            uid=11808007,
            user_ip='77.88.3.85',
            yandexuid='1602732171323096171',
            type=authtypes.AUTH_TYPE_WEB,
            status=SESSION_CREATE,
            login='test-phones',
            comment={'ssl': 1, 'ttl': 0},
            useragent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0) Gecko/20100101 Firefox/4.0',
            retpath='http://passportdev-7.yandex.ru/passport?mode=passport',
        )

        actual_log_msg = self.converter.convert(entry)
        expected_msg = '''1 %s 7F passport 11808007 test-phones - web ses_create ssl=1;ttl=0 77.88.3.85 - 1602732171323096171 - %s `%s`''' % (
            entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03'),
            entry.retpath,
            entry.useragent,
        )
        eq_(actual_log_msg, expected_msg)
        eq_(str(entry), expected_msg)
        if six.PY2:
            eq_(six.text_type(entry), expected_msg.decode('utf-8'))
