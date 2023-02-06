import pytest


HANDLER = '/v1/manage/custom_categories_groups'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_404_unknown_products(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    # Add unknown products to request.
    unknown_products = [
        '12345678-1234-1234-1234-123456789012',
        '87654321-4321-4321-4321-210987654321',
    ]
    request['categories'][0]['product_ids'] += unknown_products

    response = await taxi_eats_nomenclature.post(HANDLER, json=request)

    assert response.status_code == 404
    assert set(response.json()['product_ids']) == {
        '12345678-1234-1234-1234-123456789012',
        '87654321-4321-4321-4321-210987654321',
    }


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_404_unknown_product_types(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    # Add unknown product types to request.
    unknown_product_types = ['unknown_product_type1', 'unknown_product_type2']
    request['categories'][0]['product_type_ids'] += unknown_product_types

    response = await taxi_eats_nomenclature.post(HANDLER, json=request)

    assert response.status_code == 404
    assert set(response.json()['product_type_ids']) == {
        'unknown_product_type1',
        'unknown_product_type2',
    }


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_400(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    # Add unknown parent category.
    unknown_category = {'name': 'Неизвестная категория'}
    request['categories'][0]['parents'] += unknown_category

    response = await taxi_eats_nomenclature.post(HANDLER, json=request)

    assert response.status_code == 400


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_root_category_without_picture(
        taxi_eats_nomenclature, load_json,
):
    request = load_json('request.json')
    for category in request['categories']:
        if not category['parents']:
            category['image'] = []
            break

    response = await taxi_eats_nomenclature.post(HANDLER, json=request)
    assert response.status_code == 400


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_200(taxi_eats_nomenclature, load_json, sql_get_group_public_id):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json=load_json('request.json'),
    )
    assert response.status_code == 200
    assert response.json()['group_id'] == sql_get_group_public_id()
