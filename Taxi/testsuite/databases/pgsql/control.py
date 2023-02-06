import contextlib
import logging
import pathlib
import time
import typing

import psycopg2
import psycopg2.extensions

from testsuite import utils as testsuite_utils
from testsuite.environment import shell

from . import connection
from . import discover
from . import exceptions
from . import service
from . import testsuite_db

logger = logging.getLogger(__name__)

CREATE_DATABASE_TEMPLATE = """
CREATE DATABASE "{}" WITH TEMPLATE = template0
ENCODING='UTF8' LC_COLLATE='C' LC_CTYPE='C'
"""
DROP_DATABASE_TEMPLATE = 'DROP DATABASE IF EXISTS "{}"'
LIST_TABLES_SQL = """
SELECT CONCAT(table_schema, '.', table_name)
FROM information_schema.tables
WHERE table_schema != 'information_schema' AND
table_schema != 'pg_catalog' AND table_type = 'BASE TABLE'
ORDER BY table_schema,table_name
"""

TRUNCATE_SQL_TEMPLATE = 'TRUNCATE TABLE {tables} RESTART IDENTITY'
TRUNCATE_RETRIES = 5
TRUNCATE_RETRY_DELAY = 0.005


class BaseError(Exception):
    pass


class UninitializedUsageError(BaseError):
    pass


