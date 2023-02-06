import pytest


HANDLER = '/v1/gateway/brand_custom_categories_groups'
BRAND_ID = 777
ASSORTMENT_NAME = 'test_1'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_404_unknown_products(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    # Add unknown products to request.
    unknown_products = [
        '12345678-1234-1234-1234-123456789012',
        '87654321-4321-4321-4321-210987654321',
    ]
    request['categories'][0]['product_ids'] += unknown_products

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=request,
    )

    assert response.status_code == 404
    assert set(response.json()['product_ids']) == {
        '12345678-1234-1234-1234-123456789012',
        '87654321-4321-4321-4321-210987654321',
    }
    assert response.json()['product_type_ids'] == []
    assert response.json()['tags'] == []


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_404_unknown_product_types(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    # Add unknown product types to request.
    unknown_product_types = ['unknown_product_type1', 'unknown_product_type2']
    request['categories'][0]['product_type_ids'] += unknown_product_types

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=request,
    )

    assert response.status_code == 404
    assert set(response.json()['product_type_ids']) == {
        'unknown_product_type1',
        'unknown_product_type2',
    }
    assert response.json()['tags'] == []
    assert response.json()['product_ids'] == []


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_404_unknown_tags(taxi_eats_nomenclature, load_json):
    request = load_json('request_with_tags.json')
    # Add unknown tags to request.
    unknown_tags = ['unknown_tag1', 'unknown_tag2']
    request['categories'][0]['tags'] += unknown_tags

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=request,
    )

    assert response.status_code == 404
    assert set(response.json()['tags']) == set(unknown_tags)
    assert response.json()['product_ids'] == []
    assert response.json()['product_type_ids'] == []


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_404_unknown_assortment_name(taxi_eats_nomenclature, load_json):
    unknown_assortment_name = 'UNKNOWN_ASSORTMENT_NAME'

    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={unknown_assortment_name}',
        json=load_json('request.json'),
    )
    assert response.status_code == 404


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_404_no_default_assortment(
        taxi_eats_nomenclature, load_json, sql_remove_default_assortment_trait,
):
    sql_remove_default_assortment_trait(BRAND_ID)

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=load_json('request.json'),
    )
    assert response.status_code == 404


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_400(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    # Add unknown parent category.
    unknown_category = {'name': 'Неизвестная категория'}
    request['categories'][0]['parents'] += unknown_category

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=request,
    )

    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_root_category_without_picture(
        taxi_eats_nomenclature, load_json,
):
    request = load_json('request.json')
    for category in request['categories']:
        if not category['parents']:
            category['image'] = []
            break

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=request,
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_404_unknown_brand(taxi_eats_nomenclature, load_json):
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={99999}', json=load_json('request.json'),
    )
    assert response.status_code == 404


@pytest.mark.parametrize('mark_added_category_as_base', [True, False])
@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize('mark_added_category_as_restaurant', [True, False])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_products.sql', 'fill_assortment_traits.sql', 'fill_tags.sql'],
)
async def test_200(
        load_json,
        pgsql,
        sql_get_assortment_trait_id,
        sql_get_group,
        taxi_eats_nomenclature,
        # parametrize
        mark_added_category_as_base,
        use_assortment_name,
        mark_added_category_as_restaurant,
):
    sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )
    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    request = load_json('request_with_tags.json')
    request['is_base'] = mark_added_category_as_base
    request['is_restaurant'] = mark_added_category_as_restaurant
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' + assortment_query, json=request,
    )
    assert response.status_code == 200
    assert response.json()['group_id'] == sql_get_group_public_id(pgsql)
    (
        _,
        group_name,
        group_description,
        is_base,
        is_restaurant,
    ) = sql_get_group()
    assert (group_name, group_description, is_base, is_restaurant) == (
        'Группа категорий',
        'Описание группы категорий',
        mark_added_category_as_base,
        mark_added_category_as_restaurant,
    )

    expected_categories_tags = [
        ('Молоко', 'Тег 1'),
        ('Молочные продукты', 'Тег 1'),
        ('Молочные продукты', 'Тег 2'),
        ('Молоко и сыры', 'Тег 2'),
        ('Фрукты', 'Тег 1'),
    ]
    expected_categories_tags.sort(key=lambda item: (item[0], item[1]))
    assert sql_get_custom_categories_tags(pgsql) == expected_categories_tags


def sql_get_group_public_id(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select public_id
        from eats_nomenclature.custom_categories_groups
        """,
    )
    return list(cursor)[0][0]


def sql_get_custom_categories_tags(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select cc.name, tags.name
        from eats_nomenclature.custom_category_tags cct
        join eats_nomenclature.custom_categories cc
            on cc.id = cct.custom_category_id
        join eats_nomenclature.tags tags
            on tags.id = cct.tag_id
        """,
    )
    return sorted(cursor.fetchall(), key=lambda item: (item[0], item[1]))
