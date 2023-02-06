import pytest

from tests_eats_products import utils


PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
PRODUCT_PUBLIC_ID_SECOND = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'

PRODUCT_SKU_ID = '6949343c-d10d-4380-8507-ef0c0dba9670'
HEADERS = {
    'X-AppMetrica-DeviceId': 'device_id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
}


BASE_REQUEST = {
    'public_id': PRODUCT_PUBLIC_ID,
    'location': {'lat': 55.725326, 'lon': 37.567051},
}


@pytest.mark.parametrize(
    ('price', 'old_price'),
    [
        ('100.00', None),
        ('100.00', '40.00'),
        ('100.00', '100.00'),
        ('100.00', '120.00'),
    ],
)
@pytest.mark.parametrize('has_currency_in_db', [False, True])
async def test_product_cross_brand_products_basic(
        taxi_eats_products,
        load_json,
        mock_nomenclature_info_by_skuid,
        sql_set_place_currency,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
        price,
        old_price,
        has_currency_in_db,
):
    """
        Проверка на корректность полей ответа кросс-брендового поиска
        по public_id
    """
    mock_internal_v1_places_context.add_place()
    mock_nomenclature_info_by_skuid.add_product(
        1, PRODUCT_PUBLIC_ID, price, old_price,
    )
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    mock_nomenclature_info_by_skuid.expected_request = {
        'place_ids': [1],
        'sku_id': PRODUCT_SKU_ID,
    }
    expected_response = load_json('expected_cross_brand_response.json')
    if has_currency_in_db:
        sql_set_place_currency(code='BYN', sign='руб.')
        expected_response['crossbrand_products'][0]['place']['currency'] = {
            'code': 'BYN',
            'sign': 'руб.',
        }
    mock_internal_v1_places_context.expected_request = {
        'blocks': [
            {
                'condition': {
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                    'type': 'eq',
                },
                'id': 'kShopPlacesBlockId',
                'no_data': False,
                'type': 'open',
            },
        ],
        'location': {'latitude': 55.725326, 'longitude': 37.567051},
        'shipping_type': 'delivery',
        'enable_deduplication': True,
    }
    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    if old_price and float(old_price) > float(price):
        expected_response['crossbrand_products'][0]['product'][
            'decimal_promo_price'
        ] = price
        expected_response['crossbrand_products'][0]['product'][
            'decimal_price'
        ] = old_price
    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_nomenclature_info_by_skuid.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1
    assert resp.json() == expected_response


@pytest.mark.parametrize(
    'currency, has_currency_in_db',
    [
        pytest.param(
            {'code': 'BYN', 'sign': 'Br'},
            False,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_CURRENCY_SETTINGS=(
                        {'1': {'code': 'BYN', 'sign': 'Br'}}
                    ),
                )
            ),
            id='with currency',
        ),
        pytest.param(
            {'code': 'USD', 'sign': '$'},
            False,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_CURRENCY_SETTINGS={
                        '__default__': {'code': 'USD', 'sign': '$'},
                    },
                )
            ),
            id='changed default currency',
        ),
        pytest.param(
            {'code': 'BYN', 'sign': 'Br'},
            True,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_CURRENCY_SETTINGS=(
                        {'1': {'code': 'USD', 'sign': '$'}}
                    ),
                )
            ),
            id='with currency db',
        ),
        pytest.param(
            {'code': 'USD', 'sign': '$'},
            True,
            id='changed default currency db',
        ),
        pytest.param(
            {'code': 'RUB', 'sign': '₽'}, False, id='default currency',
        ),
    ],
)
async def test_product_cross_brand_products_currency(
        taxi_eats_products,
        load_json,
        mock_nomenclature_info_by_skuid,
        sql_set_place_currency,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
        currency,
        has_currency_in_db,
):
    """
        Проверка на корректность задания валюты для кросс-брендового поиска
        по public_id
    """
    mock_internal_v1_places_context.add_place()
    mock_nomenclature_info_by_skuid.add_product(1, PRODUCT_PUBLIC_ID)
    mock_nomenclature_info_by_skuid.expected_request = {
        'place_ids': [1],
        'sku_id': PRODUCT_SKU_ID,
    }
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    if has_currency_in_db:
        sql_set_place_currency(code=currency['code'], sign=currency['sign'])

    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    expected_response = load_json('expected_cross_brand_response.json')
    expected_response['crossbrand_products'][0]['place']['currency'] = currency
    assert resp.json() == expected_response


