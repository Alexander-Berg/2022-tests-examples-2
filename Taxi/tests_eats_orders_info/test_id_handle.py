# pylint: disable=too-many-lines
import copy
import decimal

import pytest

from tests_eats_orders_info import utils

ORDERSHISTORY_LIST_URL = '/eats-ordershistory/internal/v2/get-orders/list'
RUB = 'RUB'
CONFIRMED = 'confirmed'
IMAGE = {'url': 'url', 'resized_url_pattern': 'pattern'}
ORDER_ITEMS = [
    {
        'id': 'id',
        'name': 'name',
        'cost_for_customer': '12.5',
        'images': [IMAGE],
    },
]
PICKED_ITEMS = [item['id'] for item in ORDER_ITEMS]
COURIER = {'name': 'name', 'options': [{'code': 'yandex_rover'}]}
ITEMS_CHANGED = [{'from_item': ORDER_ITEMS[0], 'to_item': ORDER_ITEMS[0]}]
DELIVERY_FEE = '10.1'
WEIGHT_VALUE = 12.2
MEASURE_UNIT = 'g'
COST = '122.21'


def place_business_by_service(service):
    if service == 'eats':
        return 'restaurant'
    if service == 'grocery':
        return 'store'
    if service == 'fuelfood':
        return 'zapravki'
    return service


# cost is amount of money customer paid excluding donations,
# but accounting for delivery fee and discounts
# subtotal is the same as cost, but without discounts and delivery fee
def generate_order(
        order_id,
        service,
        cost,
        subtotal,
        discount,
        discount_promo,
        place_address,
):
    if service == 'shop':
        original_cost = str(
            decimal.Decimal(subtotal)
            - decimal.Decimal(discount)
            - decimal.Decimal(discount_promo),
        )
        if '.' in original_cost:
            original_cost = original_cost.rstrip('0').rstrip('.')
        return {
            'order_nr': order_id,
            'created_at': utils.SAMPLE_TIME_CONVERTED,
            'currency': {'code': RUB, 'sign': 'Р'},
            'original_cost_for_customer': original_cost,
            'final_cost_for_customer': original_cost,
            'original_total_cost_for_customer': cost,
            'total_cost_for_customer': cost,
            'status_for_customer': CONFIRMED,
            'place': {
                'id': 'place_id',
                'slug': 'place_slug',
                'name': 'place_name',
                'business': place_business_by_service(service),
                'is_marketplace': False,
                'address': place_address,
            },
            'delivery_address': 'sample',
            'delivery_point': {'latitude': 1.1, 'longitude': 1.2},
            'original_items': ORDER_ITEMS,
            'picking_status': 'complete',
            'diff': {
                'no_changes': ORDER_ITEMS,
                'add': ORDER_ITEMS,
                'remove': ORDER_ITEMS,
                'replace': ITEMS_CHANGED,
                'update': ITEMS_CHANGED,
                'soft_delete': ORDER_ITEMS,
                'picked_items': PICKED_ITEMS,
            },
            'extra_fees': [
                {
                    'code': 'service_fee',
                    'description': 'Сервисный сбор',
                    'value': '32.32',
                },
            ],
            'discounts': [
                {
                    'code': 'promo',
                    'description': 'Промоакция',
                    'value': '42.42',
                },
                {
                    'code': 'promocode',
                    'description': 'Промокод',
                    'value': '64.64',
                },
                {
                    'code': 'eats_discount',
                    'description': 'Скидка',
                    'value': '77.77',
                },
            ],
            'can_be_removed': False,
            'picker_phone_id': 'some_phone_id',
            'courier_phone_id': 'some_courier_id',
            'forwarded_picker_phone': 'picker_phone',
            'forwarded_courier_phone': 'courier_phone',
        }
    expanded_address = copy.deepcopy(place_address)
    expanded_address['location'] = {'latitude': 2.1, 'longitude': 2.2}
    return {
        'order_nr': order_id,
        'created_at': utils.SAMPLE_TIME,
        'currency': {'code': RUB, 'sign': 'Р'},
        'id': order_id,
        'cart': {
            'items': [
                {
                    'id': 123,
                    'name': 'name',
                    'price_rational': (
                        '12.5'
                    ),  # these numbers don't need to make sense,
                    # we just check if they are passed through
                    'quantity': 1,
                    'weight': f'{WEIGHT_VALUE} {MEASURE_UNIT}',
                    # 'images': None,
                },
            ],
            'subtotal_rational': subtotal,
            'discount_rational': discount,
            'discount_promo_rational': discount_promo,
            'delivery_fee_rational': DELIVERY_FEE,
            'total_rational': cost,
        },
        'place': {
            'id': 111,
            'name': 'place_name',
            'slug': 'place_slug',
            'market': False,
            'address': expanded_address,
        },
        'comment': 'comment',
        'status': {'id': 4, 'title': 'delivered', 'date': utils.SAMPLE_TIME},
        'payment_status': {'id': 123, 'title': 'title', 'type': 1},
        'address': {
            'city': 'Moscow',
            'short': 'address2',
            'location': {'latitude': 1.1, 'longitude': 1.2},
        },
        'awaiting_payment': False,
        'phone_number': '+7777',
        'without_callback': True,
        'persons_quantity': 1,
        'has_feedback': False,
        'show_feedback_button': False,
        'service': service,
        'client_app': 'app',
        'cancelable': True,
        'shipping_type': 'type',
        'courier': COURIER,
        'can_contact_us': True,
    }


