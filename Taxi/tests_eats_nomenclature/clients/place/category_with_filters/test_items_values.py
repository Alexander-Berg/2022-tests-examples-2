import datetime as dt

import pytest
import pytz

HANDLER = '/v1/place/category_products/filtered'
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)

ASSORTMENT_NAME = 'assortment_name_1'
ASSORTMENT_ID = 1
PLACE_ID = 1
ROOT_CATEGORY_ID = 11
CATEGORY_ID_1 = 22
CATEGORY_ID_2 = 33
CATEGORY_ID_1_1 = 44
CATEGORY_ID_UNKNOWN = 99999
BIG_STOCK_RESET_LIMIT = 1000

QUERY_PLACE_ID = 1
QUERY_PRODUCT_ID = 1
PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_full_response.sql'],
)
async def test_full_schema(taxi_eats_nomenclature, load_json):
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    expected_response = load_json('full_response.json')

    assert sorted_response_json(response.json()) == sorted_response_json(
        expected_response,
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_data_for_minimal_response.sql',
        'fill_products_for_minimal_response.sql',
    ],
)
async def test_minimal_product_schema(taxi_eats_nomenclature, load_json):
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    expected_response = load_json('minimal_response_with_product.json')

    assert sorted_response_json(response.json()) == sorted_response_json(
        expected_response,
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_without_categories.sql'],
)
async def test_unknown_category(taxi_eats_nomenclature, load_json):
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID_UNKNOWN}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    expected_response = load_json('empty_response.json')

    assert response.json() == expected_response


@pytest.mark.parametrize(
    'product_ids_to_disable, expected_product_public_ids',
    [
        pytest.param(
            [],
            [
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            ],
        ),
        pytest.param(
            [2, 4],
            [
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            ],
        ),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_for_availability_test.sql',
    ],
)
async def test_availability(
        taxi_eats_nomenclature,
        pgsql,
        # parametrize params
        product_ids_to_disable,
        expected_product_public_ids,
):
    if product_ids_to_disable:
        sql_disable_products(pgsql, product_ids_to_disable)

    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()

    assert len(response_json['categories']) == 1
    product_ids_from_response = [
        product['id'] for product in response_json['categories'][0]['products']
    ]
    assert sorted(product_ids_from_response) == sorted(
        expected_product_public_ids,
    )


@pytest.mark.parametrize(
    'include_pennies_in_price, db_prices, expected_prices',
    [
        pytest.param(
            True,
            {'price': '123.456', 'old_price': '345.456'},
            {'price': '123.46', 'old_price': '345.46'},
        ),
        pytest.param(
            False,
            {'price': '123.656', 'old_price': '345.656'},
            {'price': '124', 'old_price': '346'},
        ),
        pytest.param(
            True,
            {'price': '123.454', 'old_price': '345.454'},
            {'price': '123.45', 'old_price': '345.45'},
        ),
        pytest.param(
            False,
            {'price': '123.454', 'old_price': '345.454'},
            {'price': '123', 'old_price': '345'},
        ),
    ],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_PRICE_ROUNDING={
        '1': {'should_include_pennies_in_price': True},
    },
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_one_product.sql'],
)
async def test_price_rounding(
        taxi_eats_nomenclature,
        pgsql,
        update_taxi_config,
        # parametrize params
        include_pennies_in_price,
        db_prices,
        expected_prices,
):
    sql_set_prices(pgsql, db_prices['price'], db_prices['old_price'])

    update_taxi_config(
        'EATS_NOMENCLATURE_PRICE_ROUNDING',
        {'1': {'should_include_pennies_in_price': include_pennies_in_price}},
    )

    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    response_product = extract_product_from_response(response_json)
    assert response_product['price'] == expected_prices['price']
    assert response_product['old_price'] == expected_prices['old_price']


