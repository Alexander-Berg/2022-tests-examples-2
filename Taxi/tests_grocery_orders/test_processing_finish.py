# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import experiments
from . import headers
from . import helpers
from . import models
from . import order_log
from . import processing_noncrit

ITEM_ID_1 = consts.ITEM_ID

TRANSACTION_AMOUNT = '150'
PARTIAL_REFUND_AMOUNT = '100'
PARTIAL_REFUND_QUANTITY = '2'
QUANTITY = '3'
PRICE = '50'

PERSONAL_PHONE_ID = 'personal-phone-id'
OPERATION_ID_1 = 'operation-id-xxx'
OPERATION_ID_2 = 'operation-id-yyy'


@pytest.mark.now(consts.NOW)
async def test_happy_path(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots,
):
    orderstate = models.OrderState()
    orderstate.close_money_status = 'success'
    order = models.Order(pgsql=pgsql, status='closed', state=orderstate)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200

    order.update()
    assert order.finished == consts.NOW_DT


def add_depot(depot_id, grocery_depots):
    grocery_depots.add_depot(
        legacy_depot_id=depot_id,
        tin=order_log.DEPOT_TIN,
        address=order_log.DEPOT_ADDRESS,
        name=order_log.DEPOT_NAME,
    )


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_SEND_ATLAS_EVENTS=True)
@pytest.mark.parametrize('status', ['closed', 'canceled'])
async def test_status_change_event(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        status,
        transactions_eda,
):
    courier = order_log.COURIER
    dispatch_id = 'dispatch_id_1234'
    orderstate = models.OrderState()
    orderstate.close_money_status = 'success'
    order = models.Order(
        pgsql=pgsql,
        status=status,
        state=orderstate,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='accepted',
            dispatch_cargo_status='pickuped',
            dispatch_courier_name=courier['courier_full_name'],
            dispatch_courier_first_name=courier['name'],
        ),
        dispatch_performer=models.DispatchPerformer(
            driver_id=courier['driver_id'],
            eats_courier_id=courier['eats_courier_id'],
            courier_full_name=courier['courier_full_name'],
            first_name=courier['name'],
            organization_name=courier['organization_name'],
            legal_address=courier['legal_address'],
            ogrn=courier['ogrn'],
            work_schedule=courier['work_schedule'],
            personal_tin_id=courier['tin'],
            vat=courier['vat'],
            balance_client_id=courier['balance_client_id'],
        ),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(order_log.CART_ITEMS)
    grocery_cart.set_order_conditions(delivery_cost='500')
    grocery_cart.set_delivery_type('courier')
    add_depot(order.depot_id, grocery_depots)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
        headers=headers.HEADER_APP_INFO_YANGO,
    )
    order.update()

    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    if status == 'canceled':
        assert len(events) == 1
        event = events[0]
    if status == 'closed':
        assert len(events) == 2
        event = events[1]

    assert event.payload['order_id'] == order.order_id
    assert event.payload['status_change'] == status
    order_log.check_order_log_payload(
        event.payload, order, courier=courier, is_finish=True,
    )

    if status == 'closed':
        notification = events[0]
        assert notification.payload['order_id'] == order.order_id
        assert notification.payload['code'] == 'delivered'

    assert event.payload['atlas_order_info']['order_id'] == order.order_id


