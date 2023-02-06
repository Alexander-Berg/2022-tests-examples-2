# coding: utf-8

from alembic import command as alembic_command
from passport.backend.vault.api.db import get_db
from passport.backend.vault.api.test.base_test_class import BaseTestClass


def sqlite_fetch_db_tables(engine):
    return [row[0] for row in engine.execute('SELECT name FROM sqlite_master WHERE type = \'table\'')]


def sqlite_fetch_table_columns(engine, table_name):
    return [row[1] for row in engine.execute('PRAGMA table_info(%s)' % table_name)]


def mysql_fetch_db_tables(engine):
    return [row[0] for row in engine.execute('SHOW TABLES')]


def mysql_fetch_table_columns(engine, table_name):
    return [row[0] for row in engine.execute('DESCRIBE %s' % table_name)]


class TestMigrations(BaseTestClass):
    fill_database = False

    def setUp(self):
        super(TestMigrations, self).setUp()
        with self.app.app_context():
            self.db = get_db()
            self.dialect_name = self.db.get_engine().dialect.name

            if self.dialect_name == 'mysql':
                self.fetch_tables_func = mysql_fetch_db_tables
                self.fetch_table_columns_func = mysql_fetch_table_columns
            else:
                self.fetch_tables_func = sqlite_fetch_db_tables
                self.fetch_table_columns_func = sqlite_fetch_table_columns
            self.cleanup_db()

    def tearDown(self):
        self.cleanup_db()
        super(TestMigrations, self).tearDown()

    def cleanup_db(self):
        with self.app.app_context():
            for table in self.fetch_tables_func(self.db.get_engine()):
                if self.dialect_name == 'mysql':
                    self.db.get_engine().execute('SET FOREIGN_KEY_CHECKS=0')
                self.db.get_engine().execute('DROP TABLE %s' % table)

    def fetch_db_tables(self):
        return sorted(
            filter(
                lambda x: x != 'alembic_version',
                self.fetch_tables_func(self.db.get_engine()),
            ),
        )

    def fetch_models_tables(self):
        return sorted([table.name for table in self.db.metadata.sorted_tables])

    def assert_table_columns(self, table):
        """Сравниваем поля в таблице и модели"""
        db_columns = sorted(self.fetch_table_columns_func(self.db.get_engine(), table))
        model_columns = sorted([
            row.name
            for row in self.db.metadata.tables[table].columns
        ])
        self.assertListEqual(
            db_columns,
            model_columns,
        )

    def test_db_upgrade(self):
        with self.app.app_context():
            # На пустую базу накатываем миграцию. Проверяем, что создались
            # все таблички и у табличек и моделей совпадают поля.
            tables = self.fetch_db_tables()
            self.assertEqual(len(tables), 0)

            # Подпихиваем Алембику наше соединение и зовем upgrade
            config = self.app.extensions['migrate'].migrate.get_config()
            config.attributes['connection'] = self.db.get_engine().connect()
            alembic_command.upgrade(config, 'head')

            tables = self.fetch_db_tables()
            self.assertGreater(len(tables), 0)

            self.assertListEqual(
                tables,
                self.fetch_models_tables(),
            )

            for tab in tables:
                self.assert_table_columns(tab)
