import pytest


HANDLER = '/v1/manage/brands'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brands_retailers.sql'])
async def test_brands(taxi_eats_nomenclature, mockserver, load_json, pgsql):
    response = await taxi_eats_nomenclature.get(HANDLER)
    assert response.status_code == 200
    expected_result = {
        'brands': [
            {
                'brand_id': 777,
                'is_enabled': True,
                'retailer_name': 'Замечательный',
                'retailer_slug': 'zamechatelniy',
            },
            {'brand_id': 778, 'is_enabled': False},
            {'brand_id': 779, 'is_enabled': False},
        ],
    }
    assert response.json() == expected_result


@pytest.mark.pgsql('eats_nomenclature')
async def test_brands_empty(
        taxi_eats_nomenclature, mockserver, load_json, pgsql,
):
    response = await taxi_eats_nomenclature.get(HANDLER)
    assert response.status_code == 200
    assert response.json() == {'brands': []}
