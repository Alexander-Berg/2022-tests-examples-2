# pylint: disable=pointless-string-statement, too-many-lines
import pytest

from . import utils

HANDLE_V1 = '/4.0/eats-picker/api/v1/order/soft-check'
HANDLE_V2 = '/4.0/eats-picker/api/v2/order/soft-check'


EATS_ID = '123456-123456'
PICKER_ID = '1234567'
PLACE_ID = '123456'
BRAND_ID = '12345'
SOFT_CHECK_VALUE = '123'
SOFT_CHECK_CART_VERSION = 1
PARTNER_ORDER_ID = '12345'
NOW = '2021-07-29T16:00:00+03:00'
NOW_UTC = '2021-07-29T13:00:00+00:00'
GLOBUS_LOCK_FAKE_EATS_ID = 'globus-eats-id'


def create_order_with_items(
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
):
    order_id = create_order(**order)
    if order_items and create_order_item:
        for order_item in order_items:
            order_item_id = create_order_item(order_id=order_id, **order_item)
            eats_item_id = order_item['eats_item_id']
            if (
                    picked_items
                    and create_picked_item
                    and eats_item_id in picked_items
            ):
                picked_item = picked_items[eats_item_id]
                picked_item_id = create_picked_item(
                    order_item_id=order_item_id,
                    eats_item_id=eats_item_id,
                    **picked_item,
                )
                if create_picked_item_position and picked_items_positions:
                    picked_item_positions = picked_items_positions[
                        eats_item_id
                    ]
                    for picked_item_position in picked_item_positions:
                        create_picked_item_position(
                            picked_item_id,
                            picked_item_position['weight'],
                            picked_item_position['count'],
                            picked_item_position.get('barcode'),
                            picked_item_position.get('mark'),
                        )
    return order_id


