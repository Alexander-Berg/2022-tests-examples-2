import contextlib
import os
import typing

import psycopg2

from taxi_tests import utils as testsuite_utils
from taxi_tests.environment import shell

from . import exceptions
from . import utils

CREATE_DATABASE_TEMPLATE = (
    'CREATE DATABASE "{}" WITH TEMPLATE = template0 '
    'ENCODING = \'UTF8\' LC_COLLATE = \'C\' LC_CTYPE = \'C\''
)
DROP_DATABASE_TEMPLATE = 'DROP DATABASE IF EXISTS "{}"'

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')


class PgDatabaseWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.conn.autocommit = True
        cur = conn.cursor()
        with contextlib.closing(cur):
            cur.execute(
                'SELECT CONCAT(table_schema, \'.\', table_name) '
                'FROM information_schema.tables '
                'WHERE table_schema != \'information_schema\' AND '
                'table_schema != \'pg_catalog\' AND '
                'table_type = \'BASE TABLE\''
                'ORDER BY table_schema,table_name;',
            )
            self.tables = [table[0] for table in cur]

    def cursor(self):
        return self.conn.cursor()

    def apply_queries(self, queries):
        cursor = self.cursor()
        with contextlib.closing(cursor):
            self._clear_tables(cursor)
            for query in queries:
                self._apply_query(cursor, query)

    def _clear_tables(self, cursor):
        if self.tables:
            cursor.execute(
                ' '.join(
                    (
                        'TRUNCATE TABLE',
                        ','.join(self.tables),
                        'RESTART IDENTITY',
                    ),
                ),
            )

    @staticmethod
    def _apply_query(cursor, query):
        if isinstance(query, str):
            queries = [query]
        elif isinstance(query, (list, tuple)):
            queries = query
        else:
            raise exceptions.PostgresqlError(
                'sql queries of type %s are not supported' % type(query),
            )
        for query_str in queries:
            cursor.execute(query_str)


class PgControl:
    def __init__(self, base_connstr: str, *, verbose: int):
        self.base_connstr = base_connstr
        self._connections: typing.Dict[str, PgDatabaseWrapper] = {}
        self._psql_helper = _get_psql_helper()
        self._pgmigrate = _get_pgmigrate()
        self._verbose = verbose

    @testsuite_utils.cached_property
    def connection(self):
        """Connection to 'postgres' database."""
        connection = self._create_connection('postgres')
        connection.autocommit = True
        return connection

    def create_database(self, dbname):
        # pylint: disable=no-member
        cursor = self.connection.cursor()
        with contextlib.closing(cursor):
            cursor.execute(DROP_DATABASE_TEMPLATE.format(dbname))
            cursor.execute(CREATE_DATABASE_TEMPLATE.format(dbname))

    def get_connection_string(self, database):
        return self.base_connstr + database

    def get_connection_cached(self, dbname):
        if dbname not in self._connections:
            self._connections[dbname] = PgDatabaseWrapper(
                self._create_connection(dbname),
            )
        return self._connections[dbname]

    def run_script(self, dbname, path):
        command = [
            self._psql_helper,
            '-q',
            '-d',
            self.get_connection_string(dbname),
            '-v',
            'ON_ERROR_STOP=1',
            '-f',
            path,
        ]
        shell.execute(
            command, verbose=self._verbose, command_alias='pgsql/script',
        )

    def run_migrations(self, dbname, path):
        command = [
            self._pgmigrate,
            '-c',
            self.get_connection_string(dbname),
            '-d',
            path,
            '-t',
            'latest',
            '-v',
            'migrate',
        ]
        shell.execute(
            command, verbose=self._verbose, command_alias='pgsql/migrations',
        )

    def _create_connection(self, dbname):
        return psycopg2.connect(self.get_connection_string(dbname))


def _get_psql_helper():
    return os.path.join(utils.SCRIPTS_DIR, 'psql-helper')


def _get_pgmigrate():
    return os.path.join(utils.SCRIPTS_DIR, 'pgmigrate-helper')
