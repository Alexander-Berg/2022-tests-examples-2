import pytest

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_clean_old_drivers.sql'],
)
@pytest.mark.now('2020-02-02T00:10:00+00:00')
async def test_clean_old_drivers(
        taxi_dispatch_airport_partner_protocol, pgsql, taxi_config,
):
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': 150,
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_CLEANER_ENABLED': True,
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/psql-cleaner',
    )

    expected_result = [
        {'driver_id': 'dbid1_uuid1'},
        {'driver_id': 'dbid3_uuid3'},
    ]

    await utils.compare_db_with_expected(pgsql, expected_result, ['driver_id'])