async def get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items=None,
        picked_items=None,
        picked_items_positions=None,
        create_order=None,
        create_order_item=None,
        create_picked_item=None,
        create_picked_item_position=None,
        create_order_soft_check=None,
        cart_version=None,
):
    if create_order:
        order_id = create_order_with_items(
            order,
            order_items,
            picked_items,
            picked_items_positions,
            create_order,
            create_order_item,
            create_picked_item,
            create_picked_item_position,
        )

        if create_order_soft_check:
            create_order_soft_check(
                order_id,
                order['eats_id'],
                SOFT_CHECK_CART_VERSION,
                order['picker_id'],
                SOFT_CHECK_VALUE,
                place_id=order.get('place_id'),
                brand_id=order.get('brand_id'),
            )

    request_body = {'order_nr': order['eats_id']}
    if handle == HANDLE_V1:
        request_body['picker_items'] = soft_check_items
    elif cart_version is not None:
        request_body['cart_version'] = cart_version

    return await taxi_eats_picker_orders.post(
        handle,
        headers=utils.da_headers(order['picker_id']),
        json=request_body,
    )


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.metro_soft_check_config(enabled=False)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_metro_disabled_config(
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        create_order_soft_check,
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        handle,
):
    """
        Конфиг выключен. Возвращаем софт-чек без запросов в интеграции
    """

    await taxi_eats_picker_orders.tests_control(reset_metrics=True)

    order = {'eats_id': EATS_ID, 'picker_id': PICKER_ID, 'state': 'picking'}
    order_items = [{'eats_item_id': 'РН000001', 'sku': 'РН000001'}]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
        },
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 1,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        None,
        create_order,
        create_order_item,
        create_picked_item,
        None,
        create_order_soft_check,
    )

    assert response.status == 200
    assert response.json()['payload']['payload']['value'] == SOFT_CHECK_VALUE

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.metro_soft_check_config(enabled=True)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_metro_picked_items_lookup_200(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        handle,
):
    """
        Не получаем ни одного товара из METRO успешно, заказ не создается
    """

    await taxi_eats_picker_orders.tests_control(reset_metrics=True)

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def mock_cart_confirmation(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': None,
                    'payload': {'type': 'code128', 'value': SOFT_CHECK_VALUE},
                },
            },
        )

    @mockserver.json_handler('/eats-integration-workers/v1/article-lookup')
    def mock_metro_article_lookup(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        assert request.json['article_details']['weight'] == '0.2'
        return mockserver.make_response(
            status=400, json={'code': '', 'message': ''},
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
    }
    order_items = [
        {'eats_item_id': 'РН000001', 'sku': 'РН000001'},
        {'eats_item_id': 'РН000002', 'sku': 'РН000002'},
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '200',
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '200',
        },
    }
    soft_check_items = [
        {'id': 'РН000001', 'measure': {'value': 200, 'unit': 'gramm'}},
        {'id': 'РН000002', 'measure': {'value': 200, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        None,
        create_order,
        create_order_item,
        create_picked_item,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 1
    assert mock_metro_article_lookup.times_called == 2

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 2
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 1
    )


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.metro_soft_check_config(enabled=True)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_metro_create_order_200(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        handle,
):
    """
        Успешно получаем 1 штучный товар из METRO, но ручка создания заказа
        возвращает ошибку
    """

    await taxi_eats_picker_orders.tests_control(reset_metrics=True)

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def mock_cart_confirmation(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': None,
                    'payload': {'type': 'code128', 'value': SOFT_CHECK_VALUE},
                },
            },
        )

    @mockserver.json_handler('/eats-integration-workers/v1/article-lookup')
    def mock_metro_article_lookup(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        if request.json['article_details']['barcode'] == 'РН000001':
            assert 'weight' not in request.json['article_details']
            return mockserver.make_response(
                status=200,
                json={'id': 'РН000001', 'quantity': '1.0', 'weight': '0.0'},
            )
        assert request.json['article_details']['barcode'] == 'РН000002'
        assert request.json['article_details']['weight'] == '1.5'
        return mockserver.make_response(
            status=400, json={'code': '', 'message': ''},
        )

    @mockserver.json_handler('/eats-integration-workers/v1/create-order')
    def mock_metro_create_order(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        assert request.json['items'] == [
            {'sequence_number': 1, 'barcode': 'РН000001', 'quantity': '5'},
        ]
        return mockserver.make_response(
            status=400, json={'code': '', 'message': ''},
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
    }
    order_items = [
        {'eats_item_id': 'РН000001', 'sku': 'РН000001'},
        {'eats_item_id': 'РН000002', 'sku': 'РН000002'},
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1500',
        },
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        None,
        create_order,
        create_order_item,
        create_picked_item,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 1
    assert mock_metro_create_order.times_called == 1
    assert mock_metro_article_lookup.times_called == 2

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 1
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 1
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.metro_soft_check_config(enabled=True, items_search_tasks_count=1)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_metro_picked_create_order_200(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        get_order_by_eats_id,
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        handle,
):
    """
        Получаем 1 весовой товар из METRO, создаем заказ успешно
    """

    await taxi_eats_picker_orders.tests_control(reset_metrics=True)

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def mock_cart_confirmation(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': None,
                    'payload': {'type': 'code128', 'value': SOFT_CHECK_VALUE},
                },
            },
        )

    @mockserver.json_handler('/eats-integration-workers/v1/article-lookup')
    def mock_metro_article_lookup(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        if request.json['article_details']['barcode'] == 'РН000002':
            assert request.json['article_details']['weight'] == '1.5'
            return mockserver.make_response(
                status=200,
                json={'id': 'РН000002', 'quantity': '1.0', 'weight': '1.5'},
            )
        assert request.json['article_details']['barcode'] == 'РН000001'
        assert 'weight' not in request.json['article_details']
        return mockserver.make_response(
            status=400, json={'code': '', 'message': ''},
        )

    @mockserver.json_handler('/eats-integration-workers/v1/create-order')
    def mock_metro_create_order(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        assert request.json['items'] == [
            {
                'sequence_number': 1,
                'barcode': 'РН000002',
                'quantity': '1',
                'weight': '1.5',
            },
        ]
        return mockserver.make_response(
            status=200,
            json={
                'trx_number': request.json['trx_number'],
                'order_id': PARTNER_ORDER_ID,
                'customer_barcode': request.json['customer_barcode'],
            },
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
    }
    order_items = [
        {'eats_item_id': 'РН000001', 'sku': 'РН000001'},
        {'eats_item_id': 'РН000002', 'sku': 'РН000002'},
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1500',
        },
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        None,
        create_order,
        create_order_item,
        create_picked_item,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 1
    assert mock_metro_create_order.times_called == 1
    assert mock_metro_article_lookup.times_called == 2

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 1
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION + 1},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION + 1
    assert len(cart.json()['picker_items']) == 2
    for picker_item in cart.json()['picker_items']:
        if picker_item['id'] == 'РН000001':
            assert 'sent_to_partner' not in picker_item
            continue
        if picker_item['id'] == 'РН000002':
            assert picker_item['sent_to_partner'] is True
            continue
        assert False


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.metro_soft_check_config(enabled=True, items_search_tasks_count=1)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_metro_soft_check_exists_200(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_order_soft_check,
        get_order_by_eats_id,
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        handle,
):
    """
        Отдаем уже существующий софт-чек, не ходим в METRO
    """

    await taxi_eats_picker_orders.tests_control(reset_metrics=True)

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'partner_order_id': PARTNER_ORDER_ID,
    }
    order_items = [
        {'eats_item_id': 'РН000001', 'sku': 'РН000001'},
        {'eats_item_id': 'РН000002', 'sku': 'РН000002'},
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1500',
            'sent_to_partner': True,
        },
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        None,
        create_order,
        create_order_item,
        create_picked_item,
        None,
        create_order_soft_check,
    )

    assert response.status == 200

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION
    assert len(cart.json()['picker_items']) == 2
    for picker_item in cart.json()['picker_items']:
        if picker_item['id'] == 'РН000001':
            assert 'sent_to_partner' not in picker_item
            continue
        if picker_item['id'] == 'РН000002':
            assert picker_item['sent_to_partner'] is True
            continue
        assert False