@pytest.mark.now(consts.NOW)
@pytest.mark.experiments3(
    name='grocery_orders_send_to_eats_tracking_v2',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['lavka_android', 'eda_webview_iphone'],
                    'arg_name': 'application',
                    'set_elem_type': 'string',
                },
            },
            'value': {
                'send_to_eats_courier': True,
                'send_to_eats_order': True,
            },
        },
    ],
    default_value={'send_to_eats_courier': False, 'send_to_eats_order': False},
    is_config=True,
)
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_SEND_ATLAS_EVENTS=True)
@pytest.mark.parametrize('status', ['closed', 'canceled'])
@pytest.mark.parametrize('app_name', ['lavka_iphone', 'eda_webview_iphone'])
async def test_status_change_event_with_stq(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        status,
        transactions_eda,
        app_name,
        grocery_eats_gateway,
):
    order_id = '123456-grocery'
    courier = order_log.COURIER
    dispatch_id = 'dispatch_id_1234'
    orderstate = models.OrderState()
    orderstate.close_money_status = 'success'
    grocery_eats_gateway.add_history(
        order_id, '2020-05-25T17:40:45+00:00', pgsql,
    )
    grocery_eats_gateway.set_order_data(
        status=status, dispatch_cargo_status='pickuped',
    )
    order = models.Order(
        order_id=order_id,
        pgsql=pgsql,
        depot_id='12345',
        status=status,
        state=orderstate,
        created='2020-05-25T17:40:45+00:00',
        short_order_id='000000-111-2222',
        app_info=f'app_name={app_name}',
        eats_user_id='eats_user_id_0',
        updated='2020-05-25T17:43:00+00:00',
        status_updated='2020-05-25T17:43:00+00:00',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='accepted',
            dispatch_cargo_status='pickuped',
            dispatch_courier_name=courier['name'],
            dispatch_delivered_eta_ts='2020-05-25T17:43:00+00:00',
        ),
        dispatch_performer=models.DispatchPerformer(
            driver_id=courier['driver_id'],
            eats_courier_id=courier['eats_courier_id'],
            courier_full_name=courier['courier_full_name'],
            organization_name=courier['organization_name'],
            legal_address=courier['legal_address'],
            ogrn=courier['ogrn'],
            work_schedule=courier['work_schedule'],
            personal_tin_id=courier['tin'],
            vat=courier['vat'],
            balance_client_id=courier['balance_client_id'],
        ),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(order_log.CART_ITEMS)
    grocery_cart.set_order_conditions(delivery_cost='500')
    grocery_cart.set_delivery_type('courier')
    add_depot(order.depot_id, grocery_depots)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
        headers=headers.HEADER_APP_INFO_YANGO,
    )
    order.update()

    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    if status == 'canceled':
        assert len(events) == 1
        event = events[0]
    if status == 'closed':
        assert len(events) == 2
        event = events[1]

    assert event.payload['order_id'] == order.order_id
    assert event.payload['status_change'] == status

    if status == 'closed':
        notification = events[0]
        assert notification.payload['order_id'] == order.order_id
        assert notification.payload['code'] == 'delivered'

    assert event.payload['atlas_order_info']['order_id'] == order.order_id
    assert grocery_eats_gateway.times_stq_orders() == (
        2 if app_name == 'eda_webview_iphone' else 0
    )


