import collections
import re

import psycopg2
import pytest

from taxi_tests.environment.services import postgresql

from . import control
from . import exceptions
from . import utils

pytest_plugins = [
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.mocked_time',
]

DB_FILE_RE_PATTERN = re.compile(r'/pg_(?P<pg_db_alias>\w+)(/?\w*)\.sql$')


class PostgresqlDatabases:
    def __init__(self, postgresql_connections):
        for name, connection in postgresql_connections.items():
            database = _load_sqlconfig(connection)
            setattr(self, name, database)


class ServiceLocalConfig:
    def __init__(self, databases):
        self.databases = databases
        self._initialized = False
        self._connections = {}

    def initialize(self, pg_control):
        if self._initialized:
            return self._connections
        for database in self.databases:
            connections = database.initialize(pg_control)
            self._connections.update(connections)
        self._initialized = True
        return self._connections


@pytest.fixture
def pgsql(_pgsql, pgsql_apply):
    """Returns intialized pgsql wrapper."""
    return _pgsql


@pytest.fixture(scope='session')
def pgsql_local_create():
    def _pgsql_local_create(databases):
        return ServiceLocalConfig(databases)
    return _pgsql_local_create


@pytest.fixture(scope='session')
def pgsql_disabled(pytestconfig):
    return pytestconfig.getoption('--no-postgresql')


@pytest.fixture
def pgsql_local():
    """pgsql service local instance.

    In order to use pgsql fixture you have to override pgsql_local()
    """
    return ServiceLocalConfig([])


@pytest.fixture
def _pgsql(_postgresql_service, pgsql_local, pg_control, pgsql_disabled):
    if pgsql_disabled:
        pgsql_local = ServiceLocalConfig([])

    return pgsql_local.initialize(pg_control)


@pytest.fixture
def pgsql_apply(
        request, _pgsql, load, get_directory_path, testsuite_session_context):
    """Initialize PostgreSQL database with data.

    By default pg_${DBNAME}.sql and pg_${DBNAME}/*.sql files are used
    to fill PostgreSQL databases.

    Use pytest.mark.pgsql to change this behaviour:

    @pytest.mark.pgsql(
        'foo@0',
        files=[
            'pg_foo@0_alternative.sql'
        ],
        directories=[
            'pg_foo@0_alternative_dir'
        ],
        queries=[
          'INSERT INTO foo VALUES (1, 2, 3, 4)',
        ]
    )
    """
    def _pgsql_default_queries(dbname):
        queries = []
        try:
            queries.append(_substitute_mockserver(load('pg_%s.sql' % dbname)))
        except FileNotFoundError:
            pass
        try:
            queries.extend(
                _pgsql_scan_directory(get_directory_path('pg_%s' % dbname)),
            )
        except FileNotFoundError:
            pass
        return queries

    def _pgsql_mark(dbname, files=(), directories=(), queries=()):
        result_queries = []
        for path in files:
            result_queries.append(_substitute_mockserver(load(path)))
        for path in directories:
            result_queries.extend(
                _pgsql_scan_directory(get_directory_path(path)),
            )
        result_queries.extend(queries)
        return dbname, result_queries

    def _pgsql_scan_directory(root):
        result = []
        for path in utils.scan_sql_directory(root):
            with open(path) as fp:
                result.append(_substitute_mockserver(fp.read()))
        return result

    def _substitute_mockserver(str_val: str):
        mockserver = testsuite_session_context.mockserver
        if mockserver is None:
            return str_val
        return str_val.replace(
            '$mockserver',
            '{}:{}'.format(mockserver.host, mockserver.port),
        )

    pgsql_marks = request.node.get_marker('pgsql') or []
    overrides = collections.defaultdict(list)
    for mark in pgsql_marks:
        dbname, queries = _pgsql_mark(*mark.args, **mark.kwargs)
        if dbname not in _pgsql:
            raise exceptions.PostgresqlError(
                'Unknown database %s' % (dbname,),
            )
        overrides[dbname].extend(queries)

    for dbname, pg_db in _pgsql.items():
        if dbname in overrides:
            queries = overrides[dbname]
        else:
            queries = _pgsql_default_queries(dbname)
        pg_db.apply_queries(queries)


@pytest.fixture
def _postgresql_service(pytestconfig, pgsql_disabled, ensure_service_started,
                        pgsql_local):
    if (not pgsql_disabled and pgsql_local.databases and
            not pytestconfig.getoption('--postgresql')):
        ensure_service_started('postgresql')


@pytest.fixture(scope='session')
def postgresql_connections(settings, postgresql_base_connstr, pgsql_disabled):
    """
    :return: postgresql connection string
    """
    if pgsql_disabled:
        return {}
    return {
        dbname: postgresql_base_connstr + dbname
        for dbname in getattr(settings, 'POSTGRESQL_CONNECTIONS', {})
    }


@pytest.fixture(scope='session')
def postgresql_base_connstr(request, worker_id):
    connstr = request.config.getoption('--postgresql')
    if not connstr:
        return postgresql.get_connection_string(worker_id)
    return _build_base_connstr(connstr)


def pytest_addoption(parser):
    """
    :param parser: pytest's argument parser
    """
    group = parser.getgroup('postgresql')
    group.addoption('--postgresql', help='PostgreSQL connection string')
    group.addoption('--no-postgresql', help='Disable use of PostgreSQL',
                    action='store_true')


@pytest.fixture(scope='session')
def pg_control(postgresql_base_connstr, pgsql_disabled):
    if pgsql_disabled:
        return {}
    return control.PgControl(postgresql_base_connstr)


def _build_base_connstr(connection_string):
    parts = []
    dbname_part = 'dbname='
    for part in connection_string.split():
        if part.startswith('dbname='):
            dbname_part = part
        else:
            parts.append(part)
    parts.append(dbname_part)
    return ' '.join(parts)


def _load_sqlconfig(connection_string):
    return control.PgDatabaseWrapper(
        psycopg2.connect(connection_string),
    )