@utils.metro_soft_check_config(enabled=True, items_search_tasks_count=1)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_v1_metro_picked_create_order_multiple_times(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_order_soft_check,
        get_order_by_eats_id,
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
):
    """
        1) Отдаем уже существующий софт-чек
    """

    await taxi_eats_picker_orders.tests_control(reset_metrics=True)

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def mock_cart_confirmation(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': None,
                    'payload': {'type': 'code128', 'value': SOFT_CHECK_VALUE},
                },
            },
        )

    @mockserver.json_handler('/eats-integration-workers/v1/article-lookup')
    def mock_metro_article_lookup(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        if request.json['article_details']['barcode'] == 'РН000002':
            assert request.json['article_details']['weight'] == '1.5'
            return mockserver.make_response(
                status=200,
                json={'id': 'РН000002', 'quantity': '1.0', 'weight': '1.5'},
            )
        assert request.json['article_details']['barcode'] == 'РН000001'
        assert 'weight' not in request.json['article_details']
        return mockserver.make_response(
            status=400, json={'code': '', 'message': ''},
        )

    @mockserver.json_handler('/eats-integration-workers/v1/create-order')
    def mock_metro_create_order(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        assert request.json['items'] == [
            {
                'sequence_number': 1,
                'barcode': 'РН000002',
                'quantity': '1',
                'weight': '1.5',
            },
        ]
        return mockserver.make_response(
            status=200,
            json={
                'trx_number': request.json['trx_number'],
                'order_id': PARTNER_ORDER_ID,
                'customer_barcode': request.json['customer_barcode'],
            },
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'partner_order_id': PARTNER_ORDER_ID,
    }
    order_items = [
        {'eats_item_id': 'РН000001', 'sku': 'РН000001'},
        {'eats_item_id': 'РН000002', 'sku': 'РН000002'},
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
            'sent_to_partner': True,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1500',
            'sent_to_partner': True,
        },
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        HANDLE_V1,
        soft_check_items,
        order,
        order_items,
        picked_items,
        None,
        create_order,
        create_order_item,
        create_picked_item,
        None,
        create_order_soft_check,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 0
    assert mock_metro_create_order.times_called == 0
    assert mock_metro_article_lookup.times_called == 0

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION
    assert len(cart.json()['picker_items']) == 2
    for picker_item in cart.json()['picker_items']:
        assert picker_item['sent_to_partner'] is True

    """
        Далее отправляем запрос на софт-чек с другим составом товаров, один из
        которых найден в METRO. Создается новый заказ в METRO с новым составом
    """

    soft_check_items = [
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders, HANDLE_V1, soft_check_items, order,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 1
    assert mock_metro_create_order.times_called == 1
    assert mock_metro_article_lookup.times_called == 1

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION + 1},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION + 1
    assert len(cart.json()['picker_items']) == 2
    for picker_item in cart.json()['picker_items']:
        if picker_item['id'] == 'РН000001':
            assert 'sent_to_partner' not in picker_item
            continue
        if picker_item['id'] == 'РН000002':
            assert picker_item['sent_to_partner'] is True
            continue
        assert False

    """
        Далее отправляем запрос на софт-чек с другим составом товаров, ни один
        из которых не найден в METRO. Возвращаем 200. Информация о заказе не
        меняется
    """

    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders, HANDLE_V1, soft_check_items, order,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 2
    assert mock_metro_create_order.times_called == 1
    assert mock_metro_article_lookup.times_called == 2

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 1
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 1
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION + 1},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION + 1
    assert len(cart.json()['picker_items']) == 2
    for picker_item in cart.json()['picker_items']:
        if picker_item['id'] == 'РН000001':
            assert 'sent_to_partner' not in picker_item
            continue
        if picker_item['id'] == 'РН000002':
            assert picker_item['sent_to_partner'] is True
            continue
        assert False


@utils.metro_soft_check_config(enabled=True, items_search_tasks_count=1)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_v2_metro_picked_create_order_multiple_times(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_order_soft_check,
        get_order_by_eats_id,
        get_order_item_by_eats_item_id,
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
):
    """
        1) Отдаем уже существующий софт-чек
    """

    await taxi_eats_picker_orders.tests_control(reset_metrics=True)

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def mock_cart_confirmation(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': None,
                    'payload': {'type': 'code128', 'value': SOFT_CHECK_VALUE},
                },
            },
        )

    @mockserver.json_handler('/eats-integration-workers/v1/article-lookup')
    def mock_metro_article_lookup(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        if request.json['article_details']['barcode'] == 'РН000002':
            assert request.json['article_details']['weight'] == '1.5'
            return mockserver.make_response(
                status=200,
                json={'id': 'РН000002', 'quantity': '1.0', 'weight': '1.5'},
            )
        assert request.json['article_details']['barcode'] == 'РН000001'
        assert 'weight' not in request.json['article_details']
        return mockserver.make_response(
            status=400, json={'code': '', 'message': ''},
        )

    @mockserver.json_handler('/eats-integration-workers/v1/create-order')
    def mock_metro_create_order(request):
        assert request.json['place_id'] == PLACE_ID
        assert request.json['customer_barcode'] == SOFT_CHECK_VALUE
        assert request.json['items'] == [
            {
                'sequence_number': 1,
                'barcode': 'РН000002',
                'quantity': '1',
                'weight': '1.5',
            },
        ]
        return mockserver.make_response(
            status=200,
            json={
                'trx_number': request.json['trx_number'],
                'order_id': PARTNER_ORDER_ID,
                'customer_barcode': request.json['customer_barcode'],
            },
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'partner_order_id': PARTNER_ORDER_ID,
    }
    order_items = [
        {'eats_item_id': 'РН000001', 'sku': 'РН000001'},
        {'eats_item_id': 'РН000002', 'sku': 'РН000002'},
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
            'sent_to_partner': True,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1500',
            'sent_to_partner': True,
        },
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        HANDLE_V2,
        soft_check_items,
        order,
        order_items,
        picked_items,
        None,
        create_order,
        create_order_item,
        create_picked_item,
        None,
        create_order_soft_check,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 0
    assert mock_metro_create_order.times_called == 0
    assert mock_metro_article_lookup.times_called == 0

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION
    assert len(cart.json()['picker_items']) == 2
    for picker_item in cart.json()['picker_items']:
        assert picker_item['sent_to_partner'] is True

    """
        Далее отправляем запрос на софт-чек с другим составом товаров, один из
        которых найден в METRO. Создается новый заказ в METRO с новым составом
    """

    picked_items = {
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION + 1,
            'weight': '1500',
            'sent_to_partner': True,
        },
    }
    soft_check_items = [
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    order_item_id = get_order_item_by_eats_item_id(
        get_order_by_eats_id(order['eats_id'])['id'], 'РН000002',
    )['id']
    create_picked_item(
        order_item_id=order_item_id,
        eats_item_id='РН000002',
        **picked_items['РН000002'],
    )

    response = await get_soft_check_response(
        taxi_eats_picker_orders, HANDLE_V2, soft_check_items, order,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 1
    assert mock_metro_create_order.times_called == 1
    assert mock_metro_article_lookup.times_called == 1

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 0
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION + 2},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION + 2
    assert len(cart.json()['picker_items']) == 1
    picker_item = cart.json()['picker_items'][0]
    assert picker_item['id'] == 'РН000002'
    assert picker_item['sent_to_partner'] is True

    """
        Далее отправляем запрос на софт-чек с другим составом товаров, ни один
        из которых не найден в METRO. Возвращаем 200. Информация о заказе не
        меняется
    """

    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION + 3,
            'count': 5,
        },
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
    ]

    order_item_id = get_order_item_by_eats_item_id(
        get_order_by_eats_id(order['eats_id'])['id'], 'РН000001',
    )['id']
    create_picked_item(
        order_item_id=order_item_id,
        eats_item_id='РН000001',
        **picked_items['РН000001'],
    )

    response = await get_soft_check_response(
        taxi_eats_picker_orders, HANDLE_V2, soft_check_items, order,
    )

    assert response.status == 200
    assert mock_cart_confirmation.times_called == 2
    assert mock_metro_create_order.times_called == 1
    assert mock_metro_article_lookup.times_called == 2

    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-failed-to-create-orders',
        )
        == 0
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-not-found-items',
        )
        == 1
    )
    assert (
        await taxi_eats_picker_orders_monitor.get_metric(
            'metro-found-zero-items',
        )
        == 1
    )

    assert (
        get_order_by_eats_id(EATS_ID)['partner_order_id'] == PARTNER_ORDER_ID
    )

    cart = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/cart?eats_id={EATS_ID}',
        headers=utils.da_headers(PICKER_ID),
        json={'cart_version': SOFT_CHECK_CART_VERSION + 3},
    )
    assert cart.json()['cart_version'] == SOFT_CHECK_CART_VERSION + 3
    assert len(cart.json()['picker_items']) == 1
    picker_item = cart.json()['picker_items'][0]
    assert picker_item['id'] == 'РН000001'
    assert 'sent_to_partner' not in picker_item


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.globus_soft_check_config(enabled=True, soft_check_enabled=True)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now(NOW)
async def test_get_soft_check_globus_first_404(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        taxi_eats_picker_orders,
        handle,
):
    """
        Получаем 404 от глобуса. Отвечам 409
    """

    @mockserver.json_handler('/eats-retail-globus-parser/v1/create-order')
    def mock_retail_globus_parser(request):
        assert request.json == {
            'place_id': PLACE_ID,
            'soft_check': {
                'discountsValue': '0',
                'dateCreated': NOW_UTC,
                'guid': 'VQ82000000',
                'isEditable': False,
                'status': 'READY_TO_PAYMENT',
                'totalPrice': '2.38',
                'positions': [
                    {
                        'barcode': 'barcode1',
                        'code': 'РН000001',
                        'positionOrder': 1,
                        'quantity': '5',
                        'vat': 0,
                        'unitPrice': '0.1',
                        'totalPrice': '0.5',
                        'discountValue': 0,
                        'isFixedDiscounts': True,
                        'isFixedPrice': True,
                        'isCatchWeight': False,
                        'calculationSubject': 1,
                    },
                    {
                        'barcode': 'barcode2',
                        'code': 'РН000002',
                        'positionOrder': 2,
                        'quantity': '3.75',
                        'vat': 0,
                        'unitPrice': '0.5',
                        'totalPrice': '1.88',
                        'discountValue': 0,
                        'isFixedDiscounts': True,
                        'isFixedPrice': True,
                        'isCatchWeight': True,
                        'calculationSubject': 1,
                    },
                ],
            },
        }
        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'barcodes': ['barcode1'],
            'price': 0.1,
            'sold_by_weight': False,
        },
        {
            'eats_item_id': 'РН000002',
            'sku': 'РН000002',
            'barcodes': ['barcode2'],
            'price': 0.2,
            'measure_value': 400,
            'sold_by_weight': True,
        },
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1500',
        },
    }
    picked_items_positions = {
        'РН000001': [{'count': 5, 'weight': None}],
        'РН000002': [{'count': None, 'weight': 3750}],
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 3750, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )

    assert response.status_code == 409
    assert mock_retail_globus_parser.times_called == 1


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.globus_soft_check_config(
    enabled=True, soft_check_enabled=True, retries=3,
)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now('2021-07-29T16:00:00+03:00')
async def test_get_soft_check_globus_retries_exceeded(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        taxi_eats_picker_orders,
        handle,
):
    """
        Получаем 409 на все попытки получения софт-чека. Возвращаем 500
    """

    @mockserver.json_handler('/eats-retail-globus-parser/v1/create-order')
    def mock_retail_globus_parser(request):
        guid = f'VQ8200000{mock_retail_globus_parser.times_called}'
        assert request.json == {
            'place_id': PLACE_ID,
            'soft_check': {
                'discountsValue': '0',
                'dateCreated': NOW_UTC,
                'guid': guid,
                'isEditable': False,
                'status': 'READY_TO_PAYMENT',
                'totalPrice': '1.25',
                'positions': [
                    {
                        'barcode': 'barcode1',
                        'code': 'РН000001',
                        'positionOrder': 1,
                        'quantity': '5',
                        'vat': 0,
                        'unitPrice': '0.1',
                        'totalPrice': '0.5',
                        'discountValue': 0,
                        'isFixedDiscounts': True,
                        'isFixedPrice': True,
                        'isCatchWeight': False,
                        'calculationSubject': 1,
                    },
                    {
                        'barcode': 'barcode2',
                        'code': 'РН000002',
                        'positionOrder': 2,
                        'quantity': '1.5',
                        'vat': 0,
                        'unitPrice': '0.5',
                        'totalPrice': '0.75',
                        'discountValue': 0,
                        'isFixedDiscounts': True,
                        'isFixedPrice': True,
                        'isCatchWeight': True,
                        'calculationSubject': 1,
                    },
                ],
            },
        }
        return mockserver.make_response(
            status=409, json={'code': '', 'message': ''},
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'barcodes': ['barcode1'],
            'sold_by_weight': False,
            'price': 0.1,
        },
        {
            'eats_item_id': 'РН000002',
            'sku': 'РН000002',
            'barcodes': ['barcode2'],
            'price': 0.2,
            'sold_by_weight': True,
            'measure_value': 400,
        },
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1500',
        },
    }
    picked_items_positions = {
        'РН000001': [{'count': 5, 'weight': None}],
        'РН000002': [{'count': None, 'weight': 1500}],
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )

    assert response.status_code == 500
    assert mock_retail_globus_parser.times_called == 3


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.globus_soft_check_config(enabled=True, soft_check_enabled=True)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now('2021-07-29T16:00:00+03:00')
async def test_get_soft_check_globus_403(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        taxi_eats_picker_orders,
        handle,
):
    """
        Получаем 403 на попытку получения софт-чека. Возвращаем 403
    """

    @mockserver.json_handler('/eats-retail-globus-parser/v1/create-order')
    def mock_retail_globus_parser(request):
        return mockserver.make_response(
            status=403, json={'code': '1030', 'message': 'Ошибка'},
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'barcodes': ['barcode1'],
            'sold_by_weight': False,
            'price': 0.1,
        },
        {
            'eats_item_id': 'РН000002',
            'sku': 'РН000002',
            'barcodes': ['barcode2'],
            'price': 0.2,
            'sold_by_weight': True,
            'measure_value': 400,
        },
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': 1500,
        },
    }
    picked_items_positions = {
        'РН000001': [
            {'count': 2, 'weight': None},
            {'count': 3, 'weight': None},
        ],
        'РН000002': [
            {'count': None, 'weight': 1000, 'barcode': 'barcode2.1'},
            {'count': None, 'weight': 200, 'barcode': 'barcode2.2'},
            {'count': None, 'weight': 300, 'barcode': 'barcode2.3'},
        ],
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )

    assert response.status_code == 403
    assert mock_retail_globus_parser.times_called == 1


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.globus_soft_check_config(enabled=True, soft_check_enabled=False)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now('2021-07-29T16:00:00+03:00')
async def test_get_soft_check_globus_410_soft_checks_unavailable(
        create_order, taxi_eats_picker_orders, handle,
):
    """
        Возвращаем 410, если софт-чеки глобуса выключены в конфиге
    """
    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }

    response = await get_soft_check_response(
        taxi_eats_picker_orders, handle, [], order, create_order=create_order,
    )

    assert response.status_code == 410