def generate_shop_target_order(order, donation, cost, receipts):
    target_order = copy.deepcopy(order)
    target_order['donation'] = donation
    target_order['receipts'] = receipts
    for receipt in target_order['receipts']:
        receipt['created_at'] = '2021-08-06T12:42:12+00:00'
    target_order['total_cost_for_customer'] = target_order[
        'original_total_cost_for_customer'
    ] = cost
    payment_details = {'title': 'Доставка и оплата', 'payload': []}
    payment_details['payload'].append(
        {
            'title': 'Стоимость товаров',
            'amount': target_order['final_cost_for_customer'],
        },
    )
    if 'order_refunded_amount' in target_order:
        payment_details['payload'].append(
            {
                'title': 'Возвращенная сумма',
                'amount': target_order['order_refunded_amount'],
            },
        )
        del target_order['order_refunded_amount']
    if 'delivery_cost_for_customer' in target_order:
        payment_details['payload'].append(
            {
                'title': 'Стоимость доставки',
                'amount': target_order['delivery_cost_for_customer'],
            },
        )
        del target_order['delivery_cost_for_customer']
    if 'picking_cost_for_customer' in target_order:
        payment_details['payload'].append(
            {
                'title': 'Стоимость сборки',
                'amount': target_order['picking_cost_for_customer'],
            },
        )
        del target_order['picking_cost_for_customer']
    if 'tips' in target_order:
        payment_details['payload'].append(
            {'title': 'Чаевые', 'amount': target_order['tips']},
        )
        del target_order['tips']
    if 'restaurant_tips' in target_order:
        payment_details['payload'].append(
            {
                'title': 'Чаевые ресторану',
                'amount': target_order['restaurant_tips'],
            },
        )
        del target_order['restaurant_tips']
    if 'extra_fees' in target_order:
        for extra_fee in target_order['extra_fees']:
            payment_details['payload'].append(
                {
                    'title': extra_fee['description'],
                    'amount': extra_fee['value'],
                },
            )
        del target_order['extra_fees']
    if 'discounts' in target_order:
        for discount in target_order['discounts']:
            payment_details['payload'].append(
                {
                    'title': discount['description'],
                    'amount': '-' + discount['value'],
                },
            )
        del target_order['discounts']
    if donation['status'] == 'finished':
        payment_details['payload'].append(
            {'title': 'Проект «Помощь рядом»', 'amount': donation['amount']},
        )
    target_order['payment_details'] = payment_details
    if 'id' in target_order['place']:
        del target_order['place']['id']
    if 'brand' in target_order['place']:
        target_order['place']['brand']['name'] = target_order['place']['name']
        del target_order['brand']['id']
        del target_order['brand']
    else:
        target_order['place']['brand'] = {
            'slug': target_order['place']['slug'],
            'name': target_order['place']['name'],
        }

    del target_order['currency']
    target_order['currency_rules'] = {
        'code': 'RUB',
        'sign': '₽',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'руб.',
    }
    if target_order['forwarded_picker_phone']:
        target_order['picker_phone_id'] = target_order[
            'forwarded_picker_phone'
        ]
    else:
        target_order['picker_phone_id'] = None
    if target_order['forwarded_courier_phone']:
        target_order['courier_phone_id'] = target_order[
            'forwarded_courier_phone'
        ]
    else:
        target_order['courier_phone_id'] = None

    return target_order


