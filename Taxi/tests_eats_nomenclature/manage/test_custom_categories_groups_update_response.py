import pytest


ADD_GROUP_HANDLER = '/v1/manage/custom_categories_groups'
UPDATE_GROUP_HANDLER = '/v1/manage/custom_categories_groups/update'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_404_unknown_products(
        taxi_eats_nomenclature, load_json, sql_get_group_public_id,
):
    # Add custom categories group.
    request = load_json('request.json')
    response = await taxi_eats_nomenclature.post(
        ADD_GROUP_HANDLER, json=request,
    )
    added_group_id = sql_get_group_public_id()

    # Add unknown products to request.
    unknown_products = [
        '12345678-1234-1234-1234-123456789012',
        '87654321-4321-4321-4321-210987654321',
    ]
    request['categories'][0]['product_ids'] += unknown_products

    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER + f'?custom_categories_group_id={added_group_id}',
        json=request,
    )

    assert response.status_code == 404
    assert set(response.json()['product_ids']) == {
        '12345678-1234-1234-1234-123456789012',
        '87654321-4321-4321-4321-210987654321',
    }
    assert response.json()['tags'] == []
    assert response.json()['product_type_ids'] == []


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_404_unknown_product_types(
        taxi_eats_nomenclature, load_json, sql_get_group_public_id,
):
    # Add custom categories group.
    request = load_json('request.json')
    response = await taxi_eats_nomenclature.post(
        ADD_GROUP_HANDLER, json=request,
    )
    added_group_id = sql_get_group_public_id()

    # Add unknown product types to request.
    unknown_product_types = ['unknown_product_type1', 'unknown_product_type2']
    request['categories'][0]['product_type_ids'] += unknown_product_types

    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER + f'?custom_categories_group_id={added_group_id}',
        json=request,
    )

    assert response.status_code == 404
    assert set(response.json()['product_type_ids']) == {
        'unknown_product_type1',
        'unknown_product_type2',
    }
    assert response.json()['product_ids'] == []
    assert response.json()['tags'] == []


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_404_unknown_tags(
        taxi_eats_nomenclature, load_json, sql_get_group_public_id,
):
    # Add custom categories group.
    request = load_json('request_with_tags.json')
    response = await taxi_eats_nomenclature.post(
        ADD_GROUP_HANDLER, json=request,
    )
    added_group_id = sql_get_group_public_id()

    # Add unknown tags to request.
    unknown_tags = ['unknown_tag1', 'unknown_tag2']
    request['categories'][0]['tags'] += unknown_tags

    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER + f'?custom_categories_group_id={added_group_id}',
        json=request,
    )

    assert response.status_code == 404
    assert set(response.json()['tags']) == set(unknown_tags)
    assert response.json()['product_ids'] == []
    assert response.json()['product_type_ids'] == []


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_404_unknown_group(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    unknown_group_id = '11111111-1111-1111-1111-111111111111'
    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER
        + f'?custom_categories_group_id={unknown_group_id}',
        json=request,
    )

    assert response.status_code == 404
    assert (
        response.json()['message']
        == f'Custom categories group {unknown_group_id} is not found'
    )


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_400(taxi_eats_nomenclature, load_json, sql_get_group_public_id):
    # Add custom categories group.
    request = load_json('request.json')
    response = await taxi_eats_nomenclature.post(
        ADD_GROUP_HANDLER, json=request,
    )
    added_group_id = sql_get_group_public_id()

    # Add unknown parent category.
    unknown_category = {'name': 'Неизвестная категория'}
    request['categories'][0]['parents'] += unknown_category

    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER + f'?custom_categories_group_id={added_group_id}',
        json=request,
    )

    assert response.status_code == 400


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_root_category_without_picture(
        taxi_eats_nomenclature, load_json, sql_get_group_public_id,
):
    # Add custom categories group.
    request = load_json('request.json')
    response = await taxi_eats_nomenclature.post(
        ADD_GROUP_HANDLER, json=request,
    )
    added_group_id = sql_get_group_public_id()

    request = load_json('request.json')
    for category in request['categories']:
        if not category['parents']:
            category['image'] = []
            break

    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER + f'?custom_categories_group_id={added_group_id}',
        json=request,
    )
    assert response.status_code == 400
