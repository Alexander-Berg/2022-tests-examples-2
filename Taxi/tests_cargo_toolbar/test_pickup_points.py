import pytest


@pytest.mark.now('2021-02-25T10:00:00')  # четверг
@pytest.mark.parametrize(
    'schedule, expected_title',
    [
        (
            {
                'restrictions': [
                    {
                        'days': [1, 2, 3, 4, 5, 6, 7],
                        'time_from': {'hours': 8, 'minutes': 0},
                        'time_to': {'hours': 21, 'minutes': 0},
                    },
                ],
                'time_zone': 0,
            },
            'Пункт выдачи, открыто до 21:00',
        ),
        (
            {
                'restrictions': [
                    {
                        'days': [1, 2, 3, 5, 6, 7],
                        'time_from': {'hours': 8, 'minutes': 0},
                        'time_to': {'hours': 9, 'minutes': 0},
                    },
                    {
                        'days': [4],
                        'time_from': {'hours': 8, 'minutes': 0},
                        'time_to': {'hours': 21, 'minutes': 0},
                    },
                ],
                'time_zone': 0,
            },
            'Пункт выдачи, открыто до 21:00',
        ),
        (
            {
                'restrictions': [
                    {
                        'days': [1, 2, 3, 5, 6, 7],
                        'time_from': {'hours': 8, 'minutes': 0},
                        'time_to': {'hours': 9, 'minutes': 0},
                    },
                ],
                'time_zone': 0,
            },
            'Пункт выдачи',
        ),
        (
            {
                'restrictions': [
                    {
                        'days': [1, 2, 3, 4, 5, 6, 7],
                        'time_from': {'hours': 11, 'minutes': 0},
                        'time_to': {'hours': 21, 'minutes': 0},
                    },
                ],
                'time_zone': 0,
            },
            'Пункт выдачи, закрыто до 11:00',
        ),
        (
            {
                'restrictions': [
                    {
                        'days': [1, 2, 3, 4, 6, 7],
                        'time_from': {'hours': 8, 'minutes': 0},
                        'time_to': {'hours': 9, 'minutes': 0},
                    },
                    {
                        'days': [5],
                        'time_from': {'hours': 11, 'minutes': 0},
                        'time_to': {'hours': 12, 'minutes': 0},
                    },
                ],
                'time_zone': 0,
            },
            'Пункт выдачи, закрыто до 11:00',
        ),
    ],
)
async def test_stations_schedule(
        taxi_cargo_toolbar,
        default_pa_headers,
        mockserver,
        schedule,
        expected_title,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/pickup-points/list',
    )
    def _list(request):
        assert request.json == {
            'available_for_dropoff': True,
            'geo_id': 123,
            'latitude': {'from': 55.75, 'to': 55.77},
            'longitude': {'from': 37.62, 'to': 37.64},
        }
        return {
            'points': [
                {
                    'address': {'full_address': 'address_1'},
                    'contact': {'phone': 'some_phone'},
                    'id': 'id_1',
                    'name': 'name_1',
                    'payment_methods': ['already_paid'],
                    'position': {'latitude': 55.75, 'longitude': 37.62},
                    'schedule': schedule,
                    'type': 'terminal',
                },
            ],
        }

    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/pickup-points/geo-search',
        json={
            'point': {'type': 'source', 'geo_id': 123},
            'search': {'type': 'bbox', 'bbox': [37.62, 55.75, 37.64, 55.77]},
        },
        headers=default_pa_headers('phone_pd_id'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'pickup_points': [
            {
                'coordinate': [37.62, 55.75],
                'id': 'id_1',
                'subtitle': expected_title,
                'title': 'address_1',
            },
        ],
    }


@pytest.mark.config(CARGO_TOOLBAR_PICKUP_POINTS_COUNT_LIMIT=1)
async def test_limit(taxi_cargo_toolbar, default_pa_headers, mockserver):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/pickup-points/list',
    )
    def _list(request):
        return {
            'points': [
                {
                    'address': {'full_address': 'address_1'},
                    'contact': {'phone': 'some_phone'},
                    'id': 'id_1',
                    'name': 'name_1',
                    'payment_methods': ['already_paid'],
                    'position': {'latitude': 55.75, 'longitude': 37.62},
                    'schedule': {'restrictions': [], 'time_zone': 0},
                    'type': 'terminal',
                },
                {
                    'address': {'full_address': 'address_2'},
                    'contact': {'phone': 'some_phone'},
                    'id': 'id_2',
                    'name': 'name_2',
                    'payment_methods': ['already_paid'],
                    'position': {'latitude': 55.75, 'longitude': 37.62},
                    'schedule': {'restrictions': [], 'time_zone': 0},
                    'type': 'terminal',
                },
            ],
        }

    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/pickup-points/geo-search',
        json={
            'point': {'type': 'source', 'geo_id': 123},
            'search': {'type': 'bbox', 'bbox': [37.62, 55.75, 37.64, 55.77]},
        },
        headers=default_pa_headers('phone_pd_id'),
    )
    assert response.status_code == 200
    assert response.json() == {'pickup_points': []}