def generate_target_rest_order(order, donation, receipts):
    target_order = copy.deepcopy(order)
    target_order['donation'] = donation
    if donation['status'] == 'finished':
        donation_value = int(donation['amount'])
        target_order['total_cost_for_customer'] = str(
            int(target_order['total_cost_for_customer']) + donation_value,
        )
        target_order['original_total_cost_for_customer'] = str(
            int(target_order['original_total_cost_for_customer'])
            + donation_value,
        )
        target_order['payment_details']['payload'].append(
            {'amount': str(donation_value), 'title': 'Проект «Помощь рядом»'},
        )
    target_order['receipts'] = receipts
    for receipt in target_order['receipts']:
        receipt['created_at'] = '2021-08-06T12:42:12+00:00'
    if (
            order['status_for_customer'] == 'in_delivery'
            or order['status_for_customer'] == 'arrived_to_customer'
    ):
        target_order['forwarded_courier_phone'] = (
            utils.COURIER_PHONE['phone'] + ',,' + utils.COURIER_PHONE['ext']
        )
    return target_order


@pytest.mark.parametrize(
    (
        'service',
        'amounts',
        'exp_cost',
        'subtotal',
        'discount',
        'discount_promo',
        'place_address',
        'target_place_address',
    ),
    [
        (
            'eats',
            {'id1': ['1', 'finished']},
            '123.21',
            '120',
            '12.2',
            '3.1',
            {'city': 'Moscow', 'short': 'address'},
            'address',
        ),
        (
            'shop',
            {'id1': ['1', 'finished']},
            '123.21',
            '120',
            '12.2',
            '3.1',
            {'city': 'Moscow', 'short': 'address'},
            'address',
        ),
        (
            'grocery',
            {'id1': ['1', 'finished']},
            '123.21',
            '120',
            '12.2',
            '0',
            {'city': 'Moscow', 'short': 'address'},
            'address',
        ),
        (
            'shop',
            {'id1': ['1', 'unauthorized']},
            '122.21',
            '120',
            '12',
            '3.1',
            {'city': 'Moscow', 'short': 'address'},
            'address',
        ),
        (
            'eats',
            {'id1': ['1', 'unauthorized']},
            '122.21',
            '120.2',
            '12.2',
            '3',
            {'city': 'Moscow', 'street': 'street', 'house': 'house'},
            'street, house',
        ),
    ],
)
@pytest.mark.parametrize(
    'receipts_data',
    [
        [],
        [
            {
                'type': 'refund',
                'receipt_url': '/url/1',
                'created_at': '2021-08-06T12:42:12.123+00:00',
            },
        ],
        [
            {
                'type': 'refund',
                'receipt_url': '/url/1',
                'created_at': '2021-08-06T12:42:12.123+00:00',
            },
            {
                'type': 'payment',
                'receipt_url': '/url/11',
                'created_at': '2021-08-06T12:42:12.123+00:00',
            },
        ],
    ],
    ids=['no_receipts', 'one_receipt', 'few_receipts'],
)
@pytest.mark.config(EATS_ORDERS_INFO_RECEIPTS_ENABLED={'enabled': True})
@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_id_handle(
        taxi_eats_orders_info,
        service,
        amounts,
        exp_cost,
        subtotal,
        discount,
        discount_promo,
        place_address,
        target_place_address,
        receipts_data,
        local_services,
        load_json,
):
    order_nr = utils.ORDER_NR_ID
    target_donations = utils.generate_order_hist_donations(amounts)
    donations = utils.generate_donations(amounts)
    if service == 'shop':
        local_services.add_user_order(
            status='finished', bus_type=service,
        )  # for core response
        local_services.retail_response = generate_order(
            order_nr,
            service,
            COST,
            subtotal,
            discount,
            discount_promo,
            place_address,
        )
        target_order = generate_shop_target_order(
            local_services.retail_response,
            target_donations[order_nr],
            exp_cost,
            receipts_data,
        )
    else:
        local_services.set_default(bus_type=service)
        target_order = generate_target_rest_order(
            load_json('expected_response_get_order_history_200.json'),
            target_donations[order_nr],
            receipts_data,
        )
    exp_order_ids = [[], []]
    if service == 'grocery':
        exp_order_ids[1].append(order_nr)
    else:
        exp_order_ids[0].append(order_nr)
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )
    receipts = utils.generate_receipts(order_nr, receipts_data)
    local_services.receipts_data = receipts

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'order_nr': order_nr},
    )
    assert response.status_code == 200
    assert utils.format_response(response.json()) == target_order


