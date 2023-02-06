from dateutil import parser
import pytest

from tests_eats_retail_market_integration import models
from tests_eats_retail_market_integration.eats_catalog_internals import storage

EATS_PRODUCTS_HANDLER = '/eats-products/internal/v2/products/core_id'
EATS_CART_HANDLER = '/eats-cart/api/v1/cart/sync'
HANDLER = '/v1/market/cart/create'

BRAND_ID = '777'
BRAND_SLUG = 'brand777'
PLACE_ID = '123456'
PLACE_SLUG = 'slug123456'
ZONE_ID = 1
BUSINESS_ID = 999
SHOP_ID = 199
EATS_CURRENCY = 'RUB'
MARKET_CURRENCY = 'RUR'
DEFAULT_LATITUDE = 10.0
DEFAULT_LONGITUDE = 20.0
SHIPPING_TYPE = 'delivery'
BUSINESS_TYPE = 'shop'
X_PLATFORM = 'android_app'
X_APP_VERSION = '12.11.12'
X_EATS_USER = 'user_id=123'
ASSEMBLY_COST = 1


TEST_ITEMS = [
    {
        'eats_cart_id': 1,
        'nomenclature_item_id': '101ac7bc-f01a-43f1-88d9-cf5e6a52c123',
        'core_id': 123,
        'name': 'Item 1',
        'request_count': 10,
        'cart_count': 8,
        'price': '1023.50',
        'discount_price': '989.35',
        'found': True,
    },
    {
        'eats_cart_id': 2,
        'nomenclature_item_id': '101ac7bc-f01a-43f1-88d9-cf5e6a52c124',
        'core_id': 124,
        'name': 'Item 2',
        'request_count': 5,
        'cart_count': 5,
        'price': '5642',
        'found': True,
    },
    {
        'nomenclature_item_id': '101ac7bc-f01a-43f1-88d9-cf5e6a52c999',
        'request_count': 5,
        'found': False,
    },
]