@utils.globus_soft_check_config(enabled=True, soft_check_enabled=False)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now('2021-07-29T16:00:00+03:00')
async def test_v2_get_soft_check_globus_410_no_valid_positions(
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        taxi_eats_picker_orders,
):
    """
        Возвращаем 410, если после фильтрации позиций не осталось ни одной
        для получения софт-чека
    """
    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'price': 0.1,
            'barcodes': ['barcode1'],
            'sold_by_weight': False,
            'require_marks': True,
        },
        {
            'eats_item_id': 'РН000002',
            'sku': 'РН000002',
            'barcodes': ['barcode2'],
            'price': 10,
            'measure_value': 1000,
            'sold_by_weight': True,
            'require_marks': True,
        },
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': 1500,
        },
    }
    picked_items_positions = {
        'РН000001': [
            {'count': 2, 'weight': None, 'mark': 'mark1'},
            {'count': 3, 'weight': None},
        ],
        'РН000002': [
            {'count': None, 'weight': 1000, 'barcode': 'barcode2.1'},
            {'count': None, 'weight': 200, 'barcode': 'barcode2.2'},
            {'count': None, 'weight': 300, 'barcode': 'barcode2.3'},
        ],
    }

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        HANDLE_V2,
        None,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )

    assert response.status == 410


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.globus_soft_check_config(
    enabled=True, soft_check_enabled=True, retries=3,
)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now(NOW)
async def test_get_soft_check_globus_retries(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        taxi_eats_picker_orders,
        handle,
):
    """
        Получаем 409 на две первые попытки. На последнюю получаем 200 и
        сохраняем софт-чек
    """

    @mockserver.json_handler('/eats-retail-globus-parser/v1/create-order')
    def mock_retail_globus_parser(request):
        guid = f'VQ8200000{mock_retail_globus_parser.times_called}'
        assert request.json == {
            'place_id': PLACE_ID,
            'soft_check': {
                'discountsValue': '0',
                'dateCreated': NOW_UTC,
                'guid': guid,
                'isEditable': False,
                'status': 'READY_TO_PAYMENT',
                'totalPrice': '1',
                'positions': [
                    {
                        'barcode': 'barcode1',
                        'code': 'РН000001',
                        'positionOrder': 1,
                        'quantity': '5',
                        'vat': 0,
                        'unitPrice': '0.1',
                        'totalPrice': '0.5',
                        'discountValue': 0,
                        'isFixedDiscounts': True,
                        'isFixedPrice': True,
                        'isCatchWeight': False,
                        'calculationSubject': 1,
                    },
                    {
                        'barcode': (
                            '012345'
                            if handle == HANDLE_V1
                            else '01234567890123'
                        ),
                        'code': 'РН000002',
                        'positionOrder': 2,
                        'quantity': '0.001',
                        'vat': 0,
                        'unitPrice': '500',
                        'totalPrice': '0.5',
                        'discountValue': 0,
                        'isFixedDiscounts': True,
                        'isFixedPrice': True,
                        'isCatchWeight': True,
                        'calculationSubject': 1,
                    },
                ],
            },
        }

        if mock_retail_globus_parser.times_called != 2:
            return mockserver.make_response(
                status=409, json={'code': '', 'message': ''},
            )
        return mockserver.make_response(
            status=200, json=request.json['soft_check'],
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'price': 0.1,
            'barcodes': ['barcode1'],
            'sold_by_weight': False,
        },
        {
            'eats_item_id': 'РН000002',
            'sku': 'РН000002',
            'barcodes': ['barcode2'],
            'price': 200,
            'measure_value': 400,
            'sold_by_weight': True,
        },
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': '1',
        },
    }
    picked_items_positions = {
        'РН000001': [{'count': 5, 'weight': None}],
        'РН000002': [
            {'count': None, 'weight': 1, 'barcode': '01234567890123'},
        ],
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {
            'id': 'РН000002',
            'barcode': '01234567890123',
            'measure': {'value': 1, 'unit': 'gramm'},
        },
    ]

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )

    assert response.status_code == 200
    assert response.json()['payload'] == {
        'payload': {'type': 'code128', 'value': 'VQ82000002'},
        'confirmation_type': 'barcode',
        'description': 'Софт-чек',
    }
    assert mock_retail_globus_parser.times_called == 3


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@utils.globus_soft_check_config(enabled=True, soft_check_enabled=True)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now(NOW)
async def test_get_soft_check_globus_increment(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        set_latest_globus_soft_check,
        get_latest_globus_soft_check,
        taxi_eats_picker_orders,
        handle,
):
    """
        Проверяем корректность генерации новых значений софт-чеков
    """

    @mockserver.json_handler('/eats-retail-globus-parser/v1/create-order')
    def mock_retail_globus_parser(request):
        assert request.json['soft_check']['guid'] == 'VQ82123457'
        return mockserver.make_response(
            status=200, json=request.json['soft_check'],
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'price': 0.1,
            'barcodes': ['barcode1'],
            'sold_by_weight': True,
        },
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
    }
    picked_items_positions = {
        'РН000001': [{'count': 5, 'weight': None}],
        'РН000002': [{'count': None, 'weight': 1500}],
    }
    soft_check_items = [
        {
            'id': 'РН000001',
            'count': 5,
            'measure': {'value': 1000, 'unit': 'gramm'},
        },
        {'id': 'РН000002', 'measure': {'value': 1500, 'unit': 'gramm'}},
    ]

    set_latest_globus_soft_check('VQ82123456')
    await get_soft_check_response(
        taxi_eats_picker_orders,
        handle,
        soft_check_items,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )
    assert get_latest_globus_soft_check() == 'VQ82123457'
    assert mock_retail_globus_parser.times_called == 1