@pytest.mark.config(EATS_ORDERS_INFO_RECEIPTS_ENABLED={'enabled': True})
@pytest.mark.config(EATS_ORDERS_INFO_USE_CORE_METAINFO=False)
@utils.order_updater_config3()
@utils.order_details_titles_config3()
@pytest.mark.parametrize(
    """ordershistory_not_found,ordershistory_failed,ordershistory_empty_cart,
    catalog_failed,revision_failed,core_failed,
    mock_core_order_info_times_called,expected_code""",
    [
        pytest.param(
            False, False, False, False, False, True, 0, 200, id='greenflow',
        ),
        pytest.param(
            False,
            False,
            True,
            False,
            False,
            False,
            1,
            200,
            marks=pytest.mark.config(
                EATS_ORDERS_INFO_FALLBACK_TO_CORE_FOR_DETAILS=True,
            ),
            id='greenflow, fallback to core, empty cart from ordershistory',
        ),
        pytest.param(
            False,
            False,
            False,
            False,
            True,
            False,
            1,
            200,
            marks=pytest.mark.config(
                EATS_ORDERS_INFO_FALLBACK_TO_CORE_FOR_DETAILS=True,
            ),
            id='greenflow with fallback to core revision failed',
        ),
        pytest.param(
            False,
            False,
            True,
            False,
            True,
            False,
            1,
            200,
            marks=pytest.mark.config(
                EATS_ORDERS_INFO_FALLBACK_TO_CORE_FOR_DETAILS=True,
            ),
            id='greenflow with fallback to core ordershistory failed and '
            'revision failed',
        ),
        pytest.param(
            True,
            False,
            False,
            False,
            False,
            False,
            0,
            404,
            id='ordershistory_not_found',
        ),
        pytest.param(
            False,
            True,
            False,
            False,
            False,
            False,
            0,
            404,
            id='ordershistory_failed',
        ),
        pytest.param(
            False,
            False,
            False,
            True,
            False,
            False,
            0,
            500,
            id='catalog_failed',
        ),
        pytest.param(
            False,
            False,
            False,
            False,
            True,
            False,
            0,
            500,
            id='revision_failed',
        ),
        pytest.param(
            False,
            False,
            True,
            False,
            True,
            True,
            0,
            500,
            marks=pytest.mark.config(
                EATS_ORDERS_INFO_FALLBACK_TO_CORE_FOR_DETAILS=True,
            ),
            id='core_failed',
        ),
    ],
)
async def test_id_handle_ordershistory(
        taxi_eats_orders_info,
        local_services,
        mockserver,
        load_json,
        ordershistory_not_found,
        ordershistory_failed,
        ordershistory_empty_cart,
        catalog_failed,
        revision_failed,
        core_failed,
        mock_core_order_info_times_called,
        expected_code,
):
    order_nr = utils.ORDER_NR_ID
    ordershistory_body = {
        'orders': [
            {
                'order_id': order_nr,
                'place_id': int(utils.PLACE_ID),
                'status': 'finished',
                'order_type': 'native',
                'delivery_location': {'lat': 59.93507, 'lon': 30.33811},
                'total_amount': '658',
                'original_total_amount': '830',
                'is_asap': True,
                'created_at': '2021-08-06T12:42:12+00:00',
                'cart': [
                    {
                        'name': 'Макароны',
                        'quantity': 1,
                        'origin_id': 'item-0',
                        'cost_for_customer': '50',
                    },
                    {
                        'name': 'Дырка от бублика',
                        'original_quantity': 2,
                        'quantity': 1,
                        'origin_id': 'item-1',
                        'cost_for_customer': '150',
                        'refunded_amount': '150',
                    },
                    {
                        'name': 'Виноград',
                        'original_weight': 500,
                        'weight': 0,
                        'quantity': 1,
                        'measure_unit': 'GRM',
                        'origin_id': 'item-2',
                        'cost_for_customer': '99',
                    },
                    # test option
                    {
                        'name': 'Зонтик',
                        'quantity': 1,
                        'parent_origin_id': 'item-2',
                        'cost_for_customer': '1',
                    },
                    {
                        'name': 'Малина',
                        'original_weight': 600,
                        'weight': 0,
                        'measure_unit': 'GRM',
                        'quantity': 1,
                        'origin_id': 'item-3',
                        'cost_for_customer': '100',
                    },
                    # test standalone option
                    {
                        'name': 'Сливки',
                        'quantity': 1,
                        'standalone_parent_origin_id': 'item-3',
                        'cost_for_customer': '20',
                    },
                    {
                        'name': 'Сыр',
                        'weight': 200,
                        'measure_unit': 'GRM',
                        'origin_id': 'item-4',
                        'quantity': 1,
                        'cost_for_customer': '150',
                        # test with refund
                        'refunded_amount': '50',
                    },
                    {
                        'name': 'Спички',
                        'original_quantity': 1,
                        'quantity': 0,
                        'origin_id': 'item-7',
                        'cost_for_customer': '10',
                    },
                ],
                'delivery_address': {'full_address': 'ул. Пушкина'},
            },
        ],
    }
    if ordershistory_empty_cart:
        ordershistory_body['orders'][0].pop('cart')

    amounts = {'id1': ['1', 'finished']}
    receipts_data = [
        {
            'type': 'refund',
            'receipt_url': '/url/1',
            'created_at': '2021-08-06T12:42:12.123+00:00',
        },
    ]
    target_donations = utils.generate_order_hist_donations(amounts)
    donations = utils.generate_donations(amounts)
    local_services.set_default(bus_type='eats')
    target_order = generate_target_rest_order(
        load_json('expected_response_get_order_history_200.json'),
        target_donations[order_nr],
        receipts_data,
    )

    exp_order_ids = [[order_nr], []]
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )
    receipts = utils.generate_receipts(order_nr, receipts_data)
    local_services.receipts_data = receipts

    @mockserver.json_handler(ORDERSHISTORY_LIST_URL)
    def mock_orders(request):
        assert request.method == 'POST'
        assert 'order_ids' in request.json['filters']
        assert 'eater_ids' in request.json['filters']
        assert 'cart' in request.json['projection']
        assert 'include_refund' in request.json['projection']
        assert 'delivery_address' in request.json['projection']
        if ordershistory_failed:
            return mockserver.make_response(status=500, json={})
        if ordershistory_not_found:
            return mockserver.make_response(
                status=404, json={'code': 'not_found', 'message': 'message'},
            )
        return mockserver.make_response(status=200, json=ordershistory_body)

    if catalog_failed:

        @mockserver.json_handler(
            '/eats-catalog-storage/internal/eats-catalog-storage'
            '/v1/places/retrieve-by-ids',
        )
        def _mock_catalog_failed(request):
            return mockserver.make_response(status=500, json={})

    if revision_failed:

        @mockserver.json_handler(
            '/eats-order-revision/v1/revision/latest/'
            'customer-services/details',
        )
        def _mock_revision_failed(request):
            return mockserver.make_response(status=500, json={})

    if core_failed:

        @mockserver.json_handler(
            f'eats-core-orders/internal-api/v1/'
            f'order/{utils.ORDER_NR_ID}/metainfo',
        )
        def _eats_core_order(request):
            return mockserver.make_response(
                status=404,
                json={'status': 'not_found', 'message': 'not_found'},
            )

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'order_nr': order_nr},
    )
    assert mock_orders.times_called == 1
    assert (
        local_services.mock_core_order_info.times_called
        == mock_core_order_info_times_called
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert utils.format_response(response.json()) == target_order


@utils.order_details_titles_config3()
@pytest.mark.parametrize('has_soft_delete', [False, True])
async def test_id_handle_retail_soft_delete(
        taxi_eats_orders_info, local_services, has_soft_delete,
):
    order_nr = utils.ORDER_NR_ID
    amounts = {'id1': ['1', 'finished']}
    target_donations = utils.generate_order_hist_donations(amounts)
    exp_cost = '123.21'
    local_services.add_user_order(
        status='finished', bus_type='shop',
    )  # for core-metainfo response

    exp_order_ids = [[], []]
    exp_order_ids[0].append(order_nr)
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)

    local_services.retail_response = generate_order(
        order_nr,
        'shop',
        COST,
        '120',
        '12.2',
        '3.1',
        {'city': 'Moscow', 'short': 'address'},
    )
    if not has_soft_delete:
        del local_services.retail_response['diff']['soft_delete']

    target_order = generate_shop_target_order(
        local_services.retail_response,
        target_donations[order_nr],
        exp_cost,
        [],
    )
    donations = utils.generate_donations(amounts)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'order_nr': order_nr},
    )
    assert response.status_code == 200
    assert utils.format_response(response.json()) == target_order


