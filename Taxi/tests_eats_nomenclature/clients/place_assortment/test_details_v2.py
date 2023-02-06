import pytest

import tests_eats_nomenclature.parametrize.displayed_stock_limits as stocks_utils  # noqa: E501 pylint: disable=line-too-long
import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils

HANDLER = '/v2/place/assortment/details'

PLACE_SLUG = 'slug'

REQUESTED_PRODUCTS = [
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '33333333-3333-3333-3333-333333333333',
    '44444444-4444-4444-4444-444444444444',
    '55555555-5555-5555-5555-555555555555',
    '66666666-6666-6666-6666-666666666666',
    '77777777-7777-7777-7777-777777777777',
    '88888888-8888-8888-8888-888888888888',
    '12345678-9123-4567-8999-999999999999',
]

REQUESTED_CATEGORIES = ['1', '2', '3', '4', '5', '6', '7', '8']
REQUESTED_CATEGORIES_PUBLIC_ID = ['1', '222', '3', '4', '5', '6', '7', '8']
REQUESTED_CATEGORIES_ORIGIN_ID = [
    'category_1_origin',
    'category_2_origin',
    'category_3_origin',
    'category_4_origin',
    'category_5_origin',
    'category_6_origin',
    'category_7_origin',
    'unknown_category',
]

