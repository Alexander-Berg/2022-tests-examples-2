import copy
import decimal
import re

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart
# pylint: enable=import-error
import pytest

from . import configs
from . import consts
from . import experiments
from . import headers
from . import helpers
from . import integration_submit_consts
from . import models


GROCERY_ORDERS_RECENT_GOODS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_orders_recent_goods',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'save_to_fav_goods': True},
        },
    ],
    is_config=True,
)

MARKDOWN_ITEM = models.GroceryCartItem(
    item_id='item-id-2:st-md',
    title='item-2-title',
    price='0',
    full_price='0',
    quantity='2',
    currency='RUB',
    vat='10',
    refunded_quantity='0',
    gross_weight=100,
    width=200,
    height=300,
    depth=400,
)


@pytest.mark.now(consts.NOW)
async def test_submit(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        taxi_grocery_orders_monitor,
        yamaps_local,
        personal,
):
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        region_id=integration_submit_consts.REGION_ID,
    )
    grocery_cart.set_grocery_flow_version(
        integration_submit_consts.PROCESSING_FLOW_VERSION,
    )

    grocery_cart_items = copy.deepcopy(grocery_cart.get_items())
    grocery_cart_items.append(MARKDOWN_ITEM)
    grocery_cart.set_items(grocery_cart_items)

    submit_headers = headers.NO_YANDEX_USER_HEADERS.copy()
    submit_headers['X-YaTaxi-Bound-Sessions'] = 'uber:228'

    metrics_before = await taxi_grocery_orders_monitor.get_metric('metrics')

    grocery_cart.check_request(
        fields_to_check={
            'additional_data': {
                'device_coordinates': {
                    'location': integration_submit_consts.LOCATION_IN_RUSSIA,
                    'uri': integration_submit_consts.URI,
                },
                'city': 'Moscow',
                'street': 'Varshavskoye Highway',
                'house': '141Ак1',
                'flat': integration_submit_consts.FLAT,
                'comment': integration_submit_consts.COMMENT,
                'doorcode': '42',
                'entrance': '3333',
                'floor': '13',
            },
        },
        handler=mock_grocery_cart.Handler.checkout,
    )

    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=submit_headers,
    )
    assert response.status_code == 200

    metrics_after = await taxi_grocery_orders_monitor.get_metric('metrics')
    assert (
        metrics_after['created_orders'] - metrics_before['created_orders'] == 1
    )

    assert response.status_code == 200
    order_id = response.json()['order_id']

    order = models.Order(
        pgsql=pgsql,
        order_id=order_id,
        insert_in_pg=False,
        place_id='yamaps://12345',
        location='37.000000, 55.000000',
        currency=None,
    )
    order.update()

    assert grocery_cart.checkout_times_called() == 1
    assert grocery_cart.set_order_id_times_called() == 1

    # Checks create event to processing
    assert _get_last_processing_events(processing, order_id) == [
        {
            'order_id': order.order_id,
            'reason': 'created',
            'order_version': order.order_version,
        },
        {
            'order_id': order.order_id,
            'reason': 'cancel',
            'flow_version': integration_submit_consts.PROCESSING_FLOW_VERSION,
            'cancel_reason_message': 'Order timed out',
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_type': 'timeout',
            'times_called': 0,
        },
    ]

    assert order.order_id == order_id
    assert order.order_version == 0
    assert (
        order.grocery_flow_version
        == integration_submit_consts.PROCESSING_FLOW_VERSION
    )
    assert order.idempotency_token == headers.IDEMPOTENCY_TOKEN
    assert order.eats_order_id is None
    assert order.cart_id == integration_submit_consts.CART_ID
    assert order.cart_version == 4
    assert order.offer_id == integration_submit_consts.OFFER_ID
    assert order.taxi_user_id == headers.USER_ID
    assert order.eats_user_id == headers.EATS_USER_ID
    assert order.personal_phone_id == headers.PERSONAL_PHONE_ID
    assert (
        order.additional_phone_code
        == integration_submit_consts.ADDITIONAL_PHONE_CODE
    )
    assert order.locale == 'ru'
    assert order.app_info == headers.APP_INFO
    assert order.appmetrica_device_id == headers.APPMETRICA_DEVICE_ID
    assert _split_userinfo(order.user_info) == _split_userinfo(
        headers.USER_INFO,
    )
    assert order.depot_id == integration_submit_consts.DEPOT_ID
    assert order.region_id == integration_submit_consts.REGION_ID
    assert order.city == 'Moscow'
    assert order.street == 'Varshavskoye Highway'
    assert order.house == '141Ак1'
    assert order.entrance == integration_submit_consts.ENTRANCE
    assert order.flat == '666'
    assert order.doorcode == '42'
    assert order.doorcode_extra == integration_submit_consts.DOORCODE_EXTRA
    assert order.building_name == integration_submit_consts.BUILDING_NAME
    assert order.doorbell_name == integration_submit_consts.DOORBELL_NAME
    assert order.left_at_door is False
    assert order.floor == '13'
    assert order.comment == integration_submit_consts.COMMENT
    assert order.client_price == decimal.Decimal('9000')
    assert order.currency == 'RUB'
    assert order.promocode is None
    assert order.promocode_valid is None
    assert order.promocode_sum is None

    assert order.status == 'checked_out'

    assert order.session == 'taxi:' + headers.USER_ID
    assert order.bound_sessions == ['uber:228']

    assert order.personal_email_id == 'personal-email-id'

    # example: 310520-542-7918
    assert re.match(r'\d{6}-\d{3}-\d{4}', order.short_order_id)