@utils.order_updater_config3()
@pytest.mark.parametrize('exp_code', [400, 401, 404, 500])
async def test_id_handle_retail_fail(
        taxi_eats_orders_info, exp_code, local_services,
):
    local_services.add_user_order(
        status='finished', bus_type='shop',
    )  # for core-metainfo response
    local_services.retail_response_code = exp_code
    local_services.retail_response = {
        'code': f'{exp_code}',
        'message': 'message',
    }

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'order_nr': utils.ORDER_NR_ID},
    )
    assert response.status_code == exp_code


@utils.order_updater_config3()
@pytest.mark.parametrize(
    'exp_code, polling',
    [(200, True), (400, False), (401, False), (404, True), (500, False)],
)
async def test_id_handle_retail_polling(
        taxi_eats_orders_info, exp_code, polling, local_services,
):
    local_services.retail_response_code = exp_code
    local_services.add_user_order(
        status='finished', bus_type='shop',
    )  # for core-metainfo response
    if exp_code == 200:
        order_nr = utils.ORDER_NR_ID
        local_services.retail_response = generate_order(
            order_nr,
            'shop',
            COST,
            '100',
            '10',
            '10',
            {'city': 'Moscow', 'short': 'address'},
        )
        exp_order_ids = [[], []]
        exp_order_ids[0].append(order_nr)
        local_services.exp_order_ids = copy.deepcopy(exp_order_ids)
        amounts = {'id1': ['1', 'finished']}
        donations = utils.generate_donations(amounts)
        local_services.brands_response = utils.generate_brands_response(
            exp_order_ids, donations,
        )
        local_services.receipts_data = utils.generate_receipts(order_nr, [])
    else:
        local_services.retail_response = {
            'code': f'{exp_code}',
            'message': 'message',
        }
    polling_delay = '30'
    local_services.retail_response_headers = {'X-Polling-Delay': polling_delay}

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'place_business': 'shop', 'order_nr': utils.ORDER_NR_ID},
    )
    assert response.status_code == exp_code

    if polling:
        assert response.headers['X-Polling-Delay'] == polling_delay
    else:
        assert 'X-Polling-Delay' not in response.headers


