import os.path

import pytest

from taxi_tests.plugins.pgsql import discover

SERVICES = ['reposition', 'tags', 'labor', 'driver-dispatcher']


class BaseError(Exception):
    pass


class PgConfigurationError(BaseError):
    pass


def find_databases(service):
    schema_path = os.path.join(
        os.path.dirname(__file__),
        #  https://wiki.yandex-team.ru/taxi/backend/testsuite/#postgresql
        '../../' + service + '/testsuite/schemas/postgresql',
    )

    migrations = os.path.join(
        os.path.dirname(__file__), '../../' + service + '/db',
    )

    return discover.find_databases(service, schema_path, migrations)


def _pgsql_discover(services):
    result = []
    for service in services:
        databases = find_databases(service)
        for dbname, database in databases.items():
            if not database.shards:
                raise PgConfigurationError(
                    'No shards configured for postgresql database %s'
                    % (dbname,),
                )
        result += databases.values()
    return result


@pytest.fixture(scope='session', autouse=True)
def pgsql_local(pgsql_local_create):
    databases = _pgsql_discover(SERVICES)
    return pgsql_local_create(databases)
