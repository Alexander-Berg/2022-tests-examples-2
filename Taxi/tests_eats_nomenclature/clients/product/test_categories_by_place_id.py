import pytest

HANDLER = '/v1/product/categories'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_unknown_place(taxi_eats_nomenclature):
    place_id = 100
    request = _generate_request_from_origin_ids(
        [('item_origin_1', 30), ('item_origin_2', 5), ('item_origin_7', 5)],
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}&include_custom_categories=false',
        json=request,
    )
    assert response.status == 404


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_categories_without_custom(taxi_eats_nomenclature, load_json):
    place_id = 1
    request = _generate_request_from_origin_ids(
        [
            ('item_origin_1', 30),
            ('item_origin_2', 5),
            ('item_origin_7', 5),
            ('item_origin_10', 5),
        ],
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}&include_custom_categories=false',
        json=request,
    )
    assert response.status == 200

    assert sort_response(response.json()) == sort_response(
        load_json('categories_without_custom_response.json'),
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_categories_with_custom(taxi_eats_nomenclature, load_json):
    place_id = 1
    request = _generate_request_from_origin_ids(
        [
            ('item_origin_1', 30),
            ('item_origin_2', 5),
            ('item_origin_7', 5),
            ('item_origin_10', 5),
        ],
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}&include_custom_categories=true',
        json=request,
    )
    assert response.status == 200

    assert sort_response(response.json()) == sort_response(
        load_json('categories_with_custom_response.json'),
    )


@pytest.mark.parametrize(
    'get_default_assortment_from, trait_id, assortment_id',
    [
        ('place_default_assortments', 1, 1),
        ('brand_default_assortments', 2, 2),
        (None, None, 3),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_default_assortment(
        taxi_eats_nomenclature,
        testpoint,
        sql_del_default_assortments,
        sql_set_place_default_assortment,
        sql_set_brand_default_assortment,
        get_default_assortment_from,
        trait_id,
        assortment_id,
):
    sql_del_default_assortments()
    if get_default_assortment_from == 'place_default_assortments':
        sql_set_place_default_assortment(trait_id=trait_id)
    elif get_default_assortment_from == 'brand_default_assortments':
        sql_set_brand_default_assortment(trait_id=trait_id)

    place_id = 1
    request = _generate_request_from_origin_ids(
        [
            ('item_origin_1', 30),
            ('item_origin_2', 5),
            ('item_origin_7', 5),
            ('item_origin_10', 5),
        ],
    )

    @testpoint('v1-product-categories-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == assortment_id

    await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}&include_custom_categories=true',
        json=request,
    )

    assert _assortment.has_calls


def _generate_request_from_origin_ids(origin_ids):
    return {'products': [{'origin_id': i[0]} for i in origin_ids]}


def sort_response(response):
    response['categories'].sort(key=lambda category: category['public_id'])
    response['products'].sort(key=lambda category: category['origin_id'])
    return response