async def test_unique_short_id(
        taxi_grocery_orders,
        grocery_cart,
        testpoint,
        pgsql,
        mockserver,
        experiments3,
        load_json,
        yamaps_local,
        grocery_depots,
        personal,
):
    experiments.set_simultaneous_orders_limit(experiments3, 2)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)
    grocery_cart.set_grocery_flow_version(
        integration_submit_consts.PROCESSING_FLOW_VERSION,
    )
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    order = models.Order(
        pgsql=pgsql,
        depot_id=integration_submit_consts.DEPOT_ID,
        place_id='yamaps://12345',
        location='37.000000, 55.000000',
    )

    @testpoint('mock_short_order_id')
    def _mock_short_order_id(data):
        return {'short_order_id': order.short_order_id}

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    # We mocked short order id and because of unique violation
    # 500 is returned.
    assert response.status_code == 500

    another_short_order_id = '1111'

    @testpoint('mock_short_order_id')
    def _mock_another_short_order_id(data):
        return {'short_order_id': another_short_order_id}

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    assert response.status_code == 200

    order_id = response.json()['order_id']
    another_order = models.Order(
        pgsql=pgsql, order_id=order_id, insert_in_pg=False,
    )
    another_order.update()

    assert another_order.short_order_id == another_short_order_id


@pytest.mark.parametrize(
    'flow, result_failed',
    [
        ('grocery_flow_v2', True),
        ('integration_no_payment_flow_v1', False),
        ('tristero_flow_v1', False),
    ],
)
async def test_no_payment_method(
        taxi_grocery_orders,
        grocery_cart,
        personal,
        grocery_depots,
        flow,
        result_failed,
):
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['flow_version'] = flow

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    if result_failed:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'bad_payment_method',
            'message': 'no payment method',
        }
    else:
        assert response.status_code == 200


async def test_bad_geo_ymapsbm1(
        taxi_grocery_orders, grocery_cart, grocery_depots, yamaps,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        return []  # empty

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['position']['place_id'] = (
        'ymapsbm1://geo?ll=37.500%2C55.704&spn=0.001%2C0.001&'
        + 'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C'
    )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'flow, result_failed',
    [
        ('grocery_flow_v2', True),
        ('integration_no_payment_flow_v1', False),
        ('tristero_flow_v1', False),
    ],
)
@experiments.available_payment_types(['applepay'])
async def test_bad_payment_method(
        taxi_grocery_orders, grocery_cart, grocery_depots, flow, result_failed,
):
    grocery_cart.set_payment_method({'type': 'card'})
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['flow_version'] = flow

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    if result_failed:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'bad_payment_method',
            'message': 'payment type: card is not supported',
        }
    else:
        assert response.status_code == 200


