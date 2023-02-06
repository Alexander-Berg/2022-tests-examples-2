import pytest

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.mark.parametrize(
    'driver_number',
    [
        # if not mentioned driver has only one enabled tariff
        1,  # absolute block reason and one enabled tariffs
        2,  # conditional block reason and two enabled tariffs
        3,  # time block reason
        4,  # warning block reason
        5,  # hidden block reason
        6,  # ok block reason
        7,  # several absolute block reasons
        8,  # conditional and several absolute block reasons
        9,  # driver without enabled tariffs
    ],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_driver_diagnostics_update(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        taxi_config,
        load_json,
        mockserver,
        testpoint,
        redis_store,
        now,
        driver_number,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_NOT_ALLOWED_TO_PARK_REASONS': (
                load_json('not_allowed_to_park_reasons.json')
            ),
        },
    )

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    positions = load_json('positions.json')

    driver_diagnostics_responses = load_json(
        'driver_diagnostics_responses.json',
    )

    @mockserver.json_handler(
        '/driver-diagnostics/internal/'
        'driver-diagnostics/v1/common/restrictions',
    )
    def _driver_diagnostics(request):
        assert request.headers['Accept-Language'] == 'en'
        dbid = 'dbid' + str(driver_number)
        uuid = 'uuid' + str(driver_number)
        assert request.query['park_id'] == dbid
        assert request.query['contractor_profile_id'] == uuid
        assert request.json['position'] == {
            'lat': positions['inside_parking_lot1'][1],
            'lon': positions['inside_parking_lot1'][0],
        }
        return driver_diagnostics_responses[dbid + '_' + uuid]

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    dbid = 'dbid' + str(driver_number)
    uuid = 'uuid' + str(driver_number)
    geobus_drivers = {
        dbid
        + '_'
        + uuid: {
            'position': positions['inside_parking_lot1'],
            'timestamp': now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now, True)
    await merge_finished.wait_call()

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    await utils.compare_db_with_expected(
        pgsql,
        [
            load_json('expected_driver_diagnostics_result.json')[
                driver_number - 1
            ],
        ],
        [
            'driver_id',
            'driver_diagnostics_updated_ts',
            'driver_diagnostics_reasons',
            'enabled_classes',
        ],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_diagnostics_ttl.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_driver_diagnostics_update_ttl(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        mockserver,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_SERVICE_REQUESTS': load_json(
                'service_requests.json',
            ),
        },
    )

    @mockserver.json_handler(
        '/driver-diagnostics/internal/'
        'driver-diagnostics/v1/common/restrictions',
    )
    def _driver_diagnostics(request):
        assert (
            request.query['park_id'] == 'dbid1'
            or request.query['park_id'] == 'dbid3'
        )
        assert (
            request.query['contractor_profile_id'] == 'uuid1'
            or request.query['contractor_profile_id'] == 'uuid3'
        )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_diagnostics_limit.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_driver_diagnostics_update_query_limit(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        mockserver,
        pgsql,
):
    driver_diagnostics_responses = load_json(
        'driver_diagnostics_responses.json',
    )

    @mockserver.json_handler(
        '/driver-diagnostics/internal/'
        'driver-diagnostics/v1/common/restrictions',
    )
    def _driver_diagnostics(request):
        dbid = request.query['park_id']
        uuid = request.query['contractor_profile_id']
        return driver_diagnostics_responses[f'{dbid}_{uuid}']

    config = load_json('service_requests.json')
    config['driver-diagnostics'][
        '/internal/driver-diagnostics/v1/common/restrictions'
    ]['update_query_limit'] = 1
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_SERVICE_REQUESTS': config,
        },
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    assert _driver_diagnostics.times_called == 1

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    assert _driver_diagnostics.times_called == 2

    await utils.compare_db_with_expected(
        pgsql,
        [
            {
                'driver_id': 'dbid1_uuid1',
                'driver_diagnostics_updated_ts': '2020-02-02T00:00:00+00:00',
            },
            {
                'driver_id': 'dbid2_uuid2',
                'driver_diagnostics_updated_ts': '2020-02-01T00:00:30+00:00',
            },
            {
                'driver_id': 'dbid3_uuid3',
                'driver_diagnostics_updated_ts': '2020-02-02T00:00:00+00:00',
            },
        ],
        ['driver_id', 'driver_diagnostics_updated_ts'],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_diagnostics_limit.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_driver_diagnostics_negative(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        taxi_config,
        load_json,
        mockserver,
):
    driver_diagnostics_responses = load_json(
        'driver_diagnostics_responses.json',
    )

    @mockserver.json_handler(
        '/driver-diagnostics/internal/'
        'driver-diagnostics/v1/common/restrictions',
    )
    def _driver_diagnostics(request):
        if request.query['park_id'] == 'dbid1':
            return {
                'code': 'INTERNAL_ERROR',
                'message': 'DRIVER_DIAGNOSTICS_ERROR',
            }
        dbid = request.query['park_id']
        uuid = request.query['contractor_profile_id']
        return driver_diagnostics_responses[f'{dbid}_{uuid}']

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_NOT_ALLOWED_TO_PARK_REASONS': (
                load_json('not_allowed_to_park_reasons.json')
            ),
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    await utils.compare_db_with_expected(
        pgsql,
        load_json('expected_negative_result.json'),
        [
            'driver_id',
            'driver_diagnostics_updated_ts',
            'driver_diagnostics_reasons',
            'enabled_classes',
        ],
    )
