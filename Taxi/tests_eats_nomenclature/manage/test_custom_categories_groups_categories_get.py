import pytest


HANDLER = '/v1/manage/custom_categories_groups/categories'
ADD_CUSTOM_CATEGORY_HANDLER = '/v1/manage/custom_categories_groups'
DEFAULT_SORT_ORDER = 100


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
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
    response = await taxi_eats_nomenclature.post(
        ADD_CUSTOM_CATEGORY_HANDLER, json=request_json,
    )
    assert response.status_code == 200
    group_public_id = response.json()['group_id']

    category_id_to_external_id = sql_get_cat_id_to_external_id(pgsql)

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

        # compare tags
        if 'tags' not in request_category:
            assert response_category['tags'] == []
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