@pytest.mark.parametrize(
    'flow, result_failed',
    [
        ('grocery_flow_v2', True),
        ('integration_no_payment_flow_v1', False),
        ('tristero_flow_v1', False),
    ],
)
@experiments.available_payment_types(['card'])
async def test_bad_payment_method_id(
        taxi_grocery_orders, grocery_cart, grocery_depots, flow, result_failed,
):
    grocery_cart.set_payment_method({'type': 'card', 'id': None})
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['flow_version'] = flow

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    if result_failed:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'bad_payment_method',
            'message': 'no payment method id',
        }
    else:
        assert response.status_code == 200


@pytest.mark.parametrize(
    'orders_count,codes',
    [(0, [400, 400, 400]), (1, [200, 400, 400]), (2, [200, 200, 400])],
)
async def test_simultaneously_orders(
        taxi_grocery_orders,
        grocery_cart,
        taxi_config,
        experiments3,
        orders_count,
        codes,
        personal,
        grocery_depots,
):
    experiments.set_simultaneous_orders_limit(experiments3, orders_count)

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    tokens = ['token-1', 'token-2', 'token-3']

    cart_id_1 = '00000000-0000-0000-0000-d98013000000'
    cart_id_2 = '00000000-0000-0000-0000-d98013000001'
    cart_id_3 = '00000000-0000-0000-0000-d98013000002'
    cart_ids = [cart_id_1, cart_id_2, cart_id_3]

    submit_headers = headers.NO_YANDEX_USER_HEADERS.copy()
    body = integration_submit_consts.SUBMIT_BODY.copy()

    for attempt, code in enumerate(codes):
        submit_headers['X-Idempotency-Token'] = tokens[attempt]
        body['cart_id'] = cart_ids[attempt]

        response = await taxi_grocery_orders.post(
            '/orders/v1/integration-api/v1/submit',
            json=body,
            headers=submit_headers,
        )
        assert response.status_code == code, 'attempt=' + str(attempt)
        if code != 200:
            assert (
                response.json()['code'] == 'orders_limit_exceeded'
            ), 'attempt=' + str(attempt)


async def test_simultaneously_orders_idempotency_token(
        taxi_grocery_orders,
        experiments3,
        grocery_cart,
        grocery_depots,
        personal,
):
    experiments.set_simultaneous_orders_limit(experiments3, 1)

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    assert response.status_code == 200

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    assert response.status_code == 200


@experiments.available_payment_types(['googlepay'])
@pytest.mark.parametrize(
    'payment_method_type, status_code, error_code',
    [('googlepay', 200, None), ('applepay', 400, 'bad_payment_method')],
)
async def test_googlepay_check(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        payment_method_type,
        status_code,
        error_code,
):
    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['flow_version'] = 'grocery_flow_v3'
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )
    grocery_cart.set_payment_method({'type': payment_method_type, 'id': 'id'})

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    assert response.status_code == status_code
    if error_code is not None:
        assert response.json()['code'] == error_code


