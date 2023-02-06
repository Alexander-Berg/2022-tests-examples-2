import pytest

RUSSIA_ID = 'br_russia'


@pytest.mark.parametrize(
    ('locale', 'expected_countries', 'expected_agglomerations'),
    (
        pytest.param(
            'en',
            [
                {'id': 'br_kazakhstan', 'name': 'Kazakhstan'},
                {'id': RUSSIA_ID, 'name': 'Russia'},
            ],
            [{'id': 'br_moscow', 'name': 'Moscow'}],
            id='en',
        ),
        pytest.param(
            'ru',
            [
                {'id': 'br_kazakhstan', 'name': 'Казахстан'},
                {'id': RUSSIA_ID, 'name': 'Россия'},
            ],
            [{'id': 'br_moscow', 'name': 'Москва'}],
            id='ru',
        ),
    ),
)
async def test_geo_list(
        taxi_cargo_corp, locale, expected_countries, expected_agglomerations,
):
    country_response = await taxi_cargo_corp.get(
        'v1/geo/countries', headers={'Accept-Language': locale},
    )
    assert country_response.status_code == 200
    assert country_response.json()['countries'] == expected_countries

    agglo_response = await taxi_cargo_corp.get(
        'v1/geo/agglomerations',
        headers={'Accept-Language': locale, 'Country-Id': RUSSIA_ID},
    )

    assert agglo_response.status_code == 200
    assert agglo_response.json()['agglomerations'] == expected_agglomerations