@pytest.mark.parametrize(
    'has_validation_errors',
    [pytest.param(True, id='has_errors'), pytest.param(False, id='no_errors')],
)
async def test_200_create_market_cart(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
        # parametrize params
        has_validation_errors,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()
    eats_cart_response = _generate_eats_cart_response(
        items=TEST_ITEMS,
        has_errors=has_validation_errors,
        is_place_available=True,
    )

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        assert request.json['place_id'] == int(PLACE_ID)
        assert set(request.json['public_ids']) == set(
            i['nomenclature_item_id'] for i in TEST_ITEMS
        )
        return {
            'products_ids': [
                {
                    'public_id': i['nomenclature_item_id'],
                    'core_id': i.get('core_id', None),
                }
                for i in TEST_ITEMS
            ],
        }

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        assert (
            {
                'X-Platform': request.headers['X-Platform'],
                'X-Eats-User': request.headers['X-Eats-User'],
            }
            == {
                'X-Platform': 'eda_desktop_market_web',
                'X-Eats-User': headers['X-Eats-User'],
            }
        )
        assert float(request.query['latitude']) == DEFAULT_LATITUDE
        assert float(request.query['longitude']) == DEFAULT_LONGITUDE
        assert request.query['shippingType'] == SHIPPING_TYPE
        assert request.json['shipping_type'] == SHIPPING_TYPE
        assert request.json['place_slug'] == PLACE_SLUG
        assert request.json['place_business'] == BUSINESS_TYPE
        assert request.json['items'] == [
            {'item_id': i['core_id'], 'quantity': i['request_count']}
            for i in TEST_ITEMS
            if 'core_id' in i
        ]
        return eats_cart_response

    expected_response = _generate_expected_response(
        items=TEST_ITEMS, eats_cart_response=eats_cart_response,
    )

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 200
    _verify_handler_response_json(response.json(), expected_response)

    assert _mock_eats_products.times_called == 1
    assert _mock_eats_cart.times_called == 1


async def test_401_unauthorized(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        pass

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        pass

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers={}, json=request,
    )
    assert response.status == 401

    assert not _mock_eats_products.has_calls
    assert not _mock_eats_cart.has_calls


async def test_404_market_brand_place_not_found(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        pass

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        pass

    unknown_shop_id = SHOP_ID + 100
    request = _build_handler_request(unknown_shop_id, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 404
    assert response.json() == {
        'code': '404',
        'message': (
            f'Market brand place not found in cache '
            f'for shop_id = {unknown_shop_id}'
        ),
    }

    assert not _mock_eats_products.has_calls
    assert not _mock_eats_cart.has_calls


async def test_404_from_eats_products(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        return mockserver.make_response(
            status=404,
            json={
                'code': 'place_not_found',
                'message': f'Place {PLACE_ID} not found',
            },
        )

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        pass

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 404
    assert response.json() == {
        'code': '404',
        'message': (
            f'Place {PLACE_ID} not found in eats-products: '
            f'Place {PLACE_ID} not found'
        ),
    }

    assert _mock_eats_products.times_called == 1
    assert not _mock_eats_cart.has_calls


async def test_400_from_eats_cart(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        assert request.json['place_id'] == int(PLACE_ID)
        assert set(request.json['public_ids']) == set(
            i['nomenclature_item_id'] for i in TEST_ITEMS
        )
        return {
            'products_ids': [
                {
                    'public_id': i['nomenclature_item_id'],
                    'core_id': i.get('core_id', None),
                }
                for i in TEST_ITEMS
            ],
        }

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 5,
                'domain': 'UserData',
                'err': 'Неверный формат',
                'errors': {
                    'item_id': ['Элементы должны принадлежать к одному месту'],
                },
            },
        )

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Got validation error from eats-cart: Неверный формат, '
            + 'errors: '
            + '{"item_id":["Элементы должны принадлежать к одному месту"]}'
        ),
    }

    assert _mock_eats_products.times_called == 1
    assert _mock_eats_cart.times_called == 1


@pytest.mark.parametrize(
    'error_type',
    [
        pytest.param('error.items_limit_exceeded'),
        pytest.param('error.total_limit_exceeded'),
    ],
)
async def test_eats_cart_limit_exceeded(
        taxi_eats_retail_market_integration,
        mockserver,
        error_type,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        assert request.json['place_id'] == int(PLACE_ID)
        assert set(request.json['public_ids']) == set(
            i['nomenclature_item_id'] for i in TEST_ITEMS
        )
        return {
            'products_ids': [
                {
                    'public_id': i['nomenclature_item_id'],
                    'core_id': i.get('core_id', None),
                }
                for i in TEST_ITEMS
            ],
        }

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        return mockserver.make_response(
            status=400,
            json={'code': 5, 'domain': 'UserData', 'err': error_type},
        )

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 200
    assert response.json() == _generate_handler_error_response(
        TEST_ITEMS,
        errors=[
            'TotalLimitExceeded'
            if error_type == 'error.total_limit_exceeded'
            else 'ItemsLimitExceeded',
        ],
    )

    assert _mock_eats_products.times_called == 1
    assert _mock_eats_cart.times_called == 1


async def test_products_mapping_error(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        return {'products_ids': []}

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        pass

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 200
    assert response.json() == _generate_handler_error_response(TEST_ITEMS)

    assert _mock_eats_products.times_called == 1
    assert not _mock_eats_cart.has_calls


async def test_400_empty_market_cart(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        pass

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        pass

    request = _build_handler_request(SHOP_ID, items=[])
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: prepared empty cart in request',
    }

    assert not _mock_eats_products.has_calls
    assert not _mock_eats_cart.has_calls


async def test_404_place_unavailable(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    headers = _get_auth_headers()
    eats_cart_response = _generate_eats_cart_response(
        items=TEST_ITEMS, has_errors=False, is_place_available=False,
    )

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        return {
            'products_ids': [
                {
                    'public_id': i['nomenclature_item_id'],
                    'core_id': i.get('core_id', None),
                }
                for i in TEST_ITEMS
            ],
        }

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        return eats_cart_response

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 200
    assert response.json() == _generate_expected_response(
        TEST_ITEMS, eats_cart_response,
    )

    assert _mock_eats_products.times_called == 1
    assert _mock_eats_cart.times_called == 1


@pytest.mark.experiments3(filename='cart_service_fee_exp.json')
@pytest.mark.parametrize(
    'has_validation_errors',
    [pytest.param(True, id='has_errors'), pytest.param(False, id='no_errors')],
)
async def test_additional_fees(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
        save_brand_places_to_storage,
        eats_catalog_storage,
        # parametrize params
        has_validation_errors,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_brand_places_to_storage(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    eats_places_set_init_places(eats_catalog_storage)

    headers = _get_auth_headers()
    eats_cart_response = _generate_eats_cart_response(
        items=TEST_ITEMS,
        has_errors=has_validation_errors,
        is_place_available=True,
    )

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        assert request.json['place_id'] == int(PLACE_ID)
        assert set(request.json['public_ids']) == set(
            i['nomenclature_item_id'] for i in TEST_ITEMS
        )
        return {
            'products_ids': [
                {
                    'public_id': i['nomenclature_item_id'],
                    'core_id': i.get('core_id', None),
                }
                for i in TEST_ITEMS
            ],
        }

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        assert (
            {
                'X-Platform': request.headers['X-Platform'],
                'X-Eats-User': request.headers['X-Eats-User'],
            }
            == {
                'X-Platform': 'eda_desktop_market_web',
                'X-Eats-User': headers['X-Eats-User'],
            }
        )
        assert float(request.query['latitude']) == DEFAULT_LATITUDE
        assert float(request.query['longitude']) == DEFAULT_LONGITUDE
        assert request.query['shippingType'] == SHIPPING_TYPE
        assert request.json['shipping_type'] == SHIPPING_TYPE
        assert request.json['place_slug'] == PLACE_SLUG
        assert request.json['place_business'] == BUSINESS_TYPE
        assert request.json['items'] == [
            {'item_id': i['core_id'], 'quantity': i['request_count']}
            for i in TEST_ITEMS
            if 'core_id' in i
        ]
        return eats_cart_response

    additional_fees = [
        {
            'value': 39,
            'title': 'Работа сервиса',
            'description': (
                'Мы развиваем Еду для вас — внедряем новые '
                'функции и улучшаем сервис. Спасибо, что вы с нами!'
            ),
            'confirm_text': 'Хорошо',
        },
    ]
    expected_response = _generate_expected_response(
        items=TEST_ITEMS,
        eats_cart_response=eats_cart_response,
        additional_fees=additional_fees,
    )

    request = _build_handler_request(SHOP_ID, items=TEST_ITEMS)
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )
    assert response.status == 200
    _verify_handler_response_json(response.json(), expected_response)

    assert _mock_eats_products.times_called == 1
    assert _mock_eats_cart.times_called == 1


@pytest.mark.parametrize('enable_assembly_cost', [True, False])
async def test_assembly_cost(
        eats_catalog_storage,
        mockserver,
        taxi_eats_retail_market_integration,
        save_brand_places_to_storage,
        save_brands_to_db,
        save_market_brand_places_to_db,
        save_places_info_to_db,
        update_taxi_config,
        # parametrize params
        enable_assembly_cost,
):
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_DELIVERY_COST',
        {'should_include_assembly_cost': enable_assembly_cost},
    )

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_brand_places_to_storage(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    places_info = _generate_places_info()
    save_places_info_to_db(places_info)

    eats_places_set_init_places(eats_catalog_storage)

    headers = _get_auth_headers()

    @mockserver.json_handler(EATS_PRODUCTS_HANDLER)
    def _mock_eats_products(request):
        return {
            'products_ids': [
                {
                    'public_id': TEST_ITEMS[0]['nomenclature_item_id'],
                    'core_id': TEST_ITEMS[0]['core_id'],
                },
            ],
        }

    eats_cart_response = _generate_eats_cart_response(
        items=[TEST_ITEMS[0]], is_place_available=True,
    )

    @mockserver.json_handler(EATS_CART_HANDLER)
    def _mock_eats_cart(request):
        return eats_cart_response

    request = _build_handler_request(SHOP_ID, items=[TEST_ITEMS[0]])
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers=headers, json=request,
    )

    assert _mock_eats_products.times_called == 1
    assert _mock_eats_cart.times_called == 1

    cart_response_data = eats_cart_response['cart']
    expected_result = {
        'shipping_cost': float(cart_response_data['decimal_delivery_fee']),
        'total': float(cart_response_data['decimal_total']),
    }
    if enable_assembly_cost:
        expected_result['shipping_cost'] += ASSEMBLY_COST
        expected_result['total'] += ASSEMBLY_COST

    assert response.status == 200
    response_data = response.json()
    assert (
        response_data['prices']['shipping_cost']
        == expected_result['shipping_cost']
    )

    assert response_data['prices']['total'] == expected_result['total']


def _build_handler_request(shop_id, items):
    return {
        'shop_id': shop_id,
        'user_address': {
            'latitude': DEFAULT_LATITUDE,
            'longitude': DEFAULT_LONGITUDE,
        },
        'items': [
            {
                'feed_offer_id': i['nomenclature_item_id'],
                'count': i['request_count'],
            }
            for i in items
        ],
    }


def _get_auth_headers():
    return {
        'X-Platform': X_PLATFORM,
        'X-App-Version': X_APP_VERSION,
        'X-Eats-User': X_EATS_USER,
    }


def _generate_expected_response(
        items, eats_cart_response, additional_fees=None,
):
    cart = eats_cart_response['cart']

    result_items = []
    for i in items:
        result_item = {
            'feed_offer_id': i['nomenclature_item_id'],
            'found': i['found'],
            'count': i.get('cart_count', 0),
            'price': float(i['price']) if 'price' in i else 0.0,
        }
        if 'discount_price' in i:
            result_item['discount_price'] = float(i['discount_price'])
        result_items.append(result_item)
    items_total = sum(
        float(i.get('discount_price', i['price'])) * i['count']
        for i in result_items
    )

    result = {
        'currency': _map_eats_to_market_currency(
            cart['country']['currency']['code'],
        ),
        'delivery_time_minutes': int(cart['delivery_time']['min']),
        'items': result_items,
        'prices': {
            'items_total': items_total,
            'items_total_discount': round(
                float(cart['decimal_subtotal']) - items_total, 2,
            ),
            'items_total_before_discount': float(cart['decimal_subtotal']),
            'shipping_cost': (float(cart['decimal_delivery_fee'])),
            'total': float(cart['decimal_total']),
            'additional_fees': (
                additional_fees if additional_fees is not None else []
            ),
        },
        'shop_is_available': cart['place']['available'],
    }

    left_sum = 0
    if 'decimal_sum_to_free_delivery' in cart['requirements']:
        left_sum = float(cart['requirements']['decimal_sum_to_free_delivery'])
    result['prices']['left_for_free_delivery'] = left_sum

    errors = []
    if 'decimal_sum_to_min_order' in cart['requirements']:
        if float(cart['requirements']['decimal_sum_to_min_order']) > 0:
            errors.append('PriceInsufficient')
    for violated_constraint in cart['requirements']['violated_constraints']:
        if violated_constraint['type'] == 'max_weight':
            errors.append('WeightExceeded')
        elif violated_constraint['type'] == 'max_subtotal_cost':
            errors.append('PriceExceeded')
    if errors:
        result['errors'] = errors
        result['cart_created'] = False
    else:
        result['cart_created'] = True

    return result


def _verify_handler_response_json(response_json, expected_response):
    def _sort_response(response):
        response['items'].sort(key=lambda product: product['feed_offer_id'])
        if 'errors' in response:
            response['errors'].sort()
        return response

    assert _sort_response(response_json) == _sort_response(expected_response)


def _generate_eats_cart_response(
        items, has_errors=None, is_place_available=True,
):
    eats_cart_items = []
    for i in items:
        if not i['found']:
            continue

        discount_price = i.get('discount_price', None)
        promo_subtotal = (
            str(float(i['discount_price']) * i['cart_count'])
            if discount_price
            else None
        )

        cart_item = {
            'id': i['eats_cart_id'],
            'item_id': i['core_id'],
            'name': i['name'],
            'price': _decimal_to_int(i['price']),
            'decimal_price': i['price'],
            'promo_price': _decimal_to_int(discount_price),
            'decimal_promo_price': discount_price,
            'item_options': [],
            'quantity': i['cart_count'],
            'description': '',
            'weight': '400 г',
            'subtotal': str(float(i['price']) * i['cart_count']),
            'promo_subtotal': promo_subtotal,
            'place_menu_item': {
                'id': i['core_id'],
                'name': i['name'],
                'description': '',
                'available': i['cart_count'] > 0,
                'price': _decimal_to_int(i['price']),
                'decimal_price': i['price'],
                'promo_price': _decimal_to_int(discount_price),
                'decimal_promo_price': discount_price,
                'promo_types': [],
                'options_groups': [],
                'adult': False,
            },
        }
        eats_cart_items.append(cart_item)

    subtotal = str(sum([float(i['subtotal']) for i in eats_cart_items]))
    promo_subtotal = str(
        sum(
            [
                float(i['promo_subtotal'] or i['subtotal'])
                for i in eats_cart_items
            ],
        ),
    )
    delivery_cost = '149.50'
    total_cost = str(float(promo_subtotal) + float(delivery_cost))

    left_sum_to_min_delivery = '1000'
    if has_errors:
        left_sum_to_min_order = '100'
        violated_constraints = [
            {
                'type': 'max_weight',
                'title': 'Max Weight',
                'violation_message': '',
            },
            {
                'type': 'max_subtotal_cost',
                'title': 'Max Subtotal Cost',
                'violation_message': '',
            },
        ]
    else:
        left_sum_to_min_order = '0'
        violated_constraints = []

    return {
        'cart': {
            'items': eats_cart_items,
            'delivery_date_time': '27-07-2021 23:58',
            'delivery_date_time_iso': '27-07-2021T23:58:00',
            'subtotal': _decimal_to_int(subtotal),
            'decimal_subtotal': subtotal,
            'discount': 0,
            'decimal_discount': '0',
            'delivery_fee': _decimal_to_int(delivery_cost),
            'decimal_delivery_fee': delivery_cost,
            'total': _decimal_to_int(total_cost),
            'decimal_total': total_cost,
            'delivery_time': {'min': 10, 'max': 50},
            'country': {
                'id': 35,
                'code': 'RU',
                'currency': {'code': EATS_CURRENCY, 'sign': '₽'},
            },
            'requirements': {
                'sum_to_free_delivery': _decimal_to_int(
                    left_sum_to_min_delivery,
                ),
                'decimal_sum_to_free_delivery': left_sum_to_min_delivery,
                'sum_to_min_order': _decimal_to_int(left_sum_to_min_order),
                'decimal_sum_to_min_order': left_sum_to_min_order,
                'violated_constraints': violated_constraints,
            },
            'updated_at': '27-07-2021 23:58',
            'available_time_picker': [
                [
                    '2021-04-03T11:00:00+03:00',
                    '2021-04-03T11:30:00+03:00',
                    '2021-04-03T12:00:00+03:00',
                    '2021-04-03T12:30:00+03:00',
                    '2021-04-03T13:00:00+03:00',
                    '2021-04-03T13:30:00+03:00',
                ],
                ['2021-04-04T11:00:00+03:00', '2021-04-04T11:30:00+03:00'],
            ],
            'place': {
                'address': 'улица Вавилова, 64/1с1',
                'available': is_place_available,
                'available_payment_methods': [3, 0, 2],
                'available_shipping_types': [
                    {'active': True, 'type': 'delivery'},
                ],
                'business': 'shop',
                'courier_options': [],
                'courier_type': 'pedestrian',
                'is_store': False,
                'market': False,
                'name': 'Some place',
                'slug': 'slug123456',
            },
            'place_slug': 'slug123456',
            'promos': [],
            'promo_items': [],
            'discount_promo': 0,
            'decimal_discount_promo': '0',
            'shipping_type': 'delivery',
            'charges': [],
            'additional_payments': [],
        },
    }


def _generate_handler_error_response(request_items, errors=None):
    response_items = []
    for request_item in request_items:
        response_items.append(
            {
                'feed_offer_id': request_item['nomenclature_item_id'],
                'count': 0,
                'price': 0,
                'found': False,
            },
        )
    response = {
        'cart_created': False,
        'delivery_time_minutes': 0,
        'currency': '',
        'prices': {
            'items_total': 0,
            'items_total_before_discount': 0,
            'items_total_discount': 0,
            'total': 0,
            'shipping_cost': 0,
            'left_for_free_delivery': 0,
            'additional_fees': [],
        },
        'items': response_items,
    }
    if errors:
        response['errors'] = errors

    return response


def _map_eats_to_market_currency(currency):
    if currency == EATS_CURRENCY:
        return MARKET_CURRENCY
    return MARKET_CURRENCY


def _decimal_to_int(value):
    if value is None:
        return None
    return int(float(value))


def _generate_db_init_data():
    brand1 = models.Brand(brand_id=int(BRAND_ID), slug=BRAND_ID)
    brand1.add_places([models.Place(place_id=PLACE_ID, slug=PLACE_SLUG)])

    market_brand_place = models.MarketBrandPlace(
        brand_id=int(BRAND_ID),
        place_id=PLACE_ID,
        business_id=BUSINESS_ID,
        partner_id=SHOP_ID,
        feed_id=SHOP_ID,
    )

    return {'brands': [brand1], 'market_brand_places': [market_brand_place]}


def _generate_places_info():
    places_info = [
        models.PlaceInfo(
            partner_id=SHOP_ID,
            place_id=PLACE_ID,
            place_name=PLACE_SLUG,
            assembly_cost=ASSEMBLY_COST,
        ),
    ]

    return places_info


def eats_places_set_init_places(eats_catalog_storage):
    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-12-24T06:00:00+00:00'),
            end=parser.parse('2021-12-24T18:00:00+00:00'),
        ),
    ]
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=ZONE_ID,
            place_id=int(PLACE_ID),
            working_intervals=open_schedule,
        ),
    )