@pytest.mark.parametrize(
    'init_status,status_code,wms_reserved,money_held,' 'money_closed',
    [
        ('closed', 200, True, True, True),
        ('canceled', 200, True, True, True),
        ('canceled', 200, False, False, True),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        cargo,
        processing,
        init_status,
        status_code,
        wms_reserved,
        money_held,
        money_closed,
):
    orderstate = models.OrderState()
    if wms_reserved:
        orderstate.wms_reserve_status = 'success'
    if money_held:
        orderstate.hold_money_status = 'success'
    if money_closed:
        orderstate.close_money_status = 'success'

    depot_id = '1234'
    grocery_depots.add_depot(legacy_depot_id=depot_id)

    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        state=orderstate,
        dispatch_status_info=models.DispatchStatusInfo(),
        depot_id=depot_id,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    order.update()

    want_wms_close = 0
    want_set_delivered_eda_status = 0

    if init_status == 'canceled':
        if wms_reserved is not None:
            want_wms_close = 1
    else:
        want_set_delivered_eda_status = 1
        if not money_closed:
            # "Success close" without money charging..
            status_code = 500

    assert response.status_code == status_code
    assert order.status == init_status

    assert grocery_wms_gateway.times_mock_order_add() == 0
    assert grocery_wms_gateway.times_assemble_called() == 0

    assert grocery_wms_gateway.times_close_called() == want_wms_close
    assert (
        grocery_wms_gateway.times_set_eda_status_called()
        == want_set_delivered_eda_status
    )


@pytest.mark.parametrize('error_code', [400, 404, 409])
async def test_error_codes_from_wms_gateway(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        cargo,
        error_code,
):
    dispatch_id = 'dispatch_id_1234'

    order = models.Order(
        pgsql=pgsql,
        status='canceled',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='delivering',
            dispatch_cargo_status='new',
        ),
        order_version=1,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_wms_gateway.set_http_resp(code=error_code)

    cargo.set_data(items=grocery_cart.get_items(), dispatch_id=dispatch_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    if error_code in (404, 409):
        assert response.status_code == 200
    elif error_code == 400:
        assert response.status_code == 500


@pytest.mark.parametrize('with_tristero_parcels', [True, False])
@pytest.mark.parametrize('order_status,', ['closed', 'canceled'])
async def test_tristero_set_delivered_or_canceled(
        taxi_grocery_orders,
        pgsql,
        mockserver,
        grocery_cart,
        grocery_wms_gateway,
        processing,
        grocery_depots,
        with_tristero_parcels,
        order_status,
):
    depot_id = '1234'

    grocery_depots.add_depot(legacy_depot_id=depot_id)

    orderstate = models.OrderState(
        wms_reserve_status='success',
        hold_money_status='success',
        close_money_status='success',
    )
    order = models.Order(
        pgsql=pgsql, status=order_status, state=orderstate, depot_id=depot_id,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    item_id = (
        '98765432-10ab-cdef-0000-00020001:st-pa'
        if with_tristero_parcels
        else '98765432-10ab-cdef-0000-00020001'
    )

    grocery_cart.set_items([models.GroceryCartItem(item_id=item_id)])
    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v3',
            'payload': {},
        },
    )

    order.update()

    assert response.status_code == 200

    setstate_event = processing_noncrit.check_noncrit_event(
        processing, order.order_id, 'tristero_setstate',
    )
    if with_tristero_parcels:
        assert setstate_event is not None

        body = setstate_event['parcels_body']

        state = (
            'order_cancelled' if (order_status == 'canceled') else 'delivered'
        )
        assert body['state'] == state
        assert body['state_meta']['order_id'] == order.order_id
        assert body['parcel_wms_ids'][0] == item_id
    else:
        assert setstate_event is None


@pytest.mark.parametrize('is_canceled', [True, False])
@pytest.mark.parametrize('promocode_source', ['taxi', 'eats'])
@pytest.mark.parametrize('referral_complete_error_code', [None, 400])
async def test_coupon_finish(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        coupons,
        is_canceled,
        promocode_source,
        referral_complete_error_code,
        grocery_depots,
        taxi_grocery_orders_monitor,
):
    promocode = 'SOME_PROMOCODE'
    personal_phone_id = 'azsa'
    yandex_uid = '1232146712'
    phone_id = 'ndajkscs'
    discount = '100'
    depot_id = '1234'

    grocery_depots.add_depot(legacy_depot_id=depot_id)

    order = models.Order(
        pgsql=pgsql,
        status='canceled' if is_canceled else 'closed',
        phone_id=phone_id,
        state=models.OrderState(close_money_status='success'),
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_promocode(
        code=promocode, valid=True, source=promocode_source, discount=discount,
    )

    coupons.check_request(
        coupon_finish_order_id=f'cart_id:{order.cart_id}',
        phone_id=phone_id,
        yandex_uid=yandex_uid,
        token=order.cart_id + promocode,
        coupon_id=promocode,
        cost_usage=discount,
        order_id=order.order_id,
        success=(not is_canceled),
        service='grocery',
    )

    coupons.set_referral_error_code(referral_complete_error_code)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor='grocery_orders_coupons_finished',
            labels={'country': 'Russia'},
    ) as collector:
        response = await taxi_grocery_orders.post(
            '/processing/v1/finish',
            json={
                'order_id': order.order_id,
                'order_version': order.order_version,
                'flow_version': 'grocery_flow_v1',
                'payload': {},
            },
        )

    order.update()
    assert response.status_code == 200

    if promocode_source == 'taxi':
        assert coupons.times_coupon_finish_called() == 1

        if not is_canceled:
            assert coupons.times_referral_complete_called() == 1

            metric = collector.get_single_collected_metric()
            assert metric.value == 1
            assert metric.labels == {
                'country': 'Russia',
                'app_name': 'Yango (android)',
                'sensor': 'grocery_orders_coupons_finished',
            }
        else:
            assert coupons.times_referral_complete_called() == 0
    else:
        assert coupons.times_coupon_finish_called() == 0
        assert coupons.times_referral_complete_called() == 0


@pytest.mark.now(consts.NOW)
@experiments.GOAL_RESERVATION
@pytest.mark.experiments3(
    name='grocery_orders_update_goals',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enable': False},
    is_config=True,
)
@pytest.mark.parametrize('status', ['closed', 'canceled'])
@pytest.mark.parametrize('goal_release_status', [200, 400])
async def test_goals_update(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_goals,
        grocery_depots,
        processing,
        status,
        goal_release_status,
):
    reward_sku = 'reward_item_id:st-gr'
    orderstate = models.OrderState()
    orderstate.wms_reserve_status = 'success'
    orderstate.hold_money_status = 'success'
    orderstate.close_money_status = 'success'

    depot_id = '1234'
    grocery_depots.add_depot(legacy_depot_id=depot_id)

    order = models.Order(
        pgsql=pgsql,
        status=status,
        state=orderstate,
        dispatch_status_info=models.DispatchStatusInfo(),
        depot_id=depot_id,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_items([models.GroceryCartItem(reward_sku, quantity='1')])

    grocery_goals.skus = [reward_sku]
    grocery_goals.order_id = order.order_id
    release_called = grocery_goals.release_times_called()

    if goal_release_status == 400:
        grocery_goals.response_http_code = 400
        grocery_goals.error_code = 'user_has_no_such_reward'
        grocery_goals.failed_skus = [reward_sku]

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='goals'))

    if status == 'canceled':
        assert not events
        assert grocery_goals.release_times_called() - release_called == 1
    if status == 'closed':
        assert len(events) == 1
        event = events[0]

        assert event.payload['order_id'] == order.order_id
        assert event.payload['reason'] == 'close'
        assert grocery_goals.release_times_called() == release_called


