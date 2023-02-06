# coding: utf-8

from datetime import datetime
import time

from passport.backend.vault.api.test.base_test_case import BaseTestCase
from vault_client_cli.commands.format import (
    format_comment,
    format_creator,
    format_table,
    format_timestamp,
)


class TestCliFormaters(BaseTestCase):
    def test_format_empty_table(self):
        table = []

        self.assertEqual(
            format_table(table),
            ''
        )

        self.assertEqual(
            format_table(table, compact=True),
            ''
        )

        self.assertEqual(
            format_table(table, header=['column 1', 'column 2', 'column 3'], compact=True),
            'column 1    column 2    column 3\n'
            '----------  ----------  ----------\n'
        )

    def test_format_table(self):
        table = [
            ['r0-c0', 'r0-c1', 'r0-2'],
            ['r1-c0', 'r1-c1', 'r1-2'],
            ['r2-c0', 'r2-c1', 'r2-2'],
        ]

        self.assertEqual(
            format_table(table),
            '+-------+-------+------+\n'
            '| r0-c0 | r0-c1 | r0-2 |\n'
            '| r1-c0 | r1-c1 | r1-2 |\n'
            '| r2-c0 | r2-c1 | r2-2 |\n'
            '+-------+-------+------+\n'
        )

        self.assertEqual(
            format_table(table, header=['column 1', 'column 2', 'column 3']),
            '+------------+------------+------------+\n'
            '| column 1   | column 2   | column 3   |\n'
            '|------------+------------+------------|\n'
            '| r0-c0      | r0-c1      | r0-2       |\n'
            '| r1-c0      | r1-c1      | r1-2       |\n'
            '| r2-c0      | r2-c1      | r2-2       |\n'
            '+------------+------------+------------+\n'
        )

    def test_compact_format_table(self):
        table = [
            ['r0-c0', 'r0-c1', 'r0-2'],
            ['r1-c0', 'r1-c1', 'r1-2'],
            ['r2-c0', 'r2-c1', 'r2-2'],
        ]

        self.assertEqual(
            format_table(table, compact=True),
            u'-----  -----  ----\n'
            u'r0-c0  r0-c1  r0-2\n'
            u'r1-c0  r1-c1  r1-2\n'
            u'r2-c0  r2-c1  r2-2\n'
            u'-----  -----  ----\n'
        )

        self.assertEqual(
            format_table(table, header=['column 1', 'column 2', 'column 3'], compact=True),
            u'column 1    column 2    column 3\n'
            u'----------  ----------  ----------\n'
            u'r0-c0       r0-c1       r0-2\n'
            u'r1-c0       r1-c1       r1-2\n'
            u'r2-c0       r2-c1       r2-2\n'
        )

    def test_format_timestamp(self):
        test_data = [
            ['', ''],
            [time.mktime(datetime(2015, 10, 21).timetuple()), '2015-10-21 00:00:00'],
        ]
        for row in test_data:
            self.assertEqual(format_timestamp(row[0]), row[1])

    def test_format_creator(self):
        test_data = [
            [{}, '—'],
            [{'creator_login': 'user_1', 'created_by': 100}, 'user_1 (100)'],
            [{'created_by': 100}, '100'],
        ]
        for row in test_data:
            self.assertEqual(format_creator(row[0]), row[1])

    def test_format_comment(self):
        test_data = [
            ['', ''],
            ['dont wrap', 'dont wrap'],
            ['long long comment', '\nlong long\ncomment\n'],
        ]
        for row in test_data:
            self.assertEqual(format_comment(row[0], 10), row[1])
