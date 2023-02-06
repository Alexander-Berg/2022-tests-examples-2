import pytest

import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils

PLACE_SLUG = 'slug'
CATEGORY_ID = 'category_1_origin'


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature(
        taxi_eats_nomenclature,
        load_json,
        # parametrize
        should_include_pennies_in_price,
):
    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
    )

    assert response.status == 200

    expected_response = _sorted_response(load_json('response.json'))

    if not should_include_pennies_in_price:
        for category in expected_response['categories']:
            pennies_utils.rounded_price(category, 'items')

    assert _sorted_response(response.json()) == expected_response


@pytest.mark.parametrize(
    'get_default_assortment_from, trait_id, assortment_id',
    [
        ('place_default_assortments', 1, 1),
        ('brand_default_assortments', 2, 3),
        (None, None, 4),
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

    @testpoint('v1-nomenclature-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == assortment_id

    await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
    )

    assert _assortment.has_calls


@pytest.mark.parametrize(
    'experiment_on, experiment_assortment_name, expected_assortment_id',
    [
        (False, None, 1),
        (True, 'experiment_assortment_name', 5),
        (True, 'unknown_experiment_assortment_name', 1),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_assortment_name_experiment(
        taxi_eats_nomenclature,
        testpoint,
        set_assortment_name_exp,
        # parametrize
        experiment_on,
        experiment_assortment_name,
        expected_assortment_id,
):
    set_assortment_name_exp(experiment_on, experiment_assortment_name)

    @testpoint('v1-nomenclature-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == expected_assortment_id

    await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
        headers={'x-device-id': 'device_id'},
    )

    assert _assortment.has_calls


@pytest.mark.parametrize(
    'exp_brand_ids, exp_excluded_place_ids, expected_assortment_id',
    [
        pytest.param([1], [], 5, id='exp assortment'),
        pytest.param(
            [1], [1], 1, id='default assortment: place in excluded places',
        ),
        pytest.param(
            [2], [], 1, id='default assortment: brand not in exp brands',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_assortment_name_exp_brand_and_place(
        taxi_eats_nomenclature,
        testpoint,
        set_assortment_name_exp,
        # parametrize
        exp_brand_ids,
        exp_excluded_place_ids,
        expected_assortment_id,
):
    set_assortment_name_exp(
        experiment_on=True,
        assortment_name='experiment_assortment_name',
        brand_ids=exp_brand_ids,
        excluded_place_ids=exp_excluded_place_ids,
    )

    @testpoint('v1-nomenclature-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == expected_assortment_id

    await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
        headers={'x-device-id': 'device_id'},
    )

    assert _assortment.has_calls


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_pictures_for_product.sql',
    ],  # add extra file to check pictures sort order for products
)
async def test_get_nomenclature_sorted_pictures(taxi_eats_nomenclature):

    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
    )

    sorted_response = _sorted_response(response.json())
    sorted_images_1 = sorted(
        sorted_response['categories'][0]['items'][0]['images'],
        key=lambda image: image['sort_order'],
        reverse=True,
    )
    sorted_images_2 = sorted(
        sorted_response['categories'][0]['items'][1]['images'],
        key=lambda image: image['sort_order'],
        reverse=True,
    )
    sorted_images_3 = sorted(
        sorted_response['categories'][0]['items'][2]['images'],
        key=lambda image: image['sort_order'],
        reverse=True,
    )

    assert response.status == 200
    assert not sorted_images_1
    assert sorted_images_2[0] == {
        'hash': '3',
        'url': 'processed_url_3',
        'sort_order': 2,
    }
    assert sorted_images_2[1] == {
        'hash': '1',
        'url': 'processed_url_1',
        'sort_order': 1,
    }
    assert len(sorted_images_2) == 2
    assert sorted_images_3[0] == {
        'hash': '3',
        'url': 'processed_url_3',
        'sort_order': 2,
    }
    assert sorted_images_3[1] == {
        'hash': '1',
        'url': 'processed_url_1',
        'sort_order': 1,
    }
    assert len(sorted_images_3) == 2


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_pictures_for_categories.sql',
    ],
)
async def test_categories_pictures_sort_order(taxi_eats_nomenclature):

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
    )

    sorted_response = _sorted_response(response.json())
    sorted_images_1 = sorted(
        sorted_response['categories'][0]['images'],
        key=lambda image: image['sort_order'],
    )
    sorted_images_2 = sorted(
        sorted_response['categories'][1]['images'],
        key=lambda image: image['sort_order'],
    )

    assert response.status == 200
    assert sorted_images_1 == [
        {'hash': '3', 'url': 'processed_url_3', 'sort_order': 0},
        {'hash': '1', 'url': 'processed_url_1', 'sort_order': 1},
    ]
    assert sorted_images_2 == [
        {'hash': '3', 'url': 'processed_url_3', 'sort_order': 0},
        {'hash': '1', 'url': 'processed_url_1', 'sort_order': 1},
    ]


def _sorted_response(response):
    response['categories'].sort(key=lambda category: category['id'])
    for category in response['categories']:
        category['items'].sort(key=lambda item: item['id'])
    return response