@experiments.available_payment_types(['googlepay'])
async def test_idempotency(
        taxi_grocery_orders,
        grocery_cart,
        experiments3,
        processing,
        grocery_depots,
        personal,
):
    experiments.set_simultaneous_orders_limit(experiments3, 1)

    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['flow_version'] = 'grocery_flow_v3'
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )
    grocery_cart.set_payment_method({'type': 'googlepay', 'id': 'id'})

    order_id = None
    for iter_count in range(1, 4):
        grocery_cart.flush_all()

        response = await taxi_grocery_orders.post(
            '/orders/v1/integration-api/v1/submit',
            json=body,
            headers=headers.NO_YANDEX_USER_HEADERS,
        )
        assert response.status_code == 200

        if order_id is None:
            order_id = response.json()['order_id']
        else:
            assert order_id == response.json()['order_id']

        assert grocery_cart.checkout_times_called() == 1
        assert grocery_cart.set_order_id_times_called() == 1

        basic_events = _get_last_processing_events(processing, order_id)
        non_critical_events = _get_last_processing_events(
            processing, order_id, queue='processing_non_critical',
        )
        events_per_call = 2
        assert (
            len(basic_events) + len(non_critical_events)
            == iter_count * events_per_call
        )


@pytest.mark.parametrize(
    'has_name,has_phone,personal_times_called,',
    [(True, True, 1), (False, True, 1), (False, False, 0)],
)
async def test_gift_order(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        pgsql,
        personal,
        has_name,
        has_phone,
        personal_times_called,
        testpoint,
):
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    gift_phone = '8(999)123-42-12'
    gift_phone_normalized = '+79991234212'
    gift_phone_id = '1a1a2b2b3c3c'

    @testpoint('fix-log-no-phone')
    def testpoint_logs(data):
        assert gift_phone not in data['log']
        assert gift_phone_normalized not in data['log']

    if has_name:
        gift_name = 'Alice'
        gift_name_request = {'name': gift_name}
    else:
        gift_name = None
        gift_name_request = {}

    body = copy.deepcopy(integration_submit_consts.SUBMIT_BODY)

    if has_phone:
        body['gift_by_phone'] = {
            'phone_number': gift_phone,
            **gift_name_request,
        }

    if has_phone:
        personal.check_request(
            phone=gift_phone_normalized, personal_phone_id=gift_phone_id,
        )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    assert response.status_code == 200
    order_id = response.json()['order_id']
    order = models.Order(pgsql=pgsql, order_id=order_id, insert_in_pg=False)
    order.update()

    assert order.gift_info == (
        models.GiftInfo(name=gift_name, phone_id=gift_phone_id)
        if has_phone
        else None
    )
    assert personal.times_phones_store_called() == personal_times_called
    assert testpoint_logs.times_called == 1


async def test_submit_no_phone_id(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        taxi_grocery_orders_monitor,
        yamaps,
        personal,
):
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)

    submit_headers = headers.NO_YANDEX_USER_HEADERS.copy()
    submit_headers['X-YaTaxi-User'] = f'eats_user_id={headers.EATS_USER_ID}'
    submit_headers['X-YaTaxi-Bound-Sessions'] = 'eats:12345,taxi:6789'

    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=submit_headers,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'no_personal_phone_id'


@pytest.mark.parametrize('has_yandex_uid', [False, True])
@GROCERY_ORDERS_RECENT_GOODS_EXPERIMENT
async def test_save_recent_goods(
        taxi_grocery_orders,
        grocery_cart,
        grocery_fav_goods,
        testpoint,
        personal,
        grocery_depots,
        has_yandex_uid,
):
    product_ids = ['test_product_id_1', 'test_product_id_2']

    grocery_fav_goods.setup_request_checking(
        yandex_uid=headers.YANDEX_UID, product_ids=product_ids,
    )

    @testpoint('save_recent_goods')
    def save_recent_goods(data):
        pass

    items = [
        models.GroceryCartItem(item_id=product_id, price='10')
        for product_id in product_ids
    ]
    grocery_cart.set_items(items=items)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=integration_submit_consts.DEPOT_ID)
    grocery_cart.set_grocery_flow_version(
        integration_submit_consts.PROCESSING_FLOW_VERSION,
    )

    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    submit_headers = headers.NO_YANDEX_USER_HEADERS.copy()
    submit_headers['X-YaTaxi-Bound-Sessions'] = 'eats:12345,taxi:6789'
    if has_yandex_uid:
        submit_headers['X-Yandex-UID'] = headers.YANDEX_UID

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=submit_headers,
    )
    assert response.status_code == 200

    if has_yandex_uid:
        await save_recent_goods.wait_call()
        assert grocery_fav_goods.times_called == 1
    else:
        assert grocery_fav_goods.times_called == 0