@utils.order_updater_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
async def test_id_handle_feedback_info(
        mockserver, taxi_eats_orders_info, local_services,
):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/'
        'v1/get-feedbacks-for-orders-history',
    )
    def _mock_feedback(request):
        return mockserver.make_response(
            status=200,
            json={
                'feedbacks': [
                    {
                        'has_feedback': True,
                        'status': 'noshow',
                        'order_nr': utils.ORDER_NR_ID,
                        'is_feedback_needed': False,
                    },
                ],
            },
        )

    local_services.set_default()
    donations = utils.generate_donations({'id1': ['1', 'finished']})
    exp_order_ids = [[utils.ORDER_NR_ID], []]
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'order_nr': utils.ORDER_NR_ID},
    )

    assert response.status == 200
    data = response.json()
    assert data['has_feedback'] is True
    assert data['show_feedback_button'] is False


@utils.order_updater_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
@pytest.mark.parametrize(
    """feedback_code,feedback_resposne""",
    [
        (200, {'feedbacks': []}),
        (400, {'code': 'some code', 'message': 'some message'}),
    ],
)
async def test_id_handle_feedback_info_fail(
        mockserver,
        taxi_eats_orders_info,
        local_services,
        feedback_code,
        feedback_resposne,
):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/'
        'v1/get-feedbacks-for-orders-history',
    )
    def _mock_feedback(request):
        return mockserver.make_response(
            status=feedback_code, json=feedback_resposne,
        )

    local_services.set_default()
    donations = utils.generate_donations({'id1': ['1', 'finished']})
    exp_order_ids = [[utils.ORDER_NR_ID], []]
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'place_business': 'restaurant', 'order_nr': utils.ORDER_NR_ID},
    )

    assert response.status == 200
    data = response.json()
    assert 'has_feedback' not in data
    assert 'show_feedback_button' not in data


