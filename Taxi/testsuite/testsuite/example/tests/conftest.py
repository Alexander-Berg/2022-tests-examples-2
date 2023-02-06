# pylint: disable=redefined-outer-name
import os

import pytest

from taxi_tests.daemons import service_client
from taxi_tests.databases.pgsql import discover

pytest_plugins = [
    # Testsuite plugins
    'taxi_tests.pytest_plugin',
    'taxi_tests.databases.mongo.pytest_plugin',
    'taxi_tests.databases.pgsql.pytest_plugin',
]

SERVICE_BASEURL = 'http://localhost:8080/'

# See https://github.yandex-team.ru/taxi/schemas/tree/master/schemas/mongo
MONGO_COLLECTIONS = {
    'example_collection': {
        'settings': {
            'collection': 'example_collection',
            'connection': 'example',
            'database': 'example_db',
        },
        'indexes': [],
    },
}


@pytest.fixture
async def server_client(
        service_daemon,
        service_client_options,
        ensure_daemon_started,
        mockserver,
        mongodb,
        pgsql,
):
    await ensure_daemon_started(service_daemon)
    yield service_client.Client(SERVICE_BASEURL, **service_client_options)


# remove scope=session to restart service on each test
@pytest.fixture(scope='session')
async def service_daemon(
        register_daemon_scope,
        service_spawner,
        mockserver_info,
        mongo_host,
        postgresql_base_connstr,
):
    python_path = os.getenv('PYTHON3', 'python3')
    async with register_daemon_scope(
            name='yandex-taxi-test-service',
            spawn=service_spawner(
                [
                    python_path,
                    '-m',
                    'example_service.server',
                    '--service-baseurl',
                    mockserver_info.base_url,
                    '--mongo-uri',
                    mongo_host,
                    '--postgresql',
                    postgresql_base_connstr,
                ],
                check_url=SERVICE_BASEURL + 'ping',
            ),
    ) as scope:
        yield scope


@pytest.fixture(scope='session')
def mongodb_settings():
    return MONGO_COLLECTIONS


@pytest.fixture(scope='session')
def pgsql_local(pgsql_local_create):
    sqldata_path = os.path.join(
        os.path.dirname(__file__), 'static/postgresql/schemas',
    )
    migrations = os.path.join(
        os.path.dirname(__file__), 'static/postgresql/migrations',
    )
    databases = discover.find_databases(
        'service_name', sqldata_path, migrations,
    )
    return pgsql_local_create(list(databases.values()))