@pytest.mark.parametrize(
    'weighted_marks',
    [
        (None, None, None),
        (None, 'mark1', 'mark2'),
        ('mark1', 'mark2', 'mark3'),
    ],
)
@utils.globus_soft_check_config(enabled=True, soft_check_enabled=True)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now(NOW)
async def test_get_soft_check_v2_globus_positions(
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        get_order_by_eats_id,
        get_order_items,
        get_picked_items,
        get_picked_item_positions,
        taxi_eats_picker_orders,
        weighted_marks,
):
    @mockserver.json_handler('/eats-retail-globus-parser/v1/create-order')
    def mock_retail_globus_parser(request):
        guid = f'VQ8200000{mock_retail_globus_parser.times_called}'
        position_counted = {
            'code': 'РН000001',
            'vat': 0,
            'unitPrice': '0.1',
            'discountValue': 0,
            'isFixedDiscounts': True,
            'isFixedPrice': True,
            'isCatchWeight': False,
            'calculationSubject': 1,
        }
        position_weighted = {
            'code': 'РН000002',
            'vat': 0,
            'unitPrice': '10',
            'discountValue': 0,
            'isFixedDiscounts': True,
            'isFixedPrice': True,
            'isCatchWeight': True,
            'calculationSubject': 1,
        }
        positions = [
            dict(
                position_counted,
                positionOrder=1,
                barcode='barcode1',
                quantity='2',
                totalPrice='0.2',
            ),
            dict(
                position_counted,
                positionOrder=2,
                barcode='barcode1',
                quantity='3',
                totalPrice='0.3',
            ),
        ]
        if sum([mark is not None for mark in weighted_marks]) == len(
                weighted_marks,
        ):
            positions += [
                dict(
                    position_weighted,
                    positionOrder=3,
                    barcode='barcode2.1',
                    quantity='1',
                    totalPrice='10',
                    mark=weighted_marks[0],
                    calculationSubject=33,
                ),
                dict(
                    position_weighted,
                    positionOrder=4,
                    barcode='barcode2.2',
                    quantity='0.2',
                    totalPrice='2',
                    mark=weighted_marks[1],
                    calculationSubject=33,
                ),
                dict(
                    position_weighted,
                    positionOrder=5,
                    barcode='barcode2.3',
                    quantity='0.3',
                    totalPrice='3',
                    mark=weighted_marks[2],
                    calculationSubject=33,
                ),
            ]
        assert request.json == {
            'place_id': PLACE_ID,
            'soft_check': {
                'guid': guid,
                'discountsValue': '0',
                'dateCreated': NOW_UTC,
                'isEditable': False,
                'status': 'READY_TO_PAYMENT',
                'totalPrice': str(
                    sum(
                        [
                            float(position['totalPrice'])
                            for position in positions
                        ],
                    ),
                ),
                'positions': positions,
            },
        }

        if mock_retail_globus_parser.times_called != 2:
            return mockserver.make_response(
                status=409, json={'code': '', 'message': ''},
            )
        return mockserver.make_response(
            status=200, json=request.json['soft_check'],
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'price': 0.1,
            'barcodes': ['barcode1'],
            'sold_by_weight': False,
        },
        {
            'eats_item_id': 'РН000002',
            'sku': 'РН000002',
            'barcodes': ['barcode2'],
            'price': 10,
            'measure_value': 1000,
            'sold_by_weight': True,
            'require_marks': True,
        },
    ]
    picked_items = {
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': 1500,
        },
    }
    picked_items_positions = {
        'РН000001': [
            {'count': 2, 'weight': None},
            {'count': 3, 'weight': None},
        ],
        'РН000002': [
            {
                'count': None,
                'weight': 1000,
                'barcode': 'barcode2.1',
                'mark': weighted_marks[0],
            },
            {
                'count': None,
                'weight': 200,
                'barcode': 'barcode2.2',
                'mark': weighted_marks[1],
            },
            {
                'count': None,
                'weight': 300,
                'barcode': 'barcode2.3',
                'mark': weighted_marks[2],
            },
        ],
    }

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        HANDLE_V2,
        None,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )

    assert mock_retail_globus_parser.times_called == 3

    assert response.status == 200

    order = get_order_by_eats_id(EATS_ID)
    order_items = get_order_items(order['id'])
    order_item_ids = tuple([item['id'] for item in order_items])
    picked_items = [
        item
        for item in get_picked_items(order_item_ids=order_item_ids)
        if item['cart_version'] == 2
    ]
    assert len(picked_items) == 2
    for picked_item in picked_items:
        picked_item_positions = get_picked_item_positions(picked_item['id'])
        if picked_item['eats_item_id'] == 'РН000001':
            assert picked_item['sent_to_partner'] is True
            assert len(picked_item_positions) == 2
        elif picked_item['eats_item_id'] == 'РН000002':
            if sum(mark is not None for mark in weighted_marks) == len(
                    weighted_marks,
            ):
                assert picked_item['sent_to_partner'] is True
            else:
                assert bool(picked_item['sent_to_partner']) is False
            assert len(picked_item_positions) == 3
        else:
            assert False