@utils.order_updater_config3()
@pytest.mark.config(EATS_ORDERS_INFO_RECEIPTS_ENABLED={'enabled': True})
@pytest.mark.parametrize(
    """receipts_response,receipts_code""",
    [({'code': 'error', 'message': 'error'}, 404), (None, 500)],
)
async def test_id_handle_receipts_fail(
        mockserver,
        taxi_eats_orders_info,
        local_services,
        receipts_response,
        receipts_code,
):
    local_services.set_default()
    donations = utils.generate_donations({'id1': ['1', 'finished']})

    exp_order_ids = [[utils.ORDER_NR_ID], []]
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)

    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )

    @mockserver.json_handler('eats-receipts/api/v1/receipts')
    def mock_receipts(request):
        return mockserver.make_response(
            status=receipts_code, json=receipts_response,
        )

    local_services.mock_receipts = mock_receipts

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'place_business': 'restaurant', 'order_nr': utils.ORDER_NR_ID},
    )

    assert response.status == 200
    assert not response.json()['receipts']


async def test_id_handle_no_user_id_401(taxi_eats_orders_info):
    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        params={'order_nr': utils.ORDER_NR_ID, 'place_business': 'restaurant'},
    )
    assert response.status_code == 401


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize(
    'orders_response',
    [{'status': 404, 'json': {'status': 'not_found', 'message': 'not_found'}}],
)
async def test_id_handle_order_metainfo_failed(
        mockserver, local_services, orders_response, assert_response,
):
    local_services.set_default()

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{utils.ORDER_NR_ID}/metainfo',
    )
    def _eats_core_order(request):
        return mockserver.make_response(**orders_response)

    local_services.mock_core_order_info = _eats_core_order

    await assert_response(404, None)
    assert local_services.mock_core_order_info.times_called == 1


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize(
    'orders_response',
    [
        {
            'status': 200,
            'json': {
                'order_nr': utils.ORDER_NR_ID,
                'location_latitude': 1.0,
                'location_longitude': 1.0,
                'business_type': 'restaurant',
                'city': 'city',
                'street': 'street',
                'is_asap': True,
                'status': 'created',
                'place_id': utils.PLACE_ID,
                'region_id': '1',
                'place_delivery_zone_id': '1',
                'app': 'web',
                'order_status_history': {
                    'created_at': utils.SAMPLE_TIME_CONVERTED,
                },
                'order_user_information': {'eater_id': 'wrong_eater_id'},
            },
        },
        {
            'status': 200,
            'json': {
                'order_nr': utils.ORDER_NR_ID,
                'location_latitude': 1.0,
                'location_longitude': 1.0,
                'business_type': 'restaurant',
                'city': 'city',
                'street': 'street',
                'is_asap': True,
                'status': 'created',
                'place_id': utils.PLACE_ID,
                'region_id': '1',
                'place_delivery_zone_id': '1',
                'app': 'web',
                'order_status_history': {
                    'created_at': utils.SAMPLE_TIME_CONVERTED,
                },
            },
        },
    ],
)
async def test_id_handle_order_for_diff_eater(
        mockserver, local_services, orders_response, assert_response,
):
    local_services.set_default()

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{utils.ORDER_NR_ID}/metainfo',
    )
    def _eats_core_order(request):
        return mockserver.make_response(**orders_response)

    local_services.mock_core_order_info = _eats_core_order

    await assert_response(404, None)
    assert local_services.mock_core_order_info.times_called == 1


@utils.order_updater_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=False)
async def test_id_handle_change_brand_name(
        taxi_eats_orders_info, local_services,
):
    local_services.set_default()
    donations = utils.generate_donations({'id1': ['1', 'finished']})
    exp_order_ids = [[utils.ORDER_NR_ID], []]
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'order_nr': utils.ORDER_NR_ID},
    )

    assert response.status == 200
    data = response.json()
    assert data['place']['brand']['name'] == utils.PLACE_NAME


@utils.order_updater_config3()
# no order_details_titles_config3
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=False)
async def test_id_handle_empty_details(taxi_eats_orders_info, local_services):
    local_services.set_default()
    donations = utils.generate_donations({'id1': ['1', 'finished']})
    exp_order_ids = [[utils.ORDER_NR_ID], []]
    local_services.exp_order_ids = copy.deepcopy(exp_order_ids)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )

    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        headers=utils.get_auth_headers(),
        params={'order_nr': utils.ORDER_NR_ID},
    )

    assert response.status == 200
    data = response.json()
    assert data['payment_details'] == {'payload': []}
