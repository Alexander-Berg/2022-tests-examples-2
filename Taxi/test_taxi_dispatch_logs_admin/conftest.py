# pylint: disable=redefined-outer-name
import pytest

import taxi_dispatch_logs_admin.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_dispatch_logs_admin.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist, pgsql_local):
    simple_secdist['settings_override'].update(
        {
            'YT_CONFIG': {
                'hahn': {
                    'token': 'FAKE_YT_TOKEN',
                    'prefix': '//home/taxi',
                    'proxy': {'url': 'hahn.yt.yandex.net'},
                    'api_version': 'v3',
                },
            },
            'YQL_TOKEN': 'FAKE_YQL_TOKEN',
        },
    )
    simple_secdist['postgresql_settings'].update(
        {
            'databases': {
                'yt_logs_imports': [
                    {
                        'shard_number': 0,
                        'hosts': [pgsql_local['yt_logs_imports'].get_dsn()],
                    },
                ],
            },
        },
    )
    return simple_secdist
