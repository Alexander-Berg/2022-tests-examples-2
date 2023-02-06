import pytest


HANDLER = '/v1/manage/custom_categories_groups'
DEFAULT_SORT_ORDER = 100


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_products.sql', 'fill_additional_data.sql', 'fill_tags.sql'],
)
@pytest.mark.parametrize('make_category_restaurant', [True, False])
async def test_200(
        taxi_eats_nomenclature,
        load_json,
        pgsql,
        # parametrize
        make_category_restaurant,
):
    request_json = load_json('request.json')
    request_json['is_restaurant'] = make_category_restaurant

    response = await taxi_eats_nomenclature.post(HANDLER, json=request_json)
    assert response.status_code == 200
    group_public_id = response.json()['group_id']

    category_id_to_external_id = sql_get_cat_id_to_external_id(pgsql)

    product_types_id_to_name = sql_get_product_types(pgsql)
    sql_products = sql_get_products(pgsql)

    response = await taxi_eats_nomenclature.get(
        f'{HANDLER}?public_id={group_public_id}',
    )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json['group_name'] == request_json['group_name']
    assert response_json['description'] == request_json['description']
    assert response_json['is_base'] == request_json['is_base']
    assert response_json['is_restaurant'] == request_json['is_restaurant']

    request_categories = {
        category['external_id']: category
        for category in request_json['categories']
    }
    assert (
        set(row['external_id'] for row in response_json['categories'])
        == request_categories.keys()
    )
    for response_category in response_json['categories']:
        request_category = request_categories[response_category['external_id']]

        # compare main fields
        assert_response_equals_request(
            response_category,
            request_category,
            ['name', 'description', 'sort_order'],
        )

        response_parents = [
            category_id_to_external_id[parent_id]
            for parent_id in response_category['parents']
        ]
        request_parents = [
            parent['external_id'] for parent in request_category['parents']
        ]
        assert set(response_parents) == set(request_parents)

        # compare pictures
        assert ('image' in request_category) == ('image' in response_category)
        if 'image' in request_category:
            assert (
                request_category['image']['url']
                == response_category['image']['url']
            )

        # compare product types
        response_product_types = [
            row['id'] for row in response_category['product_types']
        ]
        request_product_types = request_category['product_type_ids']
        assert set(response_product_types) == set(request_product_types)
        for response_product_type in response_category['product_types']:
            assert (
                response_product_type['name']
                == product_types_id_to_name[response_product_type['id']]
            )

        # compare products
        request_products = request_category['product_ids']
        assert set(row['id'] for row in response_category['products']) == set(
            request_products,
        )
        for response_product in response_category['products']:
            assert_response_equals_request(
                response_product,
                sql_products[response_product['id']],
                ['id', 'name', 'picture_url', 'measure', 'origin_id'],
            )

        # compare tags
        if 'tags' not in request_category:
            assert 'tags' not in response_category
        else:
            response_tags = response_category['tags']
            request_tags = request_category['tags']
            assert set(response_tags) == set(request_tags)


async def test_400(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.get(f'{HANDLER}?public_id=123')
    assert response.status_code == 400


async def test_404(taxi_eats_nomenclature):
    unknown_public_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    response = await taxi_eats_nomenclature.get(
        f'{HANDLER}?public_id={unknown_public_id}',
    )
    assert response.status_code == 404


def assert_response_equals_request(
        response_entity, request_entity, fields_to_compare,
):
    for field in fields_to_compare:
        if field in request_entity and request_entity[field] is not None:
            assert response_entity[field] == request_entity[field]
        elif field == 'sort_order':
            assert response_entity[field] == DEFAULT_SORT_ORDER
        elif field == 'description':
            assert response_entity[field] == ''
        else:
            assert field not in response_entity


def sql_get_cat_id_to_external_id(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id, external_id
        from eats_nomenclature.custom_categories
        """,
    )
    return {row[0]: row[1] for row in list(cursor)}


def sql_get_picture_url_mapping(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select url, processed_url
        from eats_nomenclature.pictures
        """,
    )
    return {row[0]: row[1] for row in list(cursor)}


def sql_get_product_types(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select value_uuid, value
        from eats_nomenclature.product_types
        """,
    )
    return {row[0]: row[1] for row in list(cursor)}


def sql_get_products(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select
            p.id,
            p.public_id::text,
            p.name,
            pic.processed_url,
            mu.name,
            p.measure_value,
            p.quantum,
            p.origin_id
        from eats_nomenclature.products p
        left join eats_nomenclature.product_pictures pp
            on p.id = pp.product_id
        left join eats_nomenclature.pictures pic
            on pp.picture_id = pic.id
        left join eats_nomenclature.measure_units mu
            on p.measure_unit_id = mu.id
        """,
    )
    return {
        row[1]: {
            'id': row[1],
            'name': row[2],
            'picture_url': sql_get_product_picture(pgsql, row[0]),
            'measure': (
                format_product_measure(row[4], row[5], row[6])
                if row[4]
                else None
            ),
            'origin_id': row[7],
        }
        for row in list(cursor)
    }


def sql_get_product_picture(pgsql, product_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select
            pic.processed_url
        from eats_nomenclature.product_pictures pp
        join eats_nomenclature.pictures pic
            on pp.picture_id = pic.id
        where pp.product_id = {product_id}
          and pic.processed_url is not null
        order by pp.updated_at desc
        """,
    )
    result = list(cursor)
    return result[0][0] if result else None


def format_product_measure(measure_unit, measure_value, quantum):
    if quantum > 0:
        measure_value = int(measure_value * quantum)
    return f'{measure_value} {measure_unit}'