@utils.globus_soft_check_config(enabled=True, soft_check_enabled=True)
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.now(NOW)
@pytest.mark.parametrize('fix_enabled', [False, True])
async def test_get_soft_check_v2_globus_positions_temporary_quantity_fix(
        init_measure_units,
        mockserver,
        experiments3,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        taxi_eats_picker_orders,
        fix_enabled,
):
    if fix_enabled:
        experiments3.add_experiment3_from_marker(
            utils.soft_check_quantity_fix_experiment(True), None,
        )

    @mockserver.json_handler('/eats-retail-globus-parser/v1/create-order')
    def mock_retail_globus_parser(request):
        guid = f'VQ8200000{mock_retail_globus_parser.times_called}'
        position_template = {
            'vat': 0,
            'discountValue': 0,
            'isFixedDiscounts': True,
            'isFixedPrice': True,
            'isCatchWeight': False,
            'calculationSubject': 1,
        }
        positions = (
            (
                [
                    dict(
                        position_template,
                        code='РН000000',
                        barcode='barcode0',
                        unitPrice='1',
                        quantity='5',
                        totalPrice='5',
                    ),
                ]
                if fix_enabled
                else [
                    dict(
                        position_template,
                        code='РН000000',
                        barcode='barcode0',
                        unitPrice='1',
                        quantity='2',
                        totalPrice='2',
                    ),
                    dict(
                        position_template,
                        code='РН000000',
                        barcode='barcode0',
                        unitPrice='1',
                        quantity='2',
                        totalPrice='2',
                    ),
                ]
            )
            + [
                dict(
                    position_template,
                    code='РН000001',
                    barcode='barcode1.1',
                    unitPrice='1',
                    quantity='2',
                    totalPrice='2',
                ),
                dict(
                    position_template,
                    code='РН000001',
                    barcode='barcode1.2',
                    unitPrice='1',
                    quantity='2',
                    totalPrice='2',
                ),
                dict(
                    position_template,
                    code='РН000002',
                    barcode='barcode2',
                    unitPrice='1',
                    quantity='2',
                    totalPrice='2',
                    mark='mark2.1',
                    calculationSubject=33,
                ),
                dict(
                    position_template,
                    code='РН000002',
                    barcode='barcode2',
                    unitPrice='1',
                    quantity='2',
                    totalPrice='2',
                    mark='mark2.2',
                    calculationSubject=33,
                ),
                dict(
                    position_template,
                    code='РН000003',
                    barcode='barcode3',
                    unitPrice='2',
                    quantity='5' if fix_enabled else '4',
                    totalPrice='10' if fix_enabled else '8',
                ),
                dict(
                    position_template,
                    code='РН000004',
                    isCatchWeight=True,
                    barcode='barcode4.1',
                    unitPrice='3',
                    quantity='1',
                    totalPrice='3',
                ),
                dict(
                    position_template,
                    code='РН000004',
                    isCatchWeight=True,
                    barcode='barcode4.2',
                    unitPrice='3',
                    quantity='0.5',
                    totalPrice='1.5',
                ),
                dict(
                    position_template,
                    code='РН000005',
                    isCatchWeight=True,
                    barcode='barcode5.1',
                    unitPrice='4',
                    quantity='1.5' if fix_enabled else '1.4',
                    totalPrice='6' if fix_enabled else '5.6',
                ),
            ]
        )
        for i, position in enumerate(positions):
            position['positionOrder'] = i + 1
        assert request.json == {
            'place_id': PLACE_ID,
            'soft_check': {
                'guid': guid,
                'discountsValue': '0',
                'dateCreated': NOW_UTC,
                'isEditable': False,
                'status': 'READY_TO_PAYMENT',
                'totalPrice': str(
                    sum(
                        [
                            float(position['totalPrice'])
                            for position in positions
                        ],
                    ),
                ),
                'positions': positions,
            },
        }
        return mockserver.make_response(
            status=200, json=request.json['soft_check'],
        )

    order = {
        'eats_id': EATS_ID,
        'picker_id': PICKER_ID,
        'state': 'picking',
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
    }
    order_items = [
        {
            'eats_item_id': 'РН000000',
            'sku': 'РН000000',
            'price': 1,
            'barcodes': ['barcode0'],
            'sold_by_weight': False,
        },
        {
            'eats_item_id': 'РН000001',
            'sku': 'РН000001',
            'price': 1,
            'barcodes': ['barcode1'],
            'sold_by_weight': False,
        },
        {
            'eats_item_id': 'РН000002',
            'sku': 'РН000002',
            'price': 1,
            'barcodes': ['barcode2'],
            'sold_by_weight': False,
            'require_marks': True,
        },
        {
            'eats_item_id': 'РН000003',
            'sku': 'РН000003',
            'price': 2,
            'barcodes': ['barcode3'],
            'sold_by_weight': False,
        },
        {
            'eats_item_id': 'РН000004',
            'sku': 'РН000004',
            'barcodes': ['barcode4'],
            'price': 3,
            'measure_value': 1000,
            'sold_by_weight': True,
        },
        {
            'eats_item_id': 'РН000005',
            'sku': 'РН000005',
            'barcodes': ['barcode5'],
            'price': 4,
            'measure_value': 1000,
            'sold_by_weight': True,
        },
    ]
    picked_items = {
        'РН000000': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000001': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000002': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000003': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'count': 5,
        },
        'РН000004': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': 1500,
        },
        'РН000005': {
            'picker_id': PICKER_ID,
            'cart_version': SOFT_CHECK_CART_VERSION,
            'weight': 1500,
        },
    }
    picked_items_positions = {
        'РН000000': [
            {'count': 2, 'weight': None, 'barcode': 'barcode0'},
            {'count': 2, 'weight': None, 'barcode': 'barcode0'},
        ],
        'РН000001': [
            {'count': 2, 'weight': None, 'barcode': 'barcode1.1'},
            {'count': 2, 'weight': None, 'barcode': 'barcode1.2'},
        ],
        'РН000002': [
            {
                'count': 2,
                'weight': None,
                'barcode': 'barcode2',
                'mark': 'mark2.1',
            },
            {
                'count': 2,
                'weight': None,
                'barcode': 'barcode2',
                'mark': 'mark2.2',
            },
        ],
        'РН000003': [{'count': 4, 'weight': None}],
        'РН000004': [
            {'count': None, 'weight': 1000, 'barcode': 'barcode4.1'},
            {'count': None, 'weight': 500, 'barcode': 'barcode4.2'},
        ],
        'РН000005': [{'count': None, 'weight': 1400, 'barcode': 'barcode5.1'}],
    }

    response = await get_soft_check_response(
        taxi_eats_picker_orders,
        HANDLE_V2,
        None,
        order,
        order_items,
        picked_items,
        picked_items_positions,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
    )

    assert response.status == 200
