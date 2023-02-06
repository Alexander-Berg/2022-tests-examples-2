# -*- coding: utf-8 -*-

import mock
from nose.tools import eq_
from passport.backend.core.historydb.converter import RestoreEntryConverter
from passport.backend.core.historydb.entry import RestoreEntry
from passport.backend.core.test.test_utils import with_settings_hosts

from .base import TestEntryCase


class TestRestoreEntryConverter(TestEntryCase):
    def setUp(self):
        self.converter = RestoreEntryConverter()

    def test_convert_1(self):
        entry = RestoreEntry(
            'restore',
            1,
            '7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f',
            {'a': 'b'},
        )
        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = '1 restore %s 1 7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f `{"a": "b"}`' % time
        eq_(actual_log_msg, expected_log_msg)


@with_settings_hosts(HISTORYDB_LOG_ENCRYPTION_ENABLED=True)
class TestEncryptedRestoreEntryConverter(TestEntryCase):
    def setUp(self):
        self.converter = RestoreEntryConverter()

    def test_convert_ok(self):
        entry = RestoreEntry(
            'restore',
            1,
            '7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f',
            {'a': 'b'},
        )
        with mock.patch(
            'passport.backend.core.historydb.converter.encrypt_value',
            lambda value: 'encrypted-value',
        ):
            actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = '2 restore %s 1 7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f encrypted-value' % time
        eq_(actual_log_msg, expected_log_msg)

    def test_convert_none_value(self):
        entry = RestoreEntry(
            'restore',
            1,
            '7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f',
            None,
        )

        actual_log_msg = self.converter.convert(entry)
        time = entry.time.strftime('%Y-%m-%dT%H:%M:%S.%f+03')
        expected_log_msg = '2 restore %s 1 7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f -' % time
        eq_(actual_log_msg, expected_log_msg)
