import pytest

import tests_eats_nomenclature.parametrize.displayed_stock_limits as stocks_utils  # noqa: E501 pylint: disable=line-too-long
import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils

PLACE_ID = '1'
HANDLER = '/v1/place/products/info'
AUTH_HEADERS = {'x-device-id': 'device_id'}


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.parametrize(
    'assortment_name, experiment_on, expected_response_file',
    [
        (None, True, 'exp_response.json'),
        (None, False, 'default_response.json'),
        ('assortment_name', True, 'assortment_response.json'),
        ('unknown_assortment_name', True, 'default_response.json'),
        ('partner', False, 'partner_response.json'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_200(
        taxi_eats_nomenclature,
        load_json,
        set_assortment_name_exp,
        # parametrize
        should_include_pennies_in_price,
        assortment_name,
        experiment_on,
        expected_response_file,
):
    set_assortment_name_exp(experiment_on, 'exp_assortment_name')

    request = {
        'product_ids': [
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009',
            'unknown_product_public_id',
        ],
    }
    query = f'{HANDLER}?place_id={PLACE_ID}'
    if assortment_name:
        query += f'&assortment_name={assortment_name}'
    response = await taxi_eats_nomenclature.post(
        query, json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200
    expected_response = _sorted_response(load_json(expected_response_file))

    if not should_include_pennies_in_price:
        pennies_utils.rounded_price(expected_response, 'products')

    assert _sorted_response(response.json()) == expected_response


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_unknown_place(taxi_eats_nomenclature):
    unknown_place_id = '123'
    request = {'product_ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001']}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={unknown_place_id}', json=request,
    )

    assert response.status == 404


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
    _sql_set_place_stock_limit(pg_cursor, PLACE_ID, stocks_reset_limit)

    public_id_to_disp_stock_limit = {
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001': 2,
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002': 4,
    }
    if displayed_stocks_limits_exp_enabled:
        await stocks_utils.enable_displ_stock_limits_exp(
            taxi_eats_nomenclature,
            experiments3,
            public_id_to_disp_stock_limit,
        )

    request = {
        'product_ids': [
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009',
            'unknown_product_public_id',
        ],
    }
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200

    expected_response = load_json('default_response.json')
    pennies_utils.rounded_price(expected_response, 'products')
    _apply_limit_to_response(expected_response, stocks_reset_limit)
    if displayed_stocks_limits_applied:
        _apply_displayed_limit_to_response(
            expected_response, public_id_to_disp_stock_limit,
        )

    assert _sorted_response(response.json()) == _sorted_response(
        expected_response,
    )


@pytest.mark.parametrize(
    'exp_brand_ids, exp_excluded_place_ids, expected_assortment_id',
    [
        pytest.param([1], [], 1, id='exp assortment'),
        pytest.param(
            [1], [1], 3, id='default assortment: place in excluded places',
        ),
        pytest.param(
            [2], [], 3, id='default assortment: brand not in exp brands',
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
        assortment_name='exp_assortment_name',
        brand_ids=exp_brand_ids,
        excluded_place_ids=exp_excluded_place_ids,
    )

    @testpoint('v1-place-products-info-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == expected_assortment_id

    request = {'product_ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001']}
    query = f'{HANDLER}?place_id={PLACE_ID}'
    await taxi_eats_nomenclature.post(
        query, json=request, headers=AUTH_HEADERS,
    )

    assert _assortment.has_calls


def _sorted_response(response):
    response['products'].sort(key=lambda k: k['id'])
    return response


def _apply_limit_to_response(response, stocks_reset_limit):
    for product in response['products']:
        product_stock = product.get('in_stock', 0)
        if product_stock != 0 and product_stock < stocks_reset_limit:
            product['in_stock'] = 0


def _apply_displayed_limit_to_response(
        response, public_id_to_disp_stock_limit,
):
    for product in response['products']:
        public_id = product['id']
        if public_id not in public_id_to_disp_stock_limit:
            continue

        product_stock = product.get('in_stock', 0)
        displayed_stock_limit = public_id_to_disp_stock_limit[public_id]
        if product_stock != 0 and product_stock > displayed_stock_limit:
            product['in_stock'] = displayed_stock_limit


def _sql_set_place_stock_limit(pg_cursor, place_id, stock_reset_limit):
    pg_cursor.execute(
        """
        update eats_nomenclature.places
        set stock_reset_limit = %s
        where id = %s
        """,
        (stock_reset_limit, place_id),
    )