@pytest.mark.parametrize(
    'response_code', [400, 404, 429, 500, 'timeout', 'network_error'],
)
async def test_product_cross_brand_products_bad_responses_by_skuid(
        taxi_eats_products,
        mock_nomenclature_info_by_skuid,
        response_code,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверяет статус коды ошибок от /v1/places/products/info-by-sku-id
    """
    mock_internal_v1_places_context.add_place()
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    if response_code == 'timeout':
        mock_nomenclature_info_by_skuid.set_timeout_error(True)
    elif response_code == 'network_error':
        mock_nomenclature_info_by_skuid.set_network_error(True)
    else:
        mock_nomenclature_info_by_skuid.set_status(response_code)
    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_nomenclature_info_by_skuid.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1

    if response_code == 404:
        assert resp.status_code == 404
    else:
        assert resp.status_code == 500
        assert resp.json() == {
            'code': '500',
            'message': 'Internal Server Error',
        }


@pytest.mark.parametrize('place_enabled', [True, False])
@pytest.mark.parametrize('brand_enabled', [True, False])
async def test_product_cross_brand_products_disabled_brand_place(
        taxi_eats_products,
        load_json,
        mock_nomenclature_info_by_skuid,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
        sql_add_place,
        sql_add_brand,
        place_enabled,
        brand_enabled,
):
    """
        Проверка на корректность полей ответа кросс-брендового поиска
        c несколькими товарами
        По выключенным плейсам/брендам ответ не приходит
    """
    sql_add_brand(2, 'brand2', brand_enabled)
    sql_add_place(2, 'slug2', 2, place_enabled)
    mock_internal_v1_places_context.add_place()
    mock_internal_v1_places_context.add_place(
        place_id='2',
        place_slug='slug2',
        brand_id='2',
        brand_slug='brand2',
        brand_name='test_brand_name',
    )
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    mock_nomenclature_info_by_skuid.add_product(1, PRODUCT_PUBLIC_ID)
    mock_nomenclature_info_by_skuid.add_product(2, PRODUCT_PUBLIC_ID_SECOND)
    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )

    if place_enabled and brand_enabled:
        expected_response = load_json(
            'expected_cross_brand_response_more_places.json',
        )
    else:
        expected_response = load_json('expected_cross_brand_response.json')

    response = resp.json()
    response['crossbrand_products'].sort(
        key=lambda product: product['product']['public_id'],
    )
    assert response == expected_response


async def test_product_cross_brand_products_non_cached_place(
        taxi_eats_products,
        load_json,
        mock_nomenclature_info_by_skuid,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверка на то, что плейсы, отсутствующие в кеше не приходят
    """
    mock_internal_v1_places_context.add_place()
    mock_internal_v1_places_context.add_place(
        place_id='2',
        place_slug='slug2',
        brand_id='2',
        brand_slug='brand2',
        brand_name='test_brand_name',
    )
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    mock_nomenclature_info_by_skuid.add_product(1, PRODUCT_PUBLIC_ID)
    mock_nomenclature_info_by_skuid.add_product(2, PRODUCT_PUBLIC_ID_SECOND)
    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    expected_response = load_json('expected_cross_brand_response.json')
    assert resp.json() == expected_response


@pytest.mark.parametrize(
    'response_code', [400, 429, 500, 'timeout', 'network_error'],
)
async def test_product_cross_brand_products_bad_responses_by_catalog(
        taxi_eats_products,
        response_code,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверяет статус коды ошибок от /v1/internal/places
    """
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )

    mock_internal_v1_places_context.add_place()
    if response_code == 'timeout':
        mock_internal_v1_places_context.set_timeout_error(True)
    elif response_code == 'network_error':
        mock_internal_v1_places_context.set_network_error(True)
    else:
        mock_internal_v1_places_context.set_status(response_code)
    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )

    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1

    assert resp.status_code == 500
    assert resp.json() == {'code': '500', 'message': 'Internal Server Error'}


async def test_product_cross_brand_products_empty_response_by_skuid(
        taxi_eats_products,
        mock_nomenclature_info_by_skuid,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверяет что ответ пустой при пустом ответе
        от /v1/places/products/info-by-sku-id
    """
    mock_internal_v1_places_context.add_place()
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )

    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_nomenclature_info_by_skuid.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1
    assert resp.json()['crossbrand_products'] == []


@pytest.mark.parametrize(
    'block_name', [None, 'unknown_block_id', 'kShopPlacesBlockId'],
)
async def test_product_cross_brand_products_empty_response_block(
        taxi_eats_products,
        mock_internal_v1_places_context,
        block_name,
        mock_generalized_info_context,
):
    """
        Проверяет что ответ пустой при пустом ответе
        от /v1/internal/places
    """
    mock_internal_v1_places_context.block_name = block_name
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1
    assert resp.json()['crossbrand_products'] == []


@pytest.mark.config(
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS={
        'v1_place_products_info_by_sku_id_batch_size': 50,
    },
)
async def test_product_cross_brand_products_batch(
        taxi_eats_products,
        mock_nomenclature_info_by_skuid,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверка передачи параметров в батч запросе
    """
    for i in range(1, 101):
        mock_internal_v1_places_context.add_place(
            place_id=f'{i}',
            place_slug=f'slug_{i}',
            brand_id=f'{i}',
            brand_slug=f'brand{i}',
        )

    mock_nomenclature_info_by_skuid.add_product(1, PRODUCT_PUBLIC_ID)
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    stored_requests = {'place_ids': [], 'sku_id': []}

    for store_request in mock_nomenclature_info_by_skuid.stored_requests:
        stored_requests['place_ids'] += list(
            map(int, store_request['place_ids']),
        )
        stored_requests['sku_id'].append(store_request['sku_id'])

    stored_requests['place_ids'].sort()

    assert stored_requests['place_ids'] == list(range(1, 101))
    assert stored_requests['sku_id'] == [PRODUCT_SKU_ID, PRODUCT_SKU_ID]

    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1
    assert mock_nomenclature_info_by_skuid.times_called == 2
    assert resp.status_code == 200


@pytest.mark.parametrize(
    ('logo', 'logo_ok'),
    [
        pytest.param(
            {
                'light': [{'size': 'large', 'logo_url': 'logo_url'}],
                'dark': [{'size': 'large', 'logo_url': 'logo_url'}],
            },
            True,
            id='good logo',
        ),
        pytest.param(
            {
                'light': [
                    {'size': 'large', 'logo_url': 'logo_url'},
                    {'logo_url': 'logo_url'},
                ],
                'dark': [{'size': 'large', 'logo_url': 'logo_url'}],
            },
            True,
            id='one good logo one bad',
        ),
        pytest.param(
            {
                'light': [{'logo_url': 'logo_url'}],
                'dark': [{'size': 'large', 'logo_url': 'logo_url'}],
            },
            False,
            id='no size',
        ),
        pytest.param(
            {
                'light': [{'size': 'large', 'logo_url': 'logo_url'}],
                'dark': [{'size': 'large'}],
            },
            False,
            id='no brand_logo',
        ),
        pytest.param(
            {'light': [], 'dark': [{'size': 'large', 'logo_url': 'logo_url'}]},
            False,
            id='empty scheme',
        ),
        pytest.param(None, False, id='None logo'),
    ],
)
@pytest.mark.parametrize(
    ('color', 'color_ok'),
    [
        pytest.param(
            {'light': '#111111', 'dark': '#ffffff'}, True, id='color ok',
        ),
        pytest.param(None, False, id='None color'),
    ],
)
async def test_product_cross_brand_products_catalog_override(
        taxi_eats_products,
        mock_nomenclature_info_by_skuid,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
        logo,
        color,
        logo_ok,
        color_ok,
):
    """
        Проверяет, что при проблемах с лого или цветом,
        плейс считается неподходящим для выдачи.
    """
    mock_internal_v1_places_context.logo = logo
    mock_internal_v1_places_context.color = color
    mock_internal_v1_places_context.add_place()
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    # у нас 1 плейс, поэтому по факту, проверяем, если плохое logo/color,
    # то мы не будем вызывать нмн
    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1
    assert mock_nomenclature_info_by_skuid.times_called == (
        1 if logo_ok and color_ok else 0
    )
    assert resp.json()['crossbrand_products'] == []
    assert resp.status_code == 200


@pytest.mark.parametrize(
    'response_code', [400, 404, 429, 500, 'timeout', 'network_error'],
)
async def test_product_cross_brand_products_bad_responses_by_generalized(
        taxi_eats_products,
        response_code,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверяет статус коды ошибок от v1/product/generalized-info
    """
    mock_internal_v1_places_context.add_place()
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    if response_code == 'timeout':
        mock_internal_v1_places_context.set_timeout_error(True)
    elif response_code == 'network_error':
        mock_internal_v1_places_context.set_network_error(True)
    else:
        mock_generalized_info_context.set_status(response_code)

    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )

    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1
    if response_code == 404:
        assert resp.status_code == 404
    else:
        assert resp.status_code == 500
        assert resp.json() == {
            'code': '500',
            'message': 'Internal Server Error',
        }


async def test_product_cross_brand_products_empty_sku(
        taxi_eats_products,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверяет что приходит пустой ответ при отсутствии поля sku_id
         в ответе от v1/product/generalized-info
    """
    mock_internal_v1_places_context.add_place()
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'],
    )
    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1

    assert resp.json()['crossbrand_products'] == []
    assert resp.status_code == 200


async def test_product_cross_brand_products_place_deduplication(
        taxi_eats_products,
        load_json,
        mock_nomenclature_info_by_skuid,
        mock_internal_v1_places_context,
        mock_generalized_info_context,
):
    """
        Проверка, что при наличии нескольких public_id с одним sku_id
        в одном бренде, будет выдаваться только 1 товар
    """
    mock_internal_v1_places_context.add_place()
    mock_nomenclature_info_by_skuid.add_product(1, PRODUCT_PUBLIC_ID)
    mock_nomenclature_info_by_skuid.add_product(1, PRODUCT_PUBLIC_ID_SECOND)
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'], PRODUCT_SKU_ID,
    )
    expected_response = load_json('expected_cross_brand_response.json')

    resp = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_PRODUCTS,
        json=BASE_REQUEST,
        headers=HEADERS,
    )
    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_nomenclature_info_by_skuid.handler.times_called == 1
    assert mock_internal_v1_places_context.handler.times_called == 1
    assert resp.json() == expected_response
