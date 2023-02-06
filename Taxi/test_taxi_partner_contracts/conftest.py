# pylint: disable=redefined-outer-name
import pytest

import taxi_partner_contracts.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_partner_contracts.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist, pgsql):
    simple_secdist['settings_override'][
        'PARTNER_CONTRACTS_API_TOKEN'
    ] = 'a8f5513cc4c84d18b56acd86bdd691ed'
    simple_secdist['settings_override']['AMOCRM_SETTINGS'] = {
        'login': 'login',
        'token': 'token',
    }
    simple_secdist['postgresql_settings']['databases']['partner_contracts'] = [
        {
            'shard_number': 0,
            'hosts': [
                ' '.join(
                    f'{k}={v}'
                    for k, v in pgsql['partner_contracts']
                    .conn.get_dsn_parameters()
                    .items()
                    if k in ('host', 'port', 'user', 'password', 'dbname')
                ),
            ],
        },
    ]
    return simple_secdist
