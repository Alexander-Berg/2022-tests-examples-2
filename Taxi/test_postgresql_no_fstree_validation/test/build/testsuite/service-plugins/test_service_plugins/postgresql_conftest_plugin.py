# pylint: skip-file
# flake8: noqa
import os
import pytest

from tests_plugins import pgsupport


@pytest.fixture(scope='session')
def pgsql_local(pgsql_local_create, get_source_path, service_source_dir):
    service_yaml = {
        'postgresql': {
            'databases': [
                'orders',
            ],
        },
        'short-name': 'test-service',
    }
    databases = _pgsql_discover(
        'yandex-taxi-test-service', service_yaml,
        get_source_path, service_source_dir,
    )
    return pgsql_local_create(databases)


@pytest.fixture(scope='session')
def postgresql_local_settings(pgsql_local):
    return {
        'composite_tables_count': 1,
        'databases': {
            'orders': [
                {
                    'shard_number': 0,
                    'hosts': [
                        pgsql_local['orders'].get_uri(),
                        pgsql_local['orders'].replace(
                            options='-c default_transaction_read_only=on',
                        ).get_uri()
                    ],
                },
            ],
        },
    }


@pytest.fixture(scope='session')
def postgresql_settings_substitute(postgresql_local_settings):
    return {'postgresql_settings': lambda _: postgresql_local_settings}


def _pgsql_discover(
    service_name, service_yaml, get_source_path, service_source_dir,
):
    databases = pgsupport.find_databases(
        service_name, get_source_path, service_source_dir, service_yaml,
    )
    for dbname, database in databases.items():
        if not database.shards:
            raise pgsupport.PgConfigurationError(
                'No shards configured for postgresql database %s' % (
                    dbname,
                )
            )
    return list(databases.values())

