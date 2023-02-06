import http

import pytest


@pytest.mark.parametrize(
    'query, expected_data',
    (
        (
            {'locale': 'ru'},
            {
                'zones': [
                    {
                        'country': 'rus',
                        'name': 'moscow',
                        'time_zone': 'Europe/Moscow',
                        'translation': 'Москва',
                    },
                ],
            },
        ),
        (
            {'locale': 'ru', 'zone_names': 'moscow,unknown1'},
            {
                'zones': [
                    {
                        'country': 'rus',
                        'name': 'moscow',
                        'time_zone': 'Europe/Moscow',
                        'translation': 'Москва',
                    },
                ],
            },
        ),
        ({'locale': 'ru', 'zone_names': 'unknown1,unknown2'}, {'zones': []}),
        (
            {'locale': 'ru', 'updated_from': '1999-01-11T01:00:00'},
            {
                'zones': [
                    {
                        'country': 'rus',
                        'name': 'moscow',
                        'time_zone': 'Europe/Moscow',
                        'translation': 'Москва',
                    },
                ],
            },
        ),
        (
            {'locale': 'ru', 'updated_from': '2001-01-11T01:00:00'},
            {'zones': []},
        ),
        (
            {'locale': 'ru', 'updated_from': '1999-01-11T01:00:00'},
            {
                'zones': [
                    {
                        'country': 'rus',
                        'name': 'moscow',
                        'time_zone': 'Europe/Moscow',
                        'translation': 'Москва',
                    },
                ],
            },
        ),
        ({'locale': 'ru', 'date_from': '2001-01-11T01:00:00'}, {'zones': []}),
    ),
)
@pytest.mark.translations(
    geoareas={'moscow': {'ru': 'Москва'}, 'spb': {'ru': 'Санкт-Петербург'}},
)
async def test_get_tariff_zones_archive(
        taxi_tariffs_web, query, expected_data,
):
    response = await taxi_tariffs_web.get(
        '/v1/tariff_zones/archive/', params=query,
    )
    response_data = await response.json()
    assert response.status == http.HTTPStatus.OK, response_data
    assert response_data == expected_data
