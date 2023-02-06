import datetime

import pytest


HANDLER = '/driver/v1/contractor-transport/v1/transport-active'
MOCK_NOW = '2021-04-01T00:00:00+00:00'


def get_auth_headers(park_id, driver_profile_id):
    return {
        'X-Remote-IP': '12.34.56.78',
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-YaTaxi-Park-Id': park_id,
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
        'User-Agent': 'Taximeter 9.40 (1234)',
    }


@pytest.mark.parametrize(
    'park_id, driver_id, expected_response',
    [
        ('park3', 'driver2', {'title': 'Транспорт', 'detail': 'Пеший'}),
        (
            'park3',
            'driver3',
            {'title': 'Транспорт', 'detail': 'number_normalized2'},
        ),
    ],
)
async def test_get_transport_active(
        taxi_contractor_transport, park_id, driver_id, expected_response,
):
    response = await taxi_contractor_transport.get(
        HANDLER, headers=get_auth_headers(park_id, driver_id),
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(
    CONTRACTORS_TRANSPORT_AVAILABLE={
        'taxi_walking_courier': ['pedestrian', 'bicycle'],
        'taxi': ['motorcycle', 'car'],
        'eda': ['bicycle'],
    },
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    (
        'park_id',
        'driver_id',
        'transport',
        'expected_code',
        'expected_detail',
        'profiles_response',
        'eats_updates_times_called',
        'the_same',
    ),
    [
        pytest.param(
            'park3',
            'driver2',
            {'type': 'bicycle'},
            200,
            'Велосипед',
            'profiles_courier.json',
            0,
            False,
            id='taxi courier -> bicycle',
        ),
        pytest.param(
            'park3',
            'driver2',
            {'type': 'electric_bicycle'},
            409,
            None,
            'profiles_courier.json',
            0,
            False,
            id='not allowed',
        ),
        pytest.param(
            'park3',
            'driver3',
            {'type': 'car', 'vehicle_id': '11'},
            200,
            'Автомобиль',
            'profiles_taxi.json',
            0,
            False,
            id='with car binding',
        ),
        pytest.param(
            'park3',
            'driver2',
            {'type': 'bicycle'},
            200,
            'Велосипед',
            'eats_courier.json',
            1,
            False,
            id='eats -> bicycle',
        ),
        pytest.param(
            'park3',
            'driver2',
            {'type': 'bicycle'},
            200,
            'Велосипед',
            'eats_courier.json',
            0,
            True,
            marks=pytest.mark.pgsql(
                'contractors_transport', files=['single_bicycle.sql'],
            ),
            id='the same',
        ),
    ],
)
async def test_post_transport_active(
        taxi_contractor_transport,
        park_id,
        driver_id,
        transport,
        expected_code,
        expected_detail,
        profiles_response,
        eats_updates_times_called,
        the_same,
        load_json,
        mockserver,
        stq,
        pgsql,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/proxy-retrieve',
    )
    def _driver_profiles(request):
        return load_json(profiles_response)

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    def _bind_car(request):
        return {}

    response = await taxi_contractor_transport.post(
        'internal/v1/transport-active',
        params={'contractor_id': park_id + '_' + driver_id},
        json=transport,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        if expected_detail == 'Автомобиль':
            assert _bind_car.times_called == 1
            return

        get_response = await taxi_contractor_transport.get(
            HANDLER, headers=get_auth_headers(park_id, driver_id),
        )
        assert get_response.json()['detail'] == expected_detail

    if expected_code == 409:
        assert response.json() == {
            'code': '409',
            'message': 'Transport not allowed for orders_provider',
        }

    assert (
        stq.contractor_transport_eats_update_event.times_called
        == eats_updates_times_called
    )
    if eats_updates_times_called:
        kwargs = stq.contractor_transport_eats_update_event.next_call()[
            'kwargs'
        ]
        assert kwargs['contractor_id'] == park_id + '_' + driver_id
        assert kwargs['updated_ts'] == MOCK_NOW
        assert kwargs['transport_type'] == transport['type']

    cursor = pgsql['contractors_transport'].cursor()
    cursor.execute(
        'SELECT updated_at FROM contractors_transport.transport_active',
    )
    result = list(cursor)

    if the_same:
        assert result[0][0] == datetime.datetime.fromisoformat(
            '2020-06-19T00:00:00+03:00',
        )
