import pytest

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.now('2022-01-01T00:00:00Z')
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_LIST_CARS={
        'enabled': True,
        'data_ttl': 300,
        'updated_parkings': ['parking_lot1'],
    },
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ADDITIONAL_PARKED_DRIVERS={
        'parking_lot1': [
            {'dbid_uuid': 'dbid_uuid_add1'},
            {
                'dbid_uuid': 'dbid_uuid_add2',
                'arrived_at': '2020-02-02T00:00:00+00:00',
            },
            # alredy used, should be skipped
            {
                'dbid_uuid': 'dbid_uuid1',
                'arrived_at': '1989-02-02T00:00:00+00:00',
            },
        ],
    },
)
@pytest.mark.parametrize('singtegro_works', ([True, False]))
async def test_v2_parked_drivers(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        mockserver,
        load_json,
        singtegro_works,
):
    list_cars_response = load_json('list_cars_response.json')

    @mockserver.json_handler(
        '/sintegro-list-cars/YANDEX_SH_D/hs/parkings/list_cars',
    )
    def _list_cars(request):
        if singtegro_works:
            return utils.form_list_cars_response(request, list_cars_response)

        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Not found'},
        )

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    response = await taxi_dispatch_airport_partner_protocol.post(
        '/service/v2/parked_drivers', {'parking_id': 'parking_lot1'},
    )
    assert response.status_code == 200
    etalon = load_json('expected_response.json')
    response = response.json()

    added_drivers = [d for d in response['drivers'] if 'add' in d['driver_id']]
    added_drivers.sort(key=lambda x: x['driver_id'])
    assert added_drivers == [
        {
            'arrived_at': '2022-01-01T00:00:00+00:00',
            'driver_id': 'dbid_uuid_add1',
        },
        {
            'arrived_at': '2020-02-02T00:00:00+00:00',
            'driver_id': 'dbid_uuid_add2',
        },
    ]

    response['drivers'] = [
        d for d in response['drivers'] if 'add' not in d['driver_id']
    ]
    if singtegro_works:
        response['drivers'].sort(key=lambda x: x['driver_id'])

        assert etalon == response
    else:
        assert response['drivers'] == [
            {
                'arrived_at': '1989-02-02T00:00:00+00:00',
                'driver_id': 'dbid_uuid1',
            },
        ]


async def test_negative(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    # bad request, parking not found
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/service/v2/parked_drivers', {'parking_id': 'not_existing_parking'},
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'PARKING_ZONE_NOT_FOUND'

    # no list-cars data for parking
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/service/v2/parked_drivers', {'parking_id': 'parking_lot1'},
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'NO_DATA_FOR_PARKING'
