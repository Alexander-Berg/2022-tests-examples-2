import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/device/vehicle-bindings'
PARK_ID = 'park_1'
HEADERS = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'park_1'}

FLEET_VEHICLES_RESPONSE_CAR_0 = {
    'vehicles': [
        {
            'data': {'car_id': 'car_0', 'number': 'О122КХ777'},
            'park_id_car_id': 'park_1_car_0',
            'revision': '0_1574328384_71',
        },
    ],
}

FLEET_VEHICLES_RESPONSE_CAR_4 = {
    'vehicles': [
        {
            'data': {'car_id': 'car_4', 'number': 'О228КХ777'},
            'park_id_car_id': 'park_1_car_4',
            'revision': '0_1574321114_71',
        },
    ],
}


def _make_car_bindings_snapshot(pgsql):
    fields = [
        'id',
        'park_id',
        'car_id',
        'device_id',
        'created_at',
        'detached_at',
        'updated_at',
    ]
    return [
        {k: v for (k, v) in zip(fields, binding)}
        for binding in utils.make_table_snapshot(
            pgsql, 'car_device_bindings', fields=fields, order_by='device_id',
        )
    ]


def _check_row_unbound(row):
    utils.assert_now(row['detached_at'])
    utils.assert_now(row['updated_at'])


def _raw_device_id_to_public_id(pgsql, raw_device_id):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT id '
        'FROM signal_device_api.devices '
        'WHERE public_id = \'{}\';'.format(raw_device_id),
    )
    return list(db)[0][0]


