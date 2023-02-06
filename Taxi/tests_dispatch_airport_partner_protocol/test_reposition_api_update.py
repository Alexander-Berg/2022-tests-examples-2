# pylint: disable=import-error
import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_reposition_api.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_reposition_api_update(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
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

    @mockserver.json_handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition_api(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() is None
        request_drivers = []
        for i in range(request.DriversLength()):
            driver = request.Drivers(i)
            dbid = driver.ParkDbId().decode()
            uuid = driver.DriverProfileId().decode()
            request_drivers.append(f'{dbid}_{uuid}')
        assert sorted(request_drivers) == [
            'dbid1_uuid1',
            'dbid3_uuid3',
            'dbid4_uuid4',
            'dbid5_uuid5',
        ]
        drivers = [
            {'dbid': 'dbid1', 'uuid': 'uuid1'},
            {'dbid': 'dbid2', 'uuid': 'uuid2'},
            {'dbid': 'dbid3', 'uuid': 'uuid3'},
        ]

        return mockserver.make_response(
            response=utils.form_reposition_api_response(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )

    expected_result = [
        {
            'driver_id': 'dbid1_uuid1',
            'has_reposition': True,
            'reposition_api_updated_ts': '2020-02-02T00:00:00+00:00',
        },
        {
            'driver_id': 'dbid2_uuid2',
            'has_reposition': True,
            'reposition_api_updated_ts': '2020-02-02T00:00:00+00:00',
        },
        {
            'driver_id': 'dbid3_uuid3',
            'has_reposition': True,
            'reposition_api_updated_ts': '2020-02-02T00:00:00+00:00',
        },
        {
            'driver_id': 'dbid4_uuid4',
            'has_reposition': False,
            'reposition_api_updated_ts': '2020-02-02T00:00:00+00:00',
        },
        {
            'driver_id': 'dbid5_uuid5',
            'has_reposition': False,
            'reposition_api_updated_ts': '2020-02-02T00:00:00+00:00',
        },
    ]

    await utils.compare_db_with_expected(
        pgsql,
        expected_result,
        ['driver_id', 'has_reposition', 'reposition_api_updated_ts'],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_reposition_api_ttl.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_reposition_api_update_ttl(
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

    @mockserver.json_handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition_api(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        request_drivers = []
        for i in range(request.DriversLength()):
            driver = request.Drivers(i)
            dbid = driver.ParkDbId().decode()
            uuid = driver.DriverProfileId().decode()
            request_drivers.append(f'{dbid}_{uuid}')
        assert sorted(request_drivers) == ['dbid1_uuid1', 'dbid3_uuid3']

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_reposition_api_limit.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_reposition_api_update_query_limit(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        mockserver,
        pgsql,
):
    @mockserver.json_handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition_api(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.DriversLength() == 1
        drivers = [
            {'dbid': 'dbid1', 'uuid': 'uuid1'},
            {'dbid': 'dbid2', 'uuid': 'uuid2'},
            {'dbid': 'dbid3', 'uuid': 'uuid3'},
        ]

        return mockserver.make_response(
            response=utils.form_reposition_api_response(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    config = load_json('service_requests.json')
    config['reposition-api']['/v1/service/airport_queue/state'][
        'update_query_limit'
    ] = 1
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
    assert _reposition_api.times_called == 1

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    assert _reposition_api.times_called == 2

    expected_result = [
        {
            'driver_id': 'dbid1_uuid1',
            'reposition_api_updated_ts': '2020-02-02T00:00:00+00:00',
        },
        {
            'driver_id': 'dbid2_uuid2',
            'reposition_api_updated_ts': '2020-02-01T00:00:30+00:00',
        },
        {
            'driver_id': 'dbid3_uuid3',
            'reposition_api_updated_ts': '2020-02-02T00:00:00+00:00',
        },
    ]

    await utils.compare_db_with_expected(
        pgsql, expected_result, ['driver_id', 'reposition_api_updated_ts'],
    )
