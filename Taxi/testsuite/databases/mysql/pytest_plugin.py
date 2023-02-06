import collections
import typing

import pytest

from . import classes
from . import control
from . import service
from . import utils


def pytest_addoption(parser):
    """
    :param parser: pytest's argument parser
    """
    group = parser.getgroup('mysql')
    group.addoption('--mysql')
    group.addoption(
        '--no-mysql', help='Disable use of MySQL', action='store_true',
    )


def pytest_configure(config):
    config.addinivalue_line('markers', 'mysql: per-test MySQL initialization')


def pytest_service_register(register_service):
    register_service('mysql', service.create_service)


@pytest.fixture
def mysql(_mysql, _mysql_apply) -> typing.Dict[str, control.ConnectionWrapper]:
    """MySQL fixture.

    Returns dictionary where key is database alias and value is
    :py:class:`control.ConnectionWrapper`
    """
    return _mysql.get_wrappers()


@pytest.fixture(scope='session')
def mysql_disabled(pytestconfig) -> bool:
    return pytestconfig.option.no_mysql


@pytest.fixture(scope='session')
def mysql_conninfo(pytestconfig, _mysql_service_settings):
    if pytestconfig.option.mysql:
        return service.parse_connection_url(pytestconfig.option.mysql)
    return _mysql_service_settings.get_conninfo()


@pytest.fixture(scope='session')
def mysql_local() -> classes.DatabasesDict:
    """Use to override databases configuration."""
    return {}


@pytest.fixture
def _mysql(mysql_local, _mysql_service, _mysql_state):
    if not _mysql_service:
        mysql_local = {}
    dbcontrol = control.Control(mysql_local, _mysql_state)
    dbcontrol.run_migrations()
    return dbcontrol


@pytest.fixture
def _mysql_apply(mysql_local, _mysql_state, load, get_directory_path, request):
    def _load_default_queries(dbname):
        queries = []
        try:
            queries.append(load(f'my_{dbname}.sql'))
        except FileNotFoundError:
            pass
        try:
            queries.extend(
                utils.load_queries_directory(
                    get_directory_path('my_{dbname}'),
                ),
            )
        except FileNotFoundError:
            pass
        return queries

    def mysql_mark(dbname, *, files=(), directories=(), queries=()):
        result_queries = []
        for path in files:
            result_queries.append(load(path))
        for path in directories:
            result_queries.extend(
                utils.load_queries_directory(get_directory_path(path)),
            )
        result_queries.extend(queries)
        return dbname, queries

    overrides = collections.defaultdict(list)

    for mark in request.node.iter_markers('mysql'):
        dbname, queries = mysql_mark(*mark.args, **mark.kwargs)
        if dbname not in mysql_local:
            raise RuntimeError(f'Unknown mysql database {dbname}')
        overrides[dbname].extend(queries)

    for alias, dbconfig in mysql_local.items():
        if alias in overrides:
            queries = overrides[alias]
        else:
            queries = _load_default_queries(alias)
        _mysql_state.apply_queries(dbconfig.dbname, queries)


@pytest.fixture(scope='session')
def _mysql_service_settings():
    return service.get_service_settings()


@pytest.fixture
def _mysql_service(
        ensure_service_started,
        mysql_local,
        mysql_disabled,
        pytestconfig,
        _mysql_service_settings,
):
    if not mysql_local or mysql_disabled:
        return False
    if not pytestconfig.option.mysql:
        ensure_service_started('mysql', settings=_mysql_service_settings)
    return True


@pytest.fixture(scope='session')
def _mysql_state(pytestconfig, mysql_conninfo):
    return control.DatabasesState(
        connections=control.ConnectionCache(mysql_conninfo),
        verbose=pytestconfig.option.verbose,
    )
