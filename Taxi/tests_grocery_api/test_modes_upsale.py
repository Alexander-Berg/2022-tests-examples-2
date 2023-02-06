from grocery_mocks import grocery_upsale as upsale  # pylint: disable=E0401
import pytest

from . import common
from . import conftest
from . import const
from . import experiments
from . import tests_headers

GROCERY_UPSALE_FALLBACK = pytest.mark.config(
    GROCERY_SUGGEST_COMPLEMENT_CANDIDATES_DEFAULT={
        '__default__': ['product-1'],
        'custom': [
            {
                'candidates': ['product-2'],
                'name': 'paris_london',
                'place_ids': ['321'],
            },
        ],
    },
)

# сценарий когда получаем upsale для карточки товара при пустой корзине;
# также проверяется, что в респонс не попадают продукты с нулевыми остатками
@experiments.SHOW_SOLD_OUT_ENABLED
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud',
    [
        pytest.param(False, True, marks=experiments.ANTIFRAUD_CHECK_DISABLED),
        pytest.param(True, False, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
        pytest.param(True, True, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
    ],
)
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_upsale_item(
        taxi_grocery_api,
        overlord_catalog,
        antifraud,
        grocery_marketing,
        grocery_p13n,
        load_json,
        grocery_upsale,
        antifraud_enabled,
        is_fraud,
):
    location = const.LOCATION
    yandex_uid = tests_headers.HEADER_YANDEX_UID
    orders_count = 2 if not antifraud_enabled else None

    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count, user_id=yandex_uid,
    )

    grocery_upsale.add_product('product-1')

    # sold out product
    grocery_upsale.add_product('product-3')

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_upsale.set_request_check(
        product_ids=['product-2'],
        request_source=upsale.UpsaleRequestSource.item_page,
    )
    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(orders_count),
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'position': {'location': location},
            'products': ['product-2'],
            'additional_data': common.DEFAULT_ADDITIONAL_DATA,
        },
        headers={
            'X-Yandex-UID': yandex_uid,
            'Accept-Language': 'ru',
            'User-Agent': common.DEFAULT_USER_AGENT,
        },
    )
    assert response.status_code == 200

    assert grocery_p13n.discount_modifiers_times_called == 1
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )

    data = response.json()
    assert data['items'][0]['products'][0] == {
        'available': True,
        'description': 'product-1-description',
        'id': 'product-1',
        'image_url_template': 'product-1-image-url-template',
        'image_url_templates': ['product-1-image-url-template'],
        'pricing': {'price': '2', 'price_template': '2 $SIGN$$CURRENCY$'},
        'quantity_limit': '5',
        'title': 'product-1-title',
        'long_title': 'product-1-long-title',
        'private_label': True,
        'type': 'good',
    }

    assert data['items'][0]['type'] == 'item'

    assert grocery_upsale.umlaas_called == 1