@pytest.mark.parametrize(
    'test_params, expected_prices',
    [
        pytest.param(
            {
                'price': '1000',
                'old_price': '2000',
                'full_price': None,
                'old_full_price': None,
                'is_catch_weight': False,
                'quantum': 0.1,
            },
            {'price': '1000', 'old_price': '2000'},
        ),
        pytest.param(
            {
                'price': '1000',
                'old_price': '2000',
                'full_price': '3000',
                'old_full_price': '4000',
                'is_catch_weight': False,
                'quantum': 0.1,
            },
            {'price': '3000', 'old_price': '4000'},
        ),
        pytest.param(
            {
                'price': '1000',
                'old_price': '2000',
                'full_price': None,
                'old_full_price': None,
                'is_catch_weight': True,
                'quantum': 0.1,
            },
            {'price': '1000', 'old_price': '2000'},
        ),
        pytest.param(
            {
                'price': '1000',
                'old_price': '2000',
                'full_price': '3000',
                'old_full_price': '4000',
                'is_catch_weight': True,
                'quantum': 0.1,
            },
            {'price': '300', 'old_price': '400'},
        ),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_one_product.sql'],
)
async def test_price_measure_adjustment(
        taxi_eats_nomenclature,
        pgsql,
        # parametrize params
        test_params,
        expected_prices,
):
    sql_set_prices(
        pgsql,
        test_params['price'],
        test_params['old_price'],
        test_params['full_price'],
        test_params['old_full_price'],
    )
    sql_update_product(
        pgsql, test_params['quantum'], test_params['is_catch_weight'],
    )

    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    response_product = extract_product_from_response(response_json)
    assert response_product['price'] == expected_prices['price']
    assert response_product['old_price'] == expected_prices['old_price']


@pytest.mark.parametrize(
    'stock_reset_limit, expected_displayed_stocks',
    [
        pytest.param(
            5,
            {
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001': 10,
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002': 20,
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003': 30,
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004': 40,
            },
        ),
        pytest.param(
            25,
            {
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003': 30,
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004': 40,
            },
        ),
        pytest.param(BIG_STOCK_RESET_LIMIT, {}),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_displayed_stock(
        taxi_eats_nomenclature,
        pgsql,
        # parametrize params
        stock_reset_limit,
        expected_displayed_stocks,
):
    sql_set_stock_reset_limit(pgsql, stock_reset_limit)

    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    assert len(response_json['categories']) == 1
    assert len(response_json['categories'][0]['products']) == len(
        expected_displayed_stocks.keys(),
    )
    for product in response_json['categories'][0]['products']:
        assert product['in_stock'] == expected_displayed_stocks[product['id']]


@pytest.mark.parametrize(
    'categories_items_count, expected_categories_in_response',
    [
        pytest.param(
            {
                ROOT_CATEGORY_ID: 1,
                CATEGORY_ID_1: 1,
                CATEGORY_ID_2: 1,
                CATEGORY_ID_1_1: 1,
            },
            [
                str(ROOT_CATEGORY_ID),
                str(CATEGORY_ID_1),
                str(CATEGORY_ID_2),
                str(CATEGORY_ID_1_1),
            ],
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: 1,
                CATEGORY_ID_1: 1,
                CATEGORY_ID_2: 0,
                CATEGORY_ID_1_1: 1,
            },
            [str(ROOT_CATEGORY_ID), str(CATEGORY_ID_1), str(CATEGORY_ID_1_1)],
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: 1,
                CATEGORY_ID_1: 0,
                CATEGORY_ID_2: 1,
                CATEGORY_ID_1_1: 0,
            },
            [str(ROOT_CATEGORY_ID), str(CATEGORY_ID_2)],
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: 0,
                CATEGORY_ID_1: 0,
                CATEGORY_ID_2: 0,
                CATEGORY_ID_1_1: 0,
            },
            [],
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: 0,
                CATEGORY_ID_1: 1,
                CATEGORY_ID_2: 1,
                CATEGORY_ID_1_1: 1,
            },
            [],
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: 1,
                CATEGORY_ID_1: 0,
                CATEGORY_ID_2: 1,
                CATEGORY_ID_1_1: 1,
            },
            [str(ROOT_CATEGORY_ID), str(CATEGORY_ID_2)],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_empty_categories(
        taxi_eats_nomenclature,
        pgsql,
        # parametrize params
        categories_items_count,
        expected_categories_in_response,
):
    category_public_id_to_id = {
        ROOT_CATEGORY_ID: 1,
        CATEGORY_ID_1: 2,
        CATEGORY_ID_2: 3,
        CATEGORY_ID_1_1: 4,
    }

    for category_id, active_items_count in categories_items_count.items():
        sql_insert_places_categories(
            pgsql, category_public_id_to_id[category_id], active_items_count,
        )

    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    categories_from_response = extract_categories_from_response(response_json)
    categories_from_response.sort()
    expected_categories_in_response.sort()
    assert categories_from_response == expected_categories_in_response


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_test_category_types.sql'],
)
@pytest.mark.parametrize(
    'category_to_request, expected_type',
    [
        pytest.param(11, 'partner', id='partner'),
        pytest.param(22, 'custom_promo', id='custom_promo'),
        pytest.param(33, 'custom_base', id='custom_base'),
        pytest.param(44, 'custom_restaurant', id='custom_restaurant'),
    ],
)
async def test_category_types(
        taxi_eats_nomenclature,
        # parametrize
        category_to_request,
        expected_type,
):
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={category_to_request}'
    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    assert response.json()['categories'][0]['type'] == expected_type


def sorted_response_json(response_json):
    for category in response_json['categories']:
        category['child_ids'].sort()
        category['products'].sort(key=lambda product: product['id'])
    response_json['categories'].sort(key=lambda category: category['id'])

    return response_json


def sql_disable_products(pgsql, products_to_disable):
    products_to_disable = [str(id) for id in products_to_disable]
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""update eats_nomenclature.places_products
            set available_from = now() + interval '2 hours'
            where product_id = any(array[{', '.join(products_to_disable)}])
        """,
    )


def sql_insert_places_categories(pgsql, category_id, active_items_count):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.places_categories
        (assortment_id, place_id, category_id, active_items_count)
        values
        ({ASSORTMENT_ID}, {PLACE_ID}, {category_id}, {active_items_count});
        """,
    )


def sql_set_prices(
        pgsql, price, old_price, full_price=None, old_full_price=None,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""update eats_nomenclature.places_products
            set
                price = {price},
                old_price = {old_price}
            where product_id = {QUERY_PRODUCT_ID}
        """,
    )
    if full_price and old_full_price:
        cursor.execute(
            f"""update eats_nomenclature.places_products
            set
                full_price = {full_price},
                old_full_price = {old_full_price}
            where product_id = {QUERY_PRODUCT_ID}
        """,
        )


def sql_update_product(pgsql, quantum, is_catch_weight):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""update eats_nomenclature.products
            set
                quantum = {quantum},
                is_catch_weight = {is_catch_weight}
            where id = {QUERY_PRODUCT_ID}
        """,
    )


def sql_set_stock_reset_limit(pgsql, stock_reset_limit):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""update eats_nomenclature.places
            set
                stock_reset_limit = {stock_reset_limit}
            where id = {QUERY_PLACE_ID}
        """,
    )


def extract_product_from_response(response):
    assert len(response['categories']) == 1
    assert len(response['categories'][0]['products']) == 1
    assert response['categories'][0]['products'][0]['id'] == PRODUCT_PUBLIC_ID

    return response['categories'][0]['products'][0]


def extract_categories_from_response(response):  # pylint: disable=C0103
    return [category['id'] for category in response['categories']]