def _get_last_processing_events(processing, order_id, queue='processing'):
    return helpers.get_last_processing_payloads(
        processing, order_id, queue=queue,
    )


def _split_userinfo(userinfo):
    return [l.strip() for l in userinfo.split(',')].sort()


async def test_billing_flow_and_settings(
        taxi_grocery_orders, grocery_cart, grocery_depots, pgsql, experiments3,
):
    billing_settings_version = 'settings-version'
    configs.set_billing_settings_version(
        experiments3, billing_settings_version,
    )
    configs.set_billing_flow(experiments3)

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    assert response.status_code == 200

    order = models.Order(
        pgsql, order_id=response.json()['order_id'], insert_in_pg=False,
    )
    order.update()

    assert order.billing_settings_version == billing_settings_version


@configs.PASS_PAYMENT_METHOD_CHECKOUT_ENABLED
async def test_pass_payment_method_to_cart(
        taxi_grocery_orders, grocery_cart, grocery_depots,
):
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

    grocery_cart.check_request(
        {
            'payment_method': {
                'type': integration_submit_consts.REQUEST_PAYMENT_TYPE,
                'id': integration_submit_consts.REQUEST_PAYMENT_ID,
            },
        },
        handler=mock_grocery_cart.Handler.checkout,
    )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=integration_submit_consts.SUBMIT_BODY,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    assert response.status_code == 200


@pytest.mark.parametrize('push_notification_enabled', [True, False])
@configs.PASS_PAYMENT_METHOD_CHECKOUT_ENABLED
async def test_push_notification_enabled(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        pgsql,
        push_notification_enabled,
):
    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['push_notification_enabled'] = push_notification_enabled
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

    grocery_cart.check_request(
        {
            'payment_method': {
                'type': integration_submit_consts.REQUEST_PAYMENT_TYPE,
                'id': integration_submit_consts.REQUEST_PAYMENT_ID,
            },
        },
        handler=mock_grocery_cart.Handler.checkout,
    )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    assert response.status_code == 200

    order = models.Order(
        pgsql, order_id=response.json()['order_id'], insert_in_pg=False,
    )
    order.update()
    assert order.push_notification_enabled == push_notification_enabled


@configs.GROCERY_ORDERS_SUBMIT_LIMIT
async def test_submit_without_limit(
        taxi_grocery_orders,
        grocery_cart,
        processing,
        grocery_depots,
        personal,
):
    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['flow_version'] = 'grocery_flow_v3'
    grocery_depots.add_depot(
        legacy_depot_id=integration_submit_consts.DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

    order_id = None
    for iter_count in range(1, 20):
        grocery_cart.flush_all()

        response = await taxi_grocery_orders.post(
            '/orders/v1/integration-api/v1/submit',
            json=body,
            headers=headers.NO_YANDEX_USER_HEADERS,
        )
        assert response.status_code == 200

        if order_id is None:
            order_id = response.json()['order_id']
        else:
            assert order_id == response.json()['order_id']

        assert grocery_cart.checkout_times_called() == 1
        assert grocery_cart.set_order_id_times_called() == 1

        basic_events = _get_last_processing_events(processing, order_id)
        non_critical_events = _get_last_processing_events(
            processing, order_id, queue='processing_non_critical',
        )
        events_per_call = 2
        assert (
            len(basic_events) + len(non_critical_events)
            == iter_count * events_per_call
        )


@pytest.mark.parametrize(
    'grocery_flow_version', ['tristero_flow_v2', 'tristero_no_auth_flow_v1'],
)
async def test_submit_disabled(taxi_grocery_orders, grocery_flow_version):
    body = integration_submit_consts.SUBMIT_BODY.copy()
    body['flow_version'] = grocery_flow_version

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    assert response.status_code == 500