class PgDatabaseWrapper:
    def __init__(self, conninfo: connection.PgConnectionInfo):
        self._initialized = False
        self._conninfo = conninfo
        self._conn: typing.Optional[psycopg2.extensions.connection] = None
        self._tables: typing.Optional[typing.List[str]] = None

    def initialize(self):
        if self._initialized:
            return
        self._conn = psycopg2.connect(self.conninfo.get_uri())
        self._conn.autocommit = True
        cursor = self._conn.cursor()
        with contextlib.closing(cursor):
            cursor.execute(LIST_TABLES_SQL)
            self._tables = [table[0] for table in cursor]
        self._initialized = True

    @property
    def conninfo(self) -> connection.PgConnectionInfo:
        """ returns
        :py:class:`testsuite.databases.pgsql.connection.PgConnectionInfo`
        """
        return self._conninfo

    @property
    def conn(self) -> psycopg2.extensions.connection:
        """:returns: :py:class:`psycopg2.extensions.connection`"""
        if self._conn is None:
            raise UninitializedUsageError
        return self._conn

    def cursor(self) -> psycopg2.extensions.cursor:
        """:returns: :py:class:`psycopg2.extensions.cursor`"""
        if self._conn is None:
            raise UninitializedUsageError
        return self._conn.cursor()

    def apply_queries(self, queries: typing.Iterable[str]) -> None:
        """Apply queries to database"""
        cursor = self.cursor()
        with contextlib.closing(cursor):
            self._try_truncate_tables(cursor)
            for query in queries:
                self._apply_query(cursor, query)

    def _try_truncate_tables(self, cursor) -> None:
        for _ in range(TRUNCATE_RETRIES):
            try:
                self._truncate_tables(cursor)
                break
            except psycopg2.extensions.TransactionRollbackError as exc:
                logger.warning('Truncate table failed: %r', exc)
                time.sleep(TRUNCATE_RETRY_DELAY)
        else:
            self._truncate_tables(cursor)

    def _truncate_tables(self, cursor) -> None:
        if self._tables:
            cursor.execute(
                TRUNCATE_SQL_TEMPLATE.format(tables=','.join(self._tables)),
            )

    @staticmethod
    def _apply_query(cursor, query) -> None:
        queries: typing.Iterable[str]
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
    _applied_schemas: typing.Dict[str, typing.Set[pathlib.Path]]
    _connections: typing.Dict[str, PgDatabaseWrapper]

    def __init__(
            self,
            pgsql_conninfo: connection.PgConnectionInfo,
            *,
            verbose: int,
            skip_applied_schemas: bool,
    ) -> None:
        self._conninfo = pgsql_conninfo
        self._connections = {}
        self._psql_helper = _get_psql_helper()
        self._pgmigrate = _get_pgmigrate()
        self._verbose = verbose
        self._applied_schemas = {}
        self._skip_applied_schemas = skip_applied_schemas

    @testsuite_utils.cached_property
    def _applied_schema_hashes(
            self,
    ) -> typing.Optional[testsuite_db.AppliedSchemaHashes]:
        if self._skip_applied_schemas:
            return testsuite_db.AppliedSchemaHashes(
                self._connection, self._conninfo,
            )
        return None

    def get_connection_cached(self, dbname) -> PgDatabaseWrapper:
        if dbname not in self._connections:
            self._connections[dbname] = PgDatabaseWrapper(
                self._conninfo.replace(dbname=dbname),
            )
        return self._connections[dbname]

    def initialize_sharded_db(
            self, database: discover.PgShardedDatabase,
    ) -> None:
        logger.debug(
            'Initializing database %s for service %s...',
            database.dbname,
            database.service_name,
        )
        for shard in database.shards:
            self._initialize_shard(shard)

    def _initialize_shard(self, shard: discover.PgShard) -> None:
        logger.debug('Creating database %s', shard.dbname)
        if self._applied_schema_hashes is None:
            self._create_database(shard.dbname)
            self._apply_schema(shard)
        else:
            applied_hash = self._applied_schema_hashes.get_hash(shard.dbname)
            current_hash = shard.get_schema_hash()
            if applied_hash is not None and current_hash == applied_hash:
                logger.debug('Shard %s: schema is up to date', shard.dbname)
            else:
                self._create_database(shard.dbname)
                self._apply_schema(shard)
                self._applied_schema_hashes.set_hash(
                    shard.dbname, current_hash,
                )

    def _create_database(self, dbname: str) -> None:
        if dbname in self._applied_schemas:
            return
        cursor = self._connection.cursor()
        with contextlib.closing(cursor):
            cursor.execute(DROP_DATABASE_TEMPLATE.format(dbname))
            cursor.execute(CREATE_DATABASE_TEMPLATE.format(dbname))
        self._applied_schemas[dbname] = set()

    def _apply_schema(self, shard: discover.PgShard) -> None:
        applied_schemas = self._applied_schemas[shard.dbname]
        for path in shard.files:
            if path in applied_schemas:
                continue
            logger.debug(
                'Running sql script %s against database %s',
                path,
                shard.dbname,
            )
            self._run_script(shard.dbname, path)
            applied_schemas.add(path)

        if shard.migrations:
            for path in shard.migrations:
                if path in applied_schemas:
                    continue
                logger.debug(
                    'Running migrations from %s against database %s',
                    path,
                    shard.dbname,
                )
                self._run_migrations(shard.dbname, path)
                applied_schemas.add(path)

    def _run_script(self, dbname, path) -> None:
        command = [
            str(self._psql_helper),
            '-q',
            '-d',
            self._get_connection_uri(dbname),
            '-v',
            'ON_ERROR_STOP=1',
            '-f',
            path,
        ]
        shell.execute(
            command, verbose=self._verbose, command_alias='pgsql/script',
        )

    def _run_migrations(self, dbname, path) -> None:
        command = [
            str(self._pgmigrate),
            '-c',
            self._get_connection_dsn(dbname),
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

    @testsuite_utils.cached_property
    def _connection(self) -> psycopg2.extensions.connection:
        """Connection to 'postgres' database."""
        pg_connection = self._create_connection('postgres')
        pg_connection.autocommit = True
        return pg_connection

    def _create_connection(self, dbname) -> psycopg2.extensions.connection:
        return psycopg2.connect(self._get_connection_uri(dbname))

    def _get_connection_uri(self, dbname: str) -> str:
        return self._conninfo.replace(dbname=dbname).get_uri()

    def _get_connection_dsn(self, dbname: str) -> str:
        return self._conninfo.replace(dbname=dbname).get_dsn()


def _get_psql_helper() -> pathlib.Path:
    return service.SCRIPTS_DIR.joinpath('psql-helper')


def _get_pgmigrate() -> pathlib.Path:
    return service.SCRIPTS_DIR.joinpath('pgmigrate-helper')
