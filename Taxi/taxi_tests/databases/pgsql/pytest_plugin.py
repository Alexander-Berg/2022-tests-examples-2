import collections
import os
import re

import psycopg2
import pytest

from taxi_tests.environment import service

from . import control
from . import exceptions
from . import utils

DB_FILE_RE_PATTERN = re.compile(r'/pg_(?P<pg_db_alias>\w+)(/?\w*)\.sql$')

DEFAULT_PORT = 5433


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


def pytest_addoption(parser):
    """
    :param parser: pytest's argument parser
    """
    group = parser.getgroup('postgresql')
    group.addoption('--postgresql', help='PostgreSQL connection string')
    group.addoption(
        '--no-postgresql',
        help='Disable use of PostgreSQL',
        action='store_true',
    )


def pytest_service_register(register_service):
    @register_service('postgresql')
    def create_service(service_name, working_dir, port=DEFAULT_PORT, env=None):
        return service.ScriptService(
            service_name=service_name,
            script_path=os.path.join(utils.SCRIPTS_DIR, 'service-postgresql'),
            working_dir=working_dir,
            environment={
                'POSTGRESQL_TMPDIR': working_dir,
                'POSTGRESQL_CONFIGS_DIR': utils.CONFIGS_DIR,
                'POSTGRESQL_PORT': str(port),
                **(env or {}),
            },
            check_ports=[port],
        )


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
def pgsql_apply(request, _pgsql, load, get_directory_path, mockserver_info):
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
        return str_val.replace(
            '$mockserver',
            'http://{}:{}'.format(mockserver_info.host, mockserver_info.port),
        )

    pgsql_marks = request.node.get_marker('pgsql') or []
    overrides = collections.defaultdict(list)
    for mark in pgsql_marks:
        dbname, queries = _pgsql_mark(*mark.args, **mark.kwargs)
        if dbname not in _pgsql:
            raise exceptions.PostgresqlError('Unknown database %s' % (dbname,))
        overrides[dbname].extend(queries)

    for dbname, pg_db in _pgsql.items():
        if dbname in overrides:
            queries = overrides[dbname]
        else:
            queries = _pgsql_default_queries(dbname)
        pg_db.apply_queries(queries)


@pytest.fixture
def _postgresql_service(
        pytestconfig,
        pgsql_disabled,
        ensure_service_started,
        pgsql_local,
        _postgresql_port,
):
    if (
            not pgsql_disabled
            and pgsql_local.databases
            and not pytestconfig.getoption('--postgresql')
    ):
        ensure_service_started('postgresql', port=_postgresql_port)


@pytest.fixture(scope='session')
def _postgresql_port(worker_id, get_free_port):
    if worker_id == 'master':
        return DEFAULT_PORT
    return get_free_port()


@pytest.fixture(scope='session')
def postgresql_base_connstr(request, _postgresql_port):
    connstr = request.config.getoption('--postgresql')
    if not connstr:
        return _get_connection_string(_postgresql_port)
    return _build_base_connstr(connstr)


@pytest.fixture(scope='session')
def pg_control(pytestconfig, postgresql_base_connstr, pgsql_disabled):
    if pgsql_disabled:
        return {}
    return control.PgControl(
        postgresql_base_connstr, verbose=pytestconfig.option.verbose,
    )


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
    return control.PgDatabaseWrapper(psycopg2.connect(connection_string))


def _get_connection_string(port):
    return 'host=localhost port=%d user=testsuite dbname=' % port
