import pytest

from testsuite.utils import ordered_object


async def test_countries(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.get('/admin/catalog/v1/countries')
    assert response.status_code == 200
    response = response.json()

    expected_result = {
        'countries': [
            {'country_id': 'ZAF', 'name': 'South Africa'},
            {'country_id': 'BLR', 'name': 'Belarus'},
            {'country_id': 'FRA', 'name': 'France'},
            {'country_id': 'ISR', 'name': 'Israel'},
            {'country_id': 'RUS', 'name': 'Russia'},
            {'country_id': 'GBR', 'name': 'Great Britain'},
            {'country_id': 'SAU', 'name': 'Saudi Arabia'},
        ],
    }
    ordered_object.assert_eq(response, expected_result, ['countries'])


@pytest.mark.parametrize('accept_language', ['ru', None])
async def test_cities(taxi_overlord_catalog, accept_language):
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/cities',
        params={'country_id': 'RUS'},
        headers={'Accept-Language': accept_language},
    )
    assert response.status_code == 200
    response = response.json()
    assert response == {'cities': [{'city_id': '213', 'name': 'Moscow'}]}


async def test_cities_invalid(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/cities', params={'country_id': 'bad'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'COUNTRY_NOT_FOUND'


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'catalog_wms_test_depots.sql'],
)
@pytest.mark.parametrize('region_id,part', [('12345', 'веты')])
async def test_suggest_categories_unknown_region(
        taxi_overlord_catalog, region_id, part,
):
    await taxi_overlord_catalog.invalidate_caches()

    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/suggest/categories',
        params={'region_id': region_id, 'part': part},
    )
    assert response.status_code == 404
