import pytest


TEST_PARAMS = [
    (
        {'query': {'park': {'ids': ['park_valid1']}}},
        {
            'parks_driver_hirings': [
                {
                    'park_id': 'park_valid1',
                    'commercial_hiring': False,
                    'commercial_hiring_with_car': True,
                    'park_phone': '88005553535',
                    'park_address': 'some nice street',
                    'park_email': 'nice_email@yandex.ru',
                },
            ],
        },
    ),
    (
        {'query': {'park': {'ids': ['park_valid2']}}},
        {
            'parks_driver_hirings': [
                {
                    'park_id': 'park_valid2',
                    'commercial_hiring': False,
                    'commercial_hiring_with_car': False,
                },
            ],
        },
    ),
    (
        {'query': {'park': {'ids': ['park_unknown']}}},
        {'parks_driver_hirings': []},
    ),
    (
        {
            'query': {
                'park': {
                    'ids': [
                        'park_driver_hiring_test_2',
                        'park_driver_hiring_test_1',
                    ],
                },
            },
        },
        {
            'parks_driver_hirings': [
                {
                    'park_id': 'park_driver_hiring_test_2',
                    'commercial_hiring': False,
                    'commercial_hiring_with_car': False,
                    'park_email': 'park_email',
                },
                {
                    'park_id': 'park_driver_hiring_test_1',
                    'commercial_hiring': True,
                    'commercial_hiring_with_car': False,
                },
            ],
        },
    ),
]


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize('payload, expected_response', TEST_PARAMS)
async def test_required_field(taxi_fleet_parks, payload, expected_response):
    response = await taxi_fleet_parks.post(
        'v1/parks/driver-hirings/list', json=payload,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    'city, expected_response',
    [
        ('Москва', {'types': []}),
        ('city5', {'types': []}),
        ('CitY2', {'types': ['lease', 'private']}),
        ('city600', {'types': ['lease', 'private']}),
    ],
)
async def test_hiring_types(taxi_fleet_parks, city, expected_response):
    response = await taxi_fleet_parks.get(
        'v1/parks/driver-hirings/selfreg/types', params={'city': city},
    )
    assert response.status_code == 200
    assert response.json() == expected_response