@pytest.mark.now(consts.NOW)
@pytest.mark.experiments3(
    name='grocery_orders_update_goals',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always false',
            'predicate': {'type': 'true'},
            'value': {'enabled': False},
        },
    ],
    default_value={'enable': False},
    is_config=True,
)
async def test_goals_update_disable(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, processing,
):
    orderstate = models.OrderState()
    orderstate.wms_reserve_status = 'success'
    orderstate.hold_money_status = 'success'
    orderstate.close_money_status = 'success'

    depot_id = '1234'
    grocery_depots.add_depot(legacy_depot_id=depot_id)

    order = models.Order(
        pgsql=pgsql,
        status='closed',
        state=orderstate,
        dispatch_status_info=models.DispatchStatusInfo(),
        depot_id=depot_id,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='goals'))
    assert not events


@pytest.mark.now(consts.NOW)
async def test_retry_interval(processing, _run_with_error):
    retry_count = 2
    event_policy = {
        'retry_count': retry_count,
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
    }
    order = await _run_with_error(expected_code=200, event_policy=event_policy)

    events = list(processing.events(scope='grocery', queue='processing'))

    event_policy['retry_count'] += 1
    assert len(events) == 1
    assert events[0].payload == {
        'event_policy': event_policy,
        'order_id': order.order_id,
        'reason': 'finish',
    }

    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)


async def test_stop_after(
        _run_with_error,
        _retry_after_error,
        processing,
        mocked_time,
        grocery_depots,
        grocery_cart,
        pgsql,
):
    mocked_time.set(consts.NOW_DT)
    # Without retry_interval and error_after we cannot return 429 error, we
    # should return 500 to see it in alert chat/grafana.
    order = await _run_with_error(
        expected_code=500,
        event_policy={
            'stop_retry_after': {'minutes': consts.STOP_AFTER_MINUTES},
        },
    )

    # try again later, after "stop_after".
    await _retry_after_error(
        order=order,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy={
            'stop_retry_after': helpers.skip_minutes(
                consts.STOP_AFTER_MINUTES,
            ),
        },
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


async def test_error_after(
        _run_with_error, processing, mocked_time, _retry_after_error,
):
    mocked_time.set(consts.NOW_DT)
    # With `error_after` we don't want to see messages in alert chat, we want
    # to ignore problems until `error_after` happened.
    order = await _run_with_error(
        expected_code=429,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
    )

    await _retry_after_error(
        order=order,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
        expected_code=500,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


async def test_retry_after_error_behaviour(
        _run_with_error, processing, mocked_time, _retry_after_error,
):
    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }
    mocked_time.set(consts.NOW_DT)
    # With error after we don't want to see messages in alert chat, we want to
    # ignore problems until `error_after` happened.
    order = await _run_with_error(expected_code=200, event_policy=event_policy)

    events = list(processing.events(scope='grocery', queue='processing'))

    events_after_first_retry = 1

    assert len(events) == events_after_first_retry
    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)

    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }

    await _retry_after_error(
        order=order,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=500,
    )

    await _retry_after_error(
        order=order,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == events_after_first_retry


@pytest.fixture
def _retry_after_error(mocked_time, taxi_grocery_orders):
    return helpers.retry_processing(
        '/processing/v1/finish', mocked_time, taxi_grocery_orders,
    )


@pytest.fixture
def _run_with_error(
        pgsql,
        grocery_depots,
        grocery_cart,
        taxi_grocery_orders,
        grocery_wms_gateway,
):
    async def _do(expected_code, event_policy, times_called=1):
        order = models.Order(pgsql=pgsql, status='closed')
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)
        grocery_cart.set_cart_data(cart_id=order.cart_id)

        grocery_wms_gateway.set_http_resp(code=500)

        response = await taxi_grocery_orders.post(
            '/processing/v1/finish',
            json={
                'order_id': order.order_id,
                'times_called': times_called,
                'event_policy': event_policy,
                'payload': {},
            },
        )

        assert response.status_code == expected_code

        return order

    return _do
