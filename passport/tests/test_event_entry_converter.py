# -*- coding: utf-8 -*-

import mock
from nose.tools import eq_
from passport.backend.core.historydb.converter import EventEntryConverter
from passport.backend.core.historydb.entry import EventEntry
from passport.backend.core.test.test_utils import with_settings_hosts
import six

from .base import TestEntryCase


class TestEventEntryConverter(TestEntryCase):
    def setUp(self):
        self.converter = EventEntryConverter()

    def test_convert_1(self):
        entry = EventEntry(
            host_id=0x7f,
            client_name='passport',
            uid=11807491,
            name='sid.rm',
            value='800',
            user_ip='1.2.3.4',
            admin='spleenjack',
            comment=u'удаление старых аккаунтов',
        )

        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = u'1 %s 7F passport 11807491 sid.rm 800 1.2.3.4 - - spleenjack `удаление старых аккаунтов`' % time
        if six.PY2:
            expected_log_msg = expected_log_msg.encode('utf8')
        eq_(actual_log_msg, expected_log_msg)

    def test_convert_2(self):
        entry = EventEntry(
            host_id=0x7F,
            client_name='passport',
            uid=11808003,
            name='restore.key_generated',
            value='Tue Nov 29 18:46:22 2011',
            user_ip='77.88.4.81',
            yandexuid='2581518951322569317',
        )

        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = u'1 %s 7F passport 11808003 restore.key_generated `Tue Nov 29 18:46:22 2011` 77.88.4.81 - 2581518951322569317 - -' % time
        eq_(actual_log_msg, expected_log_msg)
        eq_(str(entry), expected_log_msg)
        if six.PY2:
            eq_(six.text_type(entry), expected_log_msg.decode('utf-8'))

    def test_convert_with_bad_yandexuid(self):
        entry = EventEntry(
            host_id=0x7F,
            client_name='passport',
            uid=11808003,
            name='restore.key_generated',
            value='Tue Nov 29 18:46:22 2011',
            user_ip='77.88.4.81',
            yandexuid='4551834931456481973, yandex_gid=213, yp=1459073973.ygu.1, yp=, yp=',
        )

        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = u'1 %s 7F passport 11808003 restore.key_generated `Tue Nov 29 18:46:22 2011` 77.88.4.81 - `4551834931456481973, yandex_gid=213, yp=1459073973.ygu.1, yp=, yp=` - -' % time
        eq_(actual_log_msg, expected_log_msg)
        eq_(str(entry), expected_log_msg)
        if six.PY2:
            eq_(six.text_type(entry), expected_log_msg.decode('utf-8'))


@with_settings_hosts(HISTORYDB_LOG_ENCRYPTION_ENABLED=True)
class TestEncryptedEventEntryConverter(TestEntryCase):
    def setUp(self):
        self.converter = EventEntryConverter()

    def test_convert_simple(self):
        entry = EventEntry(
            host_id=0x7f,
            client_name='passport',
            uid=11807491,
            name='sid.rm',
            value='800',
            user_ip='1.2.3.4',
            admin='spleenjack',
            comment=u'удаление старых аккаунтов',
        )

        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = u'2 %s 7F passport 11807491 sid.rm 800 1.2.3.4 - - spleenjack `удаление старых аккаунтов`' % time
        if six.PY2:
            expected_log_msg = expected_log_msg.encode('utf8')
        eq_(actual_log_msg, expected_log_msg)

    def test_convert_encrypted(self):
        entry = EventEntry(
            host_id=0x7f,
            client_name='passport',
            uid=11807491,
            name='info.password',
            value='new password',
            user_ip='1.2.3.4',
        )

        with mock.patch(
            'passport.backend.core.historydb.converter.encrypt_value',
            lambda value: 'encrypted-value',
        ):
            actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = u'2 %s 7F passport 11807491 info.password encrypted-value 1.2.3.4 - - - -' % time
        eq_(actual_log_msg, expected_log_msg)