AUTH_HEADERS = {'x-device-id': 'device_id'}


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_unknown_slug(taxi_eats_nomenclature):
    request = {
        'products': REQUESTED_PRODUCTS,
        'categories': REQUESTED_CATEGORIES,
    }
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=unknown_slug', json=request,
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'search_by_id_or_public_id, expected_categories',
    [
        (True, set()),
        (
            False,
            {
                'category_1_origin',
                'category_2_origin',
                'category_3_origin',
                'category_4_origin',
                'category_6_origin',
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_only_available_categories_origin_id(
        taxi_eats_nomenclature,
        update_taxi_config,
        search_by_id_or_public_id,
        expected_categories,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY',
        {'search_by_id_or_public_id': search_by_id_or_public_id},
    )

    request = {'products': [], 'categories': REQUESTED_CATEGORIES_ORIGIN_ID}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request,
    )

    assert response.status == 200
    assert (
        set(c['category_id'] for c in response.json()['categories'])
        == expected_categories
    )


@pytest.mark.parametrize(
    'search_by_id_or_public_id, request_categories, expected_categories',
    [
        (True, REQUESTED_CATEGORIES, {'1', '2', '3', '4', '6'}),
        (False, REQUESTED_CATEGORIES, {'1', '3', '4', '6'}),
        (True, REQUESTED_CATEGORIES_PUBLIC_ID, {'1', '222', '3', '4', '6'}),
        (False, REQUESTED_CATEGORIES_PUBLIC_ID, {'1', '222', '3', '4', '6'}),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_only_available_categories(
        taxi_eats_nomenclature,
        update_taxi_config,
        search_by_id_or_public_id,
        request_categories,
        expected_categories,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY',
        {'search_by_id_or_public_id': search_by_id_or_public_id},
    )

    request = {'products': [], 'categories': request_categories}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request,
    )

    assert response.status == 200
    assert (
        set(c['category_id'] for c in response.json()['categories'])
        == expected_categories
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_only_available_products_from_current_assortment(
        taxi_eats_nomenclature,
):
    request = {'products': REQUESTED_PRODUCTS, 'categories': []}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request,
    )

    expected_products = {
        '22222222-2222-2222-2222-222222222222',
        '33333333-3333-3333-3333-333333333333',
        '66666666-6666-6666-6666-666666666666',
        '12345678-9123-4567-8999-999999999999',
    }

    assert response.status == 200
    assert (
        set(p['product_id'] for p in response.json()['products'])
        == expected_products
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_all_products_from_current_assortment(taxi_eats_nomenclature):
    request = {'products': REQUESTED_PRODUCTS, 'categories': []}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}&include_unavailable=true', json=request,
    )

    expected_products = {
        '11111111-1111-1111-1111-111111111111',
        '22222222-2222-2222-2222-222222222222',
        '33333333-3333-3333-3333-333333333333',
        '44444444-4444-4444-4444-444444444444',
        '55555555-5555-5555-5555-555555555555',
        '66666666-6666-6666-6666-666666666666',
        '12345678-9123-4567-8999-999999999999',
    }

    assert response.status == 200
    assert (
        set(p['product_id'] for p in response.json()['products'])
        == expected_products
    )


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_response_content_origin_id(
        taxi_eats_nomenclature,
        load_json,
        # parametrize
        should_include_pennies_in_price,
):
    request = {
        'products': REQUESTED_PRODUCTS,
        'categories': REQUESTED_CATEGORIES_ORIGIN_ID,
    }
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request,
    )

    assert response.status == 200
    expected_response = load_json('details_response_origin_id.json')

    if not should_include_pennies_in_price:
        pennies_utils.rounded_price(expected_response, 'products')

    assert _sort_response(response.json()) == expected_response


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

    @testpoint('v2-place-assortment-details-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == assortment_id

    request = {
        'products': REQUESTED_PRODUCTS,
        'categories': REQUESTED_CATEGORIES_ORIGIN_ID,
    }
    await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request,
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
async def test_experiment(
        taxi_eats_nomenclature,
        testpoint,
        set_assortment_name_exp,
        # parametrize
        experiment_assortment_name,
        experiment_on,
        expected_assortment_id,
):
    set_assortment_name_exp(experiment_on, experiment_assortment_name)

    @testpoint('v2-place-assortment-details-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == expected_assortment_id

    request = {
        'products': REQUESTED_PRODUCTS,
        'categories': REQUESTED_CATEGORIES_ORIGIN_ID,
    }
    await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}',
        json=request,
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

    @testpoint('v2-place-assortment-details-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == expected_assortment_id

    request = {
        'products': REQUESTED_PRODUCTS,
        'categories': REQUESTED_CATEGORIES_ORIGIN_ID,
    }
    await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}',
        json=request,
        headers={'x-device-id': 'device_id'},
    )

    assert _assortment.has_calls


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.parametrize(
    'search_by_id_or_public_id, json_file, include_unavailable',
    [
        (True, 'details_response_search_by_id_or_public_id.json', False),
        (False, 'details_response.json', False),
        (False, 'details_response_with_unavailable.json', True),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_response_content(
        taxi_eats_nomenclature,
        update_taxi_config,
        load_json,
        should_include_pennies_in_price,
        search_by_id_or_public_id,
        json_file,
        include_unavailable,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY',
        {'search_by_id_or_public_id': search_by_id_or_public_id},
    )

    request = {
        'products': REQUESTED_PRODUCTS,
        'categories': REQUESTED_CATEGORIES,
    }
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}'
        + f'&include_unavailable={include_unavailable}',
        json=request,
    )

    assert response.status == 200
    expected_response = load_json(json_file)

    if not should_include_pennies_in_price:
        pennies_utils.rounded_price(expected_response, 'products')

    assert _sort_response(response.json()) == expected_response


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.parametrize(
    'is_retailer_name_used_for_concrete_sku_id', [True, False],
)
@pytest.mark.experiments3(filename='experiment_on.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql', 'fill_sku.sql'],
)
async def test_details_v2_with_sku_exp_on(
        taxi_eats_nomenclature,
        pgsql,
        load_json,
        should_include_pennies_in_price,
        is_retailer_name_used_for_concrete_sku_id,
):
    brand_id = 1
    sku_id = 2
    if is_retailer_name_used_for_concrete_sku_id:
        # set retailer name to sku picture, so we won't be able
        # to use this picture for REQUESTED_PRODUCTS, because for them
        # retailer name is null
        sql_set_retailer_name_of_sku(pgsql, sku_id)
    else:
        # add retailer and set it as retailer of brand
        retailer_id = 2
        sql_add_retailer_for_brand(pgsql, retailer_id, brand_id)

    await taxi_eats_nomenclature.invalidate_caches()
    request = {'products': REQUESTED_PRODUCTS, 'categories': []}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200
    expected_response = load_json('response_with_sku.json')
    if is_retailer_name_used_for_concrete_sku_id:
        # if we use retailer name to sku picture, we can use this picture
        # only with this retailer name, but for REQUESTED_PRODUCTS
        # retailer name is null
        expected_response['products'][sku_id]['images'] = []

    if not should_include_pennies_in_price:
        pennies_utils.rounded_price(expected_response, 'products')
    assert _sort_response(response.json()) == expected_response


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.experiments3(
    filename='experiment_with_sku_and_excluded_brands.json',
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql', 'fill_sku.sql'],
)
async def test_details_v2_with_sku_exp_on_and_disabled_brands(
        taxi_eats_nomenclature,
        pgsql,
        load_json,
        should_include_pennies_in_price,
):
    brand_id = 1
    retailer_id = 2
    sql_add_retailer_for_brand(pgsql, retailer_id, brand_id)

    await taxi_eats_nomenclature.invalidate_caches()
    request = {'products': REQUESTED_PRODUCTS, 'categories': []}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200
    expected_response = load_json('response_without_sku.json')

    if not should_include_pennies_in_price:
        pennies_utils.rounded_price(expected_response, 'products')
    assert _sort_response(response.json()) == expected_response


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.experiments3(filename='experiment_off.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql', 'fill_sku.sql'],
)
async def test_details_v2_with_sku_exp_off(
        taxi_eats_nomenclature, load_json, should_include_pennies_in_price,
):
    request = {'products': REQUESTED_PRODUCTS, 'categories': []}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200
    expected_response = load_json('response_without_sku.json')

    if not should_include_pennies_in_price:
        pennies_utils.rounded_price(expected_response, 'products')

    assert _sort_response(response.json()) == expected_response


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_limit_requested_items(taxi_eats_nomenclature, taxi_config):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS': {
                'v2/place/assortment/details': {'max_items_count': 3},
            },
        },
    )

    request = {'products': REQUESTED_PRODUCTS, 'categories': []}
    response_400 = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request,
    )
    assert response_400.status == 400

    request = {'products': REQUESTED_PRODUCTS[:2], 'categories': []}
    response_200 = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request,
    )
    assert response_200.status == 200