def _check_row_bound(row, pgsql, park_id, vehicle_id, device_id):
    assert not row['detached_at']
    assert row['park_id'] == park_id
    assert row['car_id'] == vehicle_id
    assert row['device_id'] == _raw_device_id_to_public_id(pgsql, device_id)


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'device_id',
    [
        'device_never_bound',
        'device_bound_to_previous_park_vehicle',
        'device_active_in_2_used_to_be_in_1',
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_unbind_200_not_bound(
        taxi_signal_device_api_admin, pgsql, device_id, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    snapshot_before = _make_car_bindings_snapshot(pgsql)
    device_id = 'device_never_bound'
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT, params={'device_id': device_id}, json={}, headers=HEADERS,
    )
    snapshot_after = _make_car_bindings_snapshot(pgsql)
    assert snapshot_after == snapshot_before
    assert response.status_code == 200, response.text
    assert response.json() == {'device_id': device_id}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_unbind_200_bound(
        taxi_signal_device_api_admin, pgsql, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    snapshot_before = _make_car_bindings_snapshot(pgsql)
    device_id = 'device_bound'
    for _ in range(2):  # idempotency
        response = await taxi_signal_device_api_admin.put(
            ENDPOINT,
            params={'device_id': device_id},
            json={},
            headers=HEADERS,
        )
        snapshot_after = _make_car_bindings_snapshot(pgsql)
        _check_row_unbound(snapshot_after[0])
        assert snapshot_before[1:] == snapshot_after[1:]
        assert response.status_code == 200, response.text
        assert response.json() == {'device_id': device_id}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize('device_id', ['no_such_device', 'device_active_in_2'])
@pytest.mark.config(TVM_ENABLED=True)
async def test_unbind_400(
        taxi_signal_device_api_admin, pgsql, device_id, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    snapshot_before = _make_car_bindings_snapshot(pgsql)
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT, params={'device_id': device_id}, json={}, headers=HEADERS,
    )
    snapshot_after = _make_car_bindings_snapshot(pgsql)
    assert snapshot_before == snapshot_after
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': f'Failed to find device_id {device_id}',
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'device_id, vehicle_id, expected_plate_number, '
    'expected_events_for_car_amount',
    [
        ('device_never_bound', 'car_0', 'О122КХ777', 2),
        ('device_unbound', 'car_4', 'О228КХ777', 2),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_bind_200_unbound_device(
        taxi_signal_device_api_admin,
        mockserver,
        pgsql,
        device_id,
        vehicle_id,
        expected_plate_number,
        expected_events_for_car_amount,
):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        if 'park_1_car_0' in request.json['id_in_set']:
            return FLEET_VEHICLES_RESPONSE_CAR_0
        return FLEET_VEHICLES_RESPONSE_CAR_4

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        params={'device_id': device_id},
        json={'vehicle_id': vehicle_id},
        headers=HEADERS,
    )
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT COUNT(*)'
        'FROM signal_device_api.events '
        f'WHERE car_id = \'{vehicle_id}\' AND '
        f'vehicle_plate_number = \'{expected_plate_number}\'',
    )
    car_events_number = list(db)
    assert car_events_number[0][0] == expected_events_for_car_amount
    db.execute(
        'SELECT created_at, detached_at, device_id '
        'FROM signal_device_api.car_device_bindings '
        f'WHERE car_id = \'{vehicle_id}\''
        ' ORDER BY created_at DESC LIMIT 1',
    )
    result = list(db)
    utils.assert_now(result[0][0])
    assert result[0][1] is None
    assert result[0][2] == _raw_device_id_to_public_id(pgsql, device_id)
    assert response.status_code == 200, response.text
    assert response.json() == {
        'device_id': device_id,
        'vehicle_id': vehicle_id,
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_bind_200_bound_device(
        taxi_signal_device_api_admin, mockserver, pgsql,
):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        if 'park_1_car_0' in request.json['id_in_set']:
            return FLEET_VEHICLES_RESPONSE_CAR_0
        return FLEET_VEHICLES_RESPONSE_CAR_4

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    snapshot_before = _make_car_bindings_snapshot(pgsql)
    device_id = 'device_bound'
    vehicle_id = 'car_0'
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        params={'device_id': device_id},
        json={'vehicle_id': vehicle_id},
        headers=HEADERS,
    )
    snapshot_after = _make_car_bindings_snapshot(pgsql)
    _check_row_unbound(snapshot_after[0])
    _check_row_bound(snapshot_after[1], pgsql, PARK_ID, vehicle_id, device_id)
    snapshot_after.pop(1)
    snapshot_before.pop(0)
    snapshot_after.pop(0)
    assert snapshot_before == snapshot_after
    assert response.status_code == 200, response.text
    assert response.json() == {
        'device_id': device_id,
        'vehicle_id': vehicle_id,
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_bind_200_bound_to_previous_park_vehicle(
        taxi_signal_device_api_admin, mockserver, pgsql,
):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        if 'park_1_car_0' in request.json['id_in_set']:
            return FLEET_VEHICLES_RESPONSE_CAR_0
        return FLEET_VEHICLES_RESPONSE_CAR_4

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    snapshot_before = _make_car_bindings_snapshot(pgsql)
    device_id = 'device_bound_to_previous_park_vehicle'
    vehicle_id = 'car_0'
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        params={'device_id': device_id},
        json={'vehicle_id': vehicle_id},
        headers=HEADERS,
    )
    snapshot_after = _make_car_bindings_snapshot(pgsql)
    _check_row_bound(snapshot_after[2], pgsql, PARK_ID, vehicle_id, device_id)
    snapshot_after.pop(2)
    assert snapshot_before == snapshot_after
    assert response.status_code == 200, response.text
    assert response.json() == {
        'device_id': device_id,
        'vehicle_id': vehicle_id,
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'device_id',
    [
        'no_such_device',
        'device_active_in_2',
        'device_active_in_2_used_to_be_in_1',
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_bind_400(
        taxi_signal_device_api_admin, pgsql, device_id, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    snapshot_before = _make_car_bindings_snapshot(pgsql)
    vehicle_id = 'car_1'
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        params={'device_id': device_id},
        json={'vehicle_id': vehicle_id},
        headers=HEADERS,
    )
    snapshot_after = _make_car_bindings_snapshot(pgsql)
    assert snapshot_before == snapshot_after
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': f'Failed to find device_id {device_id}',
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_bind_409(taxi_signal_device_api_admin, pgsql, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(HEADERS['X-Park-Id']),
                    'specifications': ['signalq'],
                },
            ],
        }

    snapshot_before = _make_car_bindings_snapshot(pgsql)
    vehicle_id = 'car_1'
    device_id = 'device_never_bound'
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        params={'device_id': device_id},
        json={'vehicle_id': vehicle_id},
        headers=HEADERS,
    )
    snapshot_after = _make_car_bindings_snapshot(pgsql)
    assert snapshot_before == snapshot_after
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': '409',
        'message': (
            f'Failed to bind device_id {device_id}, '
            f'vehicle_id {vehicle_id} is bound by another device'
        ),
    }
