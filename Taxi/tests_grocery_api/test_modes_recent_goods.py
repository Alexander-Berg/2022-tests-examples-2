import pytest

from . import common
from . import const
from . import experiments

DEFAULT_LOCATION = const.LOCATION

DEFAULT_GROUP_REQUEST_BODY = {
    'modes': ['grocery'],
    'position': {'location': DEFAULT_LOCATION},
    'layout_id': 'layout-1',
    'group_id': 'category-group-some-id',
    'offer_id': 'some-offer-id',
}

DEFAULT_CATEGORY_REQUEST_BODY = {
    'modes': ['grocery'],
    'position': {'location': DEFAULT_LOCATION},
    'category_path': {
        'layout_id': 'layout-1',
        'group_id': 'category-group-some-id',
    },
    'category_id': 'virtual-category-some-id',
    'offer_id': 'some-offer-id',
}

HANDLERS = pytest.mark.parametrize(
    'test_handler,request_body',
    [
        pytest.param(
            '/lavka/v1/api/v1/modes/category-group',
            DEFAULT_GROUP_REQUEST_BODY,
            id='category_group',
        ),
        pytest.param(
            '/lavka/v1/api/v1/modes/category',
            DEFAULT_CATEGORY_REQUEST_BODY,
            id='category',
        ),
    ],
)


def _validate_response(response, expected_products):
    assert [item['id'] for item in response['modes'][0]['items']] == [
        'virtual-category-some-id',
    ] + expected_products
    assert sorted(
        [item['id'] for item in response['modes'][0]['items']],
    ) == sorted([product['id'] for product in response['products']])


def _prepare_test_context(overlord_catalog, grocery_products, load_json):
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, DEFAULT_LOCATION,
    )
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='some-id')
    category_group.add_virtual_category(
        test_id='some-id', special_category='recent-purchases',
    )


@experiments.RECENT_GOODS_EXP
@HANDLERS
async def test_recent_goods(
        taxi_grocery_api,
        grocery_fav_goods,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
):
    _prepare_test_context(overlord_catalog, grocery_products, load_json)

    product_ids = ['product-1', 'product-2']

    grocery_fav_goods.setup_request_checking(
        yandex_uid=common.DEFAULT_HEADERS['X-Yandex-UID'],
    )
    grocery_fav_goods.set_response_product_ids(product_ids=product_ids)

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    _validate_response(response.json(), product_ids)

    assert grocery_fav_goods.recent_goods_check_presence_times_called == 1
    assert grocery_fav_goods.recent_goods_get_times_called == 1


@experiments.SHOW_SOLD_OUT_ENABLED
@experiments.RECENT_GOODS_EXP
@HANDLERS
async def test_recent_goods_sold_out(
        taxi_grocery_api,
        grocery_fav_goods,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
):
    _prepare_test_context(overlord_catalog, grocery_products, load_json)

    # product-3 - рапсроданный
    product_ids = ['product-1', 'product-3', 'product-2']
    product_ids_expected = ['product-1', 'product-2', 'product-3']

    grocery_fav_goods.setup_request_checking(
        yandex_uid=common.DEFAULT_HEADERS['X-Yandex-UID'],
    )
    grocery_fav_goods.set_response_product_ids(product_ids=product_ids)

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    _validate_response(response.json(), product_ids_expected)
    for item in response.json()['products']:
        if item['id'] == 'product-3':
            assert not item['available']

    assert grocery_fav_goods.recent_goods_check_presence_times_called == 1
    assert grocery_fav_goods.recent_goods_get_times_called == 1


@pytest.mark.parametrize(
    'fav_goods_handler', ('recent-goods/check-presence', 'recent-goods/get'),
)
@pytest.mark.parametrize('fav_goods_problem', ('timeout', 500, 404, 400))
@experiments.RECENT_GOODS_EXP
@HANDLERS
async def test_recent_goods_fav_goods_problems(
        taxi_grocery_api,
        grocery_fav_goods,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
        fav_goods_handler,
        fav_goods_problem,
):
    _prepare_test_context(overlord_catalog, grocery_products, load_json)

    grocery_fav_goods.set_response_product_ids(product_ids=['product_id'])

    if fav_goods_problem == 'timeout':
        grocery_fav_goods.set_to_raise_timeout(handler_name=fav_goods_handler)
    else:
        grocery_fav_goods.set_error_status(
            handler_name=fav_goods_handler, error_status=fav_goods_problem,
        )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    _validate_response(response.json(), [])

    assert grocery_fav_goods.recent_goods_check_presence_times_called == 1
    if fav_goods_handler == 'recent-goods/check-presence':
        assert grocery_fav_goods.recent_goods_get_times_called == 0
    else:
        assert grocery_fav_goods.recent_goods_get_times_called == 1


@experiments.RECENT_GOODS_EXP
@HANDLERS
async def test_recent_goods_empty(
        taxi_grocery_api,
        grocery_fav_goods,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
):
    _prepare_test_context(overlord_catalog, grocery_products, load_json)

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    _validate_response(response.json(), [])

    assert grocery_fav_goods.recent_goods_check_presence_times_called == 1
    assert grocery_fav_goods.recent_goods_get_times_called == 0


@experiments.parametrize_recent_goods_exp(always_enabled=True)
@HANDLERS
async def test_recent_goods_always_enabled(
        taxi_grocery_api,
        grocery_fav_goods,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
):
    _prepare_test_context(overlord_catalog, grocery_products, load_json)

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    _validate_response(response.json(), [])

    assert grocery_fav_goods.recent_goods_check_presence_times_called == 1
    assert grocery_fav_goods.recent_goods_get_times_called == 1
