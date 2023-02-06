import logging
import pathlib
import typing

import pymysql
import pymysql.constants

from testsuite.environment import shell
from testsuite.utils import cached_property

from . import classes


logger = logging.getLogger(__name__)

MYSQL_HELPER = pathlib.Path(__file__).parent.joinpath('scripts/mysql-helper')


class ConnectionWrapper:
    """MySQL database connection wrapper."""

    def __init__(self, connection, conninfo):
        self._connection = connection
        self._conninfo = conninfo

    @property
    def conninfo(self) -> classes.ConnectionInfo:
        """:py:class:`classes.ConnectionInfo` instance."""
        return self._conninfo

    def cursor(self) -> pymysql.cursors.Cursor:
        """Returns cursor instance."""
        return self._connection.cursor()


class ConnectionCache:
    def __init__(self, conninfo, verbose: bool = False):
        self._conninfo = conninfo
        self._cache: dict = {}
        self._master_connection = None

    def get_master_connection(self):
        if self._master_connection is None:
            self._master_connection = self._connect(self._conninfo)
        return self._master_connection

    def get_conninfo(self, dbname: str) -> classes.ConnectionInfo:
        return self._conninfo.replace(dbname=dbname)

    def get_connection(self, dbname):
        if dbname not in self._cache:
            self._cache[dbname] = self._create_connection(dbname)
        return self._cache[dbname]

    def _create_connection(self, dbname):
        return self._connect(self.get_conninfo(dbname))

    def _connect(self, conninfo: classes.ConnectionInfo):
        return pymysql.connect(
            host=conninfo.hostname,
            port=conninfo.port,
            user=conninfo.user,
            password=conninfo.password,
            database=conninfo.dbname,
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
        )


class DatabasesState:
    _migrations_run: typing.Set[typing.Tuple[str, str]]
    _initialized: typing.Set[str]

    def __init__(self, connections: ConnectionCache, verbose: bool = False):
        self._connections = connections
        self._verbose = verbose
        self._migrations_run = set()
        self._initialized = set()

    def get_connection(self, dbname: str):
        if dbname not in self._initialized:
            self._initdb(dbname)
        return self._connections.get_connection(dbname)

    def wrapper_for(self, dbname: str):
        return ConnectionWrapper(
            self._connections.get_connection(dbname),
            self._connections.get_conninfo(dbname),
        )

    def run_migration(self, dbname: str, path: str):
        key = dbname, path
        if key in self._migrations_run:
            return
        logger.debug(
            'Running mysql script %s against databse %s', path, dbname,
        )
        conninfo = self._connections.get_conninfo(dbname)
        _run_script(conninfo, ['-e', f'source {path}'], verbose=self._verbose)
        self._migrations_run.add(key)

    def apply_queries(self, dbname: str, queries: typing.List[str]):
        connection = self._connections.get_connection(dbname)
        with connection.cursor() as cursor:
            cursor.execute('show tables')
            for (table,) in cursor.fetchall():
                cursor.execute(f'truncate table {table}')
            for query in queries:
                cursor.execute(query, args=[])
        connection.commit()

    @cached_property
    def known_databases(self):
        connection = self._connections.get_master_connection()
        cursor = connection.cursor()
        cursor.execute('show databases')
        return {row[0] for row in cursor.fetchall()}

    def _initdb(self, dbname: str):
        connection = self._connections.get_master_connection()
        with connection.cursor() as cursor:
            if dbname in self.known_databases:
                cursor.execute(f'DROP DATABASE IF EXISTS `{dbname}`')
            cursor.execute(f'CREATE DATABASE `{dbname}`')
        connection.commit()
        self._initialized.add(dbname)


class Control:
    def __init__(
            self, databases: classes.DatabasesDict, state: DatabasesState,
    ):
        self._databases = databases
        self._state = state

    def get_wrappers(self):
        return {
            alias: self._state.wrapper_for(dbconfig.dbname)
            for alias, dbconfig in self._databases.items()
        }

    def run_migrations(self):
        for dbconfig in self._databases.values():
            self._run_database_migrations(dbconfig)

    def _run_database_migrations(self, dbconfig):
        self._state.get_connection(dbconfig.dbname)
        for path in dbconfig.migrations:
            self._state.run_migration(dbconfig.dbname, path)


def _build_mysql_args(conninfo: classes.ConnectionInfo) -> typing.List[str]:
    result = ['--protocol=tcp']
    if conninfo.hostname:
        result.append(f'--host={conninfo.hostname}')
    if conninfo.port:
        result.append(f'--port={conninfo.port}')
    if conninfo.user:
        result.append(f'--user={conninfo.user}')
    if conninfo.password:
        result.append(f'--password={conninfo.password}')
    if conninfo.dbname:
        result.append(f'--database={conninfo.dbname}')
    return result


def _run_script(
        conninfo: classes.ConnectionInfo,
        args: typing.List[str],
        verbose: bool,
):
    command = [str(MYSQL_HELPER), *_build_mysql_args(conninfo), *args]
    shell.execute(command, verbose=verbose, command_alias='mysql/script')
