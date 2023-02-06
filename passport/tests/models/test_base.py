# coding: utf-8

import re
import time

from passport.backend.vault.api.app import create_cli
from passport.backend.vault.api.commands.generate import sql_dialect_by_name
from passport.backend.vault.api.db import get_db
from passport.backend.vault.api.models import Secret
from passport.backend.vault.api.models.base import (
    MagicBigInteger,
    MagicBLOB,
    MagicInteger,
    MagicJSON,
    MySQLMatch,
    StringyJSON,
    Timestamp,
)
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from sqlalchemy import types
import sqlalchemy.dialects.mysql.types as mysql_types


class TestModelsRepr(BaseTestClass):
    def test_repr_after_flush(self):
        with self.app.app_context():
            secret = Secret(
                uuid='10000000000000000000000001',
                name='Test',
                created_at=time.time(),
                created_by=1,
                updated_at=time.time(),
                updated_by=1,
            )
            get_db().session.add(secret)
            get_db().session.flush()
            self.assertEqual(repr(secret), '<Secret #10000000000000000000000001 "Test">')

    def test_repr_before_flush(self):
        with self.app.app_context():
            secret = Secret(
                uuid='10000000000000000000000001',
                name='Test',
                created_at=time.time(),
                created_by=1,
                updated_at=time.time(),
                updated_by=1,
            )
            self.assertEqual(repr(secret), '<Secret #None "Test">')


class TestStringyJSON(BaseTestClass):
    def setUp(self):
        super(TestStringyJSON, self).setUp()
        self.json_decorator = StringyJSON()

    def test_process_bind(self):
        self.assertEqual(
            self.json_decorator.process_bind_param({'key': 'value'}, None),
            '{"key": "value"}',
        )

    def test_process_result(self):
        self.assertDictEqual(
            self.json_decorator.process_result_value('{"key": "value"}', None),
            {'key': 'value'},
        )


class TestTypeDecoratorsImpl(BaseTestClass):
    def setUp(self):
        super(TestTypeDecoratorsImpl, self).setUp()
        self.mysql_dialect = sql_dialect_by_name('mysql')
        self.sqlite_dialect = sql_dialect_by_name('sqlite')

    def test_integer_id_mysql_impl(self):
        decorator = MagicInteger()
        mysql_impl = decorator.load_dialect_impl(self.mysql_dialect)
        self.assertIsInstance(mysql_impl, mysql_types.INTEGER)
        self.assertTrue(mysql_impl.unsigned)

    def test_integer_id_sqlite_impl(self):
        decorator = MagicInteger()
        sqlite_impl = decorator.load_dialect_impl(self.sqlite_dialect)
        self.assertIsInstance(sqlite_impl, types.Integer)

    def test_big_integer_id_mysql_impl(self):
        decorator = MagicBigInteger()
        mysql_impl = decorator.load_dialect_impl(self.mysql_dialect)
        self.assertIsInstance(mysql_impl, mysql_types.BIGINT)
        self.assertTrue(mysql_impl.unsigned)

    def test_big_integer_id_sqlite_impl(self):
        decorator = MagicBigInteger()
        sqlite_impl = decorator.load_dialect_impl(self.sqlite_dialect)
        self.assertIsInstance(sqlite_impl, types.BigInteger)

    def test_timestamp_mysql_impl(self):
        decorator = Timestamp()
        mysql_impl = decorator.load_dialect_impl(self.mysql_dialect)
        self.assertIsInstance(mysql_impl, mysql_types.NUMERIC)
        self.assertEqual(mysql_impl.precision, 15)
        self.assertEqual(mysql_impl.scale, 3)

    def test_timestamp_sqlite_impl(self):
        decorator = Timestamp()
        sqlite_impl = decorator.load_dialect_impl(self.sqlite_dialect)
        self.assertIsInstance(sqlite_impl, types.Float)

    def test_magic_json_mysql_impl(self):
        decorator = MagicJSON()
        mysql_impl = decorator.load_dialect_impl(self.mysql_dialect)
        self.assertIsInstance(mysql_impl, types.JSON)

    def test_magic_json_sqlite_impl(self):
        decorator = MagicJSON()
        sqlite_impl = decorator.load_dialect_impl(self.sqlite_dialect)
        self.assertIsInstance(sqlite_impl, StringyJSON)

    def test_magic_blob_mysql_impl(self):
        decorator = MagicBLOB()
        mysql_impl = decorator.load_dialect_impl(self.mysql_dialect)
        self.assertIsInstance(mysql_impl, mysql_types.MEDIUMBLOB)

    def test_magic_blob_sqlite_impl(self):
        decorator = MagicBLOB()
        sqlite_impl = decorator.load_dialect_impl(self.sqlite_dialect)
        self.assertIsInstance(sqlite_impl, types.BLOB)


class TestDatabase(BaseTestClass):
    maxDiff = None

    def setUp(self):
        super(TestDatabase, self).setUp()
        self.runner = self.app.test_cli_runner()

    def test_autoincrement_not_found(self):
        with self.app.app_context():
            result = self.runner.invoke(create_cli(self.app, self.config), ['generate', 'schema', '--dialect=mysql'])
            self.assertEqual(result.exit_code, 0)
            self.assertRegexpMatches(
                result.output,
                re.compile(r'CREATE\sTABLE\ssecrets\s\(.+?CREATE\sINDEX', re.DOTALL),
            )
            self.assertNotRegexpMatches(
                result.output,
                re.compile(r'AUTO_INCREMENT', re.I),
            )


class TestMySQLMatch(BaseTestClass):
    def test_generate_match_statement(self):
        clause = MySQLMatch([Secret.name, Secret.comment], u'пасспорт')
        self.assertEqual(
            (
                str(clause),
                clause.compile().params,
            ),
            (
                'MATCH (secrets.name, secrets.comment) AGAINST (:param_1 )',
                {u'param_1': u'пасспорт'},
            )
        )

    def test_generate_match_statement_with_mode(self):
        clause = MySQLMatch([Secret.name, Secret.comment], u'пасспорт', MySQLMatch.BOOLEAN_MODE)
        self.assertEqual(
            (
                str(clause),
                clause.compile().params,
            ),
            (
                'MATCH (secrets.name, secrets.comment) AGAINST (:param_1 IN BOOLEAN MODE)',
                {u'param_1': u'пасспорт'},
            )
        )