# сценарий когда получаем upsale для корзины
# возвращается две "карусели" - полученные при запросе в сервис апсейла
# с разными параметрами - cart_page и cart_page_v2
async def test_upsale_cart(
        taxi_grocery_api, overlord_catalog, load_json, grocery_upsale,
):
    location = const.LOCATION

    grocery_upsale.add_product_with_source(
        'product-1', upsale.UpsaleRequestSource.cart_page,
    )

    grocery_upsale.add_product_with_source(
        'product-2', upsale.UpsaleRequestSource.cart_page_v2,
    )

    grocery_upsale.add_product_with_source(
        'product-3', upsale.UpsaleRequestSource.tableware,
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
            {
                'in_stock': '10',
                'product_id': 'product-2',
                'quantity_limit': '10',
            },
            {
                'in_stock': '10',
                'product_id': 'product-3',
                'quantity_limit': '15',
            },
        ],
    )

    grocery_upsale.set_request_check(
        cart_items=['product-2'],
        request_source=upsale.UpsaleRequestSource.cart_page,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'position': {'location': location},
            'cart': {'cart_items': [{'product_id': 'product-2'}]},
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert [
        [product['id'] for product in item['products']]
        for item in data['items']
    ] == [['product-1'], ['product-2'], ['product-3']]
    assert grocery_upsale.umlaas_called == 3

    assert [item['type'] for item in data['items']] == [
        'cart',
        'cart_v2',
        'tableware',
    ]


@pytest.mark.parametrize(
    'target_cart_items,expected_response',
    [
        pytest.param(['cart'], [['product-1']]),
        pytest.param(['cart_v2'], [['product-2']]),
        pytest.param(['tableware'], [['product-3']]),
        pytest.param(['cart', 'cart_v2'], [['product-1'], ['product-2']]),
        pytest.param(None, [['product-1'], ['product-2'], ['product-3']]),
        pytest.param(
            ['cart', 'cart_v2', 'tableware'],
            [['product-1'], ['product-2'], ['product-3']],
        ),
        pytest.param([], []),
    ],
)
async def test_upsale_filter(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        grocery_upsale,
        target_cart_items,
        expected_response,
):
    location = const.LOCATION

    grocery_upsale.add_product_with_source(
        'product-1', upsale.UpsaleRequestSource.cart_page,
    )

    grocery_upsale.add_product_with_source(
        'product-2', upsale.UpsaleRequestSource.cart_page_v2,
    )

    grocery_upsale.add_product_with_source(
        'product-3', upsale.UpsaleRequestSource.tableware,
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
            {
                'in_stock': '10',
                'product_id': 'product-2',
                'quantity_limit': '10',
            },
            {
                'in_stock': '10',
                'product_id': 'product-3',
                'quantity_limit': '15',
            },
        ],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'target_cart_items': target_cart_items,
            'position': {'location': location},
            'cart': {'cart_items': [{'product_id': 'product-2'}]},
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert [
        [product['id'] for product in item['products']]
        for item in data['items']
    ] == expected_response

    assert grocery_upsale.umlaas_called == len(expected_response)


# Проверяем fallback когда получаем upsale для корзины
# 1) Если неудачен запрос с cart_page, используем фолбек - GROCERY_SUGGEST_ML
# 2) Если неудачен запрос с cart_page_v2, не используем фолбек
# 3) Если неудачны оба, используем фолбек только для cart_page
@GROCERY_UPSALE_FALLBACK
@pytest.mark.parametrize(
    'upsale_source,expected_response',
    [
        pytest.param(
            {upsale.UpsaleRequestSource.cart_page},
            [('cart', ['product-1']), ('cart_v2', ['product-2'])],
            id='cart fail',
        ),
        pytest.param(
            {upsale.UpsaleRequestSource.cart_page_v2},
            [('cart', ['product-1'])],
            id='cart_v2 fail',
        ),
        pytest.param(
            {
                upsale.UpsaleRequestSource.cart_page,
                upsale.UpsaleRequestSource.cart_page_v2,
            },
            [('cart', ['product-1'])],
            id='both fail',
        ),
    ],
)
async def test_upsale_cart_fallbacks(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        grocery_upsale,
        upsale_source,
        expected_response,
):
    location = const.LOCATION

    grocery_upsale.set_response_type(error_on_source=upsale_source)

    if upsale.UpsaleRequestSource.cart_page not in upsale_source:
        grocery_upsale.add_product_with_source(
            'product-1', upsale.UpsaleRequestSource.cart_page,
        )

    if upsale.UpsaleRequestSource.cart_page_v2 not in upsale_source:
        grocery_upsale.add_product_with_source(
            'product-2', upsale.UpsaleRequestSource.cart_page_v2,
        )

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_upsale.set_request_check(
        cart_items=['product-3'],
        request_source=upsale.UpsaleRequestSource.cart_page,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'position': {'location': location},
            'cart': {'cart_items': [{'product_id': 'product-3'}]},
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert [
        (item['type'], [product['id'] for product in item['products']])
        for item in data['items']
    ] == expected_response
    assert grocery_upsale.umlaas_called == 3


# сценарий когда корзина не пуста, и нужен upsale для карточки товара
async def test_upsale_item_with_cart(
        taxi_grocery_api, overlord_catalog, load_json, grocery_upsale,
):
    location = const.LOCATION
    grocery_upsale.add_product('product-1')
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_upsale.set_request_check(
        product_ids=['product-2'],
        cart_items=['product-3'],
        request_source=upsale.UpsaleRequestSource.item_page,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'position': {'location': location},
            'products': ['product-2'],
            'cart': {'cart_items': [{'product_id': 'product-3'}]},
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['items'][0]['products'][0]['id'] == 'product-1'
    assert data['items'][0]['type'] == 'item'

    assert grocery_upsale.umlaas_called == 1


async def test_upsale_complement_for_user(
        taxi_grocery_api, overlord_catalog, load_json, grocery_upsale,
):
    location = const.LOCATION
    grocery_upsale.add_product('product-1')
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_upsale.set_request_check(
        product_ids=[], request_source=upsale.UpsaleRequestSource.menu_page,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={'position': {'location': location}, 'complement_for_user': True},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['items'][0]['products'][0]['id'] == 'product-1'
    assert data['items'][0]['type'] == 'menu'

    assert grocery_upsale.umlaas_called == 1


# ml ручки возвращают ошибки, фолбек - конфиг grocery_suggest_ml
@GROCERY_UPSALE_FALLBACK
async def test_upsale_fallback(
        taxi_grocery_api, overlord_catalog, load_json, grocery_upsale,
):
    location = const.LOCATION

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_upsale.set_response_type(is_error=True)
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={'position': {'location': location}, 'products': ['product-2']},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()

    assert data['items'][0]['products'][0]['id'] == 'product-1'
    assert data['items'][0]['type'] == 'item'

    assert grocery_upsale.umlaas_called != 0


# Используем конфиг GROCERY_SUGGEST_COMPLEMENT_CANDIDATES_DEFAULT
# для получения продуктов по id депота
@GROCERY_UPSALE_FALLBACK
async def test_upsale_fallback_custom(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        grocery_upsale,
        grocery_depots,
):
    location = const.LOCATION
    legacy_depot_id = '321'

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id), depot_id=const.DEPOT_ID,
    )

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, legacy_depot_id=legacy_depot_id,
    )
    grocery_upsale.set_response_type(is_error=True)

    await taxi_grocery_api.invalidate_caches()

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={'position': {'location': location}, 'products': ['product-1']},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()

    assert data['items'][0]['products'][0]['id'] == 'product-2'
    assert data['items'][0]['type'] == 'item'

    assert grocery_upsale.umlaas_called != 0


# Порядок элементов в апсейле такой же, как в ручке сервиса апсейла.
async def test_upsale_order_is_preserved(
        taxi_grocery_api, grocery_upsale, overlord_catalog, load_json,
):
    upsale_ids = ['product-1', 'product-2', 'product-3']
    grocery_upsale.add_products(upsale_ids)

    stocks = [
        {'in_stock': '10', 'product_id': 'product-1', 'quantity_limit': '5'},
        {'in_stock': '10', 'product_id': 'product-2', 'quantity_limit': '10'},
        {'in_stock': '10', 'product_id': 'product-3', 'quantity_limit': '15'},
    ]

    location = common.DEFAULT_LOCATION
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, product_stocks=stocks,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={'position': {'location': location}, 'products': ['product-1']},
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert [
        item['id'] for item in response.json()['items'][0]['products']
    ] == upsale_ids


# Проверяем что выдача апсейла помечается лайками.
async def test_upsale_favorites(
        taxi_grocery_api,
        grocery_upsale,
        overlord_catalog,
        load_json,
        grocery_fav_goods,
):
    product_id = 'product-1'
    grocery_upsale.add_products([product_id])

    stocks = [
        {'in_stock': '10', 'product_id': product_id, 'quantity_limit': '5'},
    ]

    location = common.DEFAULT_LOCATION
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, product_stocks=stocks,
    )
    grocery_fav_goods.add_favorite(
        yandex_uid=common.DEFAULT_UID, product_id=product_id,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={'position': {'location': location}, 'products': ['product-1']},
        headers={'X-Yandex-UID': common.DEFAULT_UID},
    )
    assert response.status_code == 200
    product = response.json()['items'][0]['products'][0]
    assert product['is_favorite']