@stocks_utils.PARAMETRIZE_STOCKS_LIMITS
@pytest.mark.parametrize('stocks_reset_limit', [0, 1, 5])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stock_limit(
        taxi_eats_nomenclature,
        pg_cursor,
        load_json,
        experiments3,
        # paramaterize
        stocks_reset_limit,
        displayed_stocks_limits_applied,
        displayed_stocks_limits_exp_enabled,
):
    _sql_set_place_stock_limit(pg_cursor, PLACE_SLUG, stocks_reset_limit)

    public_id_to_disp_stock_limit = {
        REQUESTED_PRODUCTS[0]: 2,
        REQUESTED_PRODUCTS[1]: 4,
    }
    if displayed_stocks_limits_exp_enabled:
        await stocks_utils.enable_displ_stock_limits_exp(
            taxi_eats_nomenclature,
            experiments3,
            public_id_to_disp_stock_limit,
        )

    request = {'products': REQUESTED_PRODUCTS, 'categories': []}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?slug={PLACE_SLUG}', json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200
    expected_response = load_json('response_without_sku.json')

    pennies_utils.rounded_price(expected_response, 'products')
    _apply_limit_to_response(expected_response, stocks_reset_limit)
    if displayed_stocks_limits_applied:
        _apply_displayed_limit_to_response(
            expected_response, public_id_to_disp_stock_limit,
        )

    assert _sort_response(response.json()) == _sort_response(expected_response)


def sql_set_retailer_name_of_sku(pgsql, sku_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            update eats_nomenclature.sku_pictures
            set retailer_name='retailer_name'
            where sku_id={sku_id};
            """,
    )


def sql_add_retailer_for_brand(pgsql, retailer_id, brand_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into retailers(id, name, slug)
        values
        ({retailer_id}, 'retailer', 'retailer_slug');
        update eats_nomenclature.brands
        set retailer_id={retailer_id}
        where id={brand_id};
        """,
    )


def _sql_set_place_stock_limit(pg_cursor, place_slug, stock_reset_limit):
    pg_cursor.execute(
        """
        update eats_nomenclature.places
        set stock_reset_limit = %s
        where slug = %s
        """,
        (stock_reset_limit, place_slug),
    )


def _apply_limit_to_response(response, stocks_reset_limit):
    for product in response['products']:
        product_stock = product.get('in_stock', 0)
        if product_stock != 0 and product_stock < stocks_reset_limit:
            product['in_stock'] = 0


def _apply_displayed_limit_to_response(
        response, public_id_to_disp_stock_limit,
):
    for product in response['products']:
        public_id = product['product_id']
        if public_id not in public_id_to_disp_stock_limit:
            continue

        product_stock = product.get('in_stock', 0)
        displayed_stock_limit = public_id_to_disp_stock_limit[public_id]
        if product_stock != 0 and product_stock > displayed_stock_limit:
            product['in_stock'] = displayed_stock_limit


def _sort_response(response):
    response['categories'].sort(key=lambda category: category['category_id'])
    response['products'].sort(key=lambda product: product['product_id'])
    return response
