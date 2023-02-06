import pytest


@pytest.mark.eats_plus_regions_cache(
    [
        {
            'id': 1111,
            'name': 'Moscow',
            'slug': 'moscow',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [11.1111, 11.1111, 22.2222, 22.2222],
            'center': [12.3456, 12.3456],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [213, 216],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 2222,
            'name': 'SPB',
            'slug': 'spb',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [1.000, 1.000, 3.000, 3.000],
            'center': [2.000, 2.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [321, 911],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 3333,
            'name': 'EKB',
            'slug': 'ekb',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [70.000, 70.000, 80.000, 80.000],
            'center': [75.000, 75.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [1, 2],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 112233,
            'name': 'KZN',
            'slug': 'kzn',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [80.000, 80.000, 100.000, 100.000],
            'center': [90.000, 90.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [1, 2],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
    ],
)
@pytest.mark.parametrize(
    ['query_request', 'expected_response'],
    [
        ({'latitude': 0.5, 'longitude': 0.5}, False),
        ({'latitude': 2.000, 'longitude': 2.000}, True),
        ({'latitude': 75.000, 'longitude': 75.000}, True),
        ({'latitude': 90.000, 'longitude': 90.000}, False),
        ({'latitude': 123.321, 'longitude': 111.000}, False),
        ({'region_id': '333'}, True),
        ({'region_id': '567'}, False),
        ({'latitude': 2.750, 'longitude': 3.000, 'region_id': '2222'}, True),
        ({'latitude': 85.0, 'longitude': 85.0, 'region_id': '112233'}, False),
    ],
)
@pytest.mark.experiments3(filename='exp3_eats_plus_check_geozone.json')
async def test_plus_availability_handler(
        taxi_eats_plus,
        query_request,
        expected_response,
        eats_plus_regions_cache,
):

    response = await taxi_eats_plus.get(
        '/internal/eats-plus/v1/plus_availability', params=query_request,
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {'is_available': expected_response}