# Проверяем, что выдаются замены для товара.
async def test_upsale_substitutions(
        taxi_grocery_api, grocery_upsale, overlord_catalog, load_json,
):
    product_id = 'product-1'
    substitutions = ['product-2', 'product-3']
    grocery_upsale.add_product_substitutions(substitutions)

    stocks = [
        {'in_stock': '10', 'product_id': product_id, 'quantity_limit': '5'},
        {'in_stock': '10', 'product_id': 'product-2', 'quantity_limit': '5'},
        {'in_stock': '10', 'product_id': 'product-3', 'quantity_limit': '5'},
    ]

    location = common.DEFAULT_LOCATION
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, product_stocks=stocks,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'position': {'location': location},
            'products': [product_id],
            'suggest_type': 'substitute',
        },
        headers={'X-Yandex-UID': common.DEFAULT_UID},
    )
    assert response.status_code == 200
    assert [
        item['id'] for item in response.json()['items'][0]['products']
    ] == substitutions


# Проверяем, что отдаем 400 если товаров больше 1.
async def test_upsale_substitutions_incorrect_size(
        taxi_grocery_api, grocery_upsale, overlord_catalog, load_json,
):
    substitutions = ['product-3']
    grocery_upsale.add_product_substitutions(substitutions)

    stocks = [
        {'in_stock': '10', 'product_id': 'product-1', 'quantity_limit': '5'},
        {'in_stock': '10', 'product_id': 'product-2', 'quantity_limit': '5'},
        {'in_stock': '10', 'product_id': 'product-3', 'quantity_limit': '5'},
    ]

    location = common.DEFAULT_LOCATION
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, product_stocks=stocks,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'position': {'location': location},
            'products': ['product-1', 'product-2'],
            'suggest_type': 'substitute',
        },
        headers={'X-Yandex-UID': common.DEFAULT_UID},
    )
    assert response.status_code == 400


# Проверка 'catalog_paths' в ответе ручки
@pytest.mark.parametrize(
    'layout_id',
    [
        pytest.param(
            'layout-1', marks=experiments.create_modes_layouts_exp('layout-1'),
        ),
        pytest.param(
            'layout-2', marks=experiments.create_modes_layouts_exp('layout-2'),
        ),
    ],
)
@pytest.mark.parametrize('need_catalog_paths', [None, False, True])
async def test_catalog_paths(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_upsale,
        layout_id,
        need_catalog_paths,
):
    product_id = 'some-product-id'
    common.setup_catalog_for_paths_test(
        overlord_catalog, grocery_products, product_id,
    )

    grocery_upsale.add_product(product_id)

    headers = {'Accept-Language': 'en'}
    request_body = {
        'position': {'location': common.DEFAULT_LOCATION},
        'products': [product_id],
    }
    if need_catalog_paths is not None:
        request_body['need_catalog_paths'] = need_catalog_paths

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale', headers=headers, json=request_body,
    )
    assert response.status_code == 200
    response_data = response.json()

    assert response_data['items'][0]['type'] == 'item'
    assert grocery_upsale.umlaas_called == 1
    if need_catalog_paths is True:
        assert 'catalog_paths' in response_data['items'][0]['products'][0]
        common.check_catalog_paths(
            response_data['items'][0]['products'][0]['catalog_paths'],
            layout_id,
        )
    else:
        assert 'catalog_paths' not in response_data['items'][0]['products'][0]
