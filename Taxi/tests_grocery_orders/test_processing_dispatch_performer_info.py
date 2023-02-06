import uuid

import pytest

from . import consts
from . import helpers
from . import models


NOW = '2020-11-12T13:00:50.283761+00:00'
AFTER_HOUR = '2020-11-12T14:00:50.283761+00:00'
COURIER_SERVICE_ID = '100123'
COURIER_SERVICE = {
    'courier_service_id': int(COURIER_SERVICE_ID),
    'name': 'Yandex',
    'tin': '7707083893',
    'vat': 20,
}
COURIER_SERVICE_BILLING = 'courier_service'

TAXI_EATS_COURIER_ID = 'taxi-eats-courier-id-123'

TAXI_COURIER_INFO_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_taxi_courier_info',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled ISR',
            'predicate': {'type': 'true'},
            'value': {
                'courier_service_id': COURIER_SERVICE_ID,
                'eats_courier_id': TAXI_EATS_COURIER_ID,
            },
        },
    ],
    is_config=True,
)


@pytest.fixture
def _prepare(
        pgsql, grocery_cart, grocery_supply, grocery_depots, grocery_dispatch,
):
    def _do(
            transport_type,
            eats_courier_id,
            balance_client_id=None,
            courier_service=None,
            courier_billing_type=None,
            dispatch_id=str(uuid.uuid4()),
    ):
        driver_id = 'driver_id_123'
        courier_name = 'Ivan'
        courier_full_name = 'Ivanov Ivan Ivanovich'

        order = models.Order(
            pgsql=pgsql,
            status='delivering',
            dispatch_status_info=models.DispatchStatusInfo(
                dispatch_id=dispatch_id,
                dispatch_status='accepted',
                dispatch_cargo_status='accepted',
                dispatch_driver_id=driver_id,
                dispatch_courier_name=courier_full_name,
                dispatch_courier_first_name=courier_name,
                dispatch_transport_type=transport_type,
                dispatch_delivered_eta_ts=AFTER_HOUR,
                dispatch_pickuped_eta_ts=NOW,
                dispatch_status_meta={
                    'cargo_dispatch': {'dispatch_delivery_type': 'courier'},
                },
            ),
        )
        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        grocery_dispatch.set_data(
            dispatch_id=dispatch_id,
            items=grocery_cart.get_items(),
            status='delivering',
            performer_name=courier_full_name,
            performer_id=driver_id,
            eats_profile_id=eats_courier_id,
            transport_type=transport_type,
        )

        if eats_courier_id:
            grocery_supply.check_courier_info(courier_id=eats_courier_id)
            grocery_supply.set_courier_response(
                response={
                    'courier_id': eats_courier_id,
                    'transport_type': transport_type,
                    'full_name': courier_full_name,
                    'billing_client_id': balance_client_id,
                    'courier_service': courier_service,
                    'billing_type': courier_billing_type,
                },
            )
        return order

    return _do


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
@pytest.mark.parametrize('transport_type', ['rover', 'bicycle'])
async def test_happy_path(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_dispatch,
        grocery_cart,
        processing,
        _prepare,
        transport_type,
        personal,
):
    driver_id = 'driver_id_123'
    eats_courier_id = 'eats_courier_id_123'
    courier_name = 'Ivan'
    courier_full_name = 'Ivanov Ivan Ivanovich'
    dispatch_track_version = 10
    balance_client_id = 'balance_client_id:qwe'

    order = _prepare(
        transport_type=transport_type,
        eats_courier_id=eats_courier_id,
        courier_service={
            **COURIER_SERVICE,
            'billing_client_id': balance_client_id,
        },
        balance_client_id=balance_client_id,
        courier_billing_type=COURIER_SERVICE_BILLING,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': driver_id,
            'dispatch_track_version': dispatch_track_version,
            'payload': {'courier_name': courier_name},
        },
    )

    assert response.status_code == 200

    assert personal.times_tins_store_called() == 1

    assert grocery_dispatch.times_performer_info_called() == 1
    assert grocery_supply.times_courier_called() == 1

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    courier_vin = {}
    courier_type = {}
    if transport_type == 'rover':
        courier_vin['courier_vin'] = courier_full_name
        courier_type['courier_type'] = 'rover'
    else:
        courier_type['courier_type'] = 'human'

    assert len(events) == 1
    assert events[0].payload == {
        'order_id': order.order_id,
        'reason': 'courier_info_update',
        'flow_version': 'grocery_flow_v1',
        'depot_id': order.depot_id,
        'related_orders': [order.order_id],
        'courier_name': courier_name,
        'courier_delivery_promise': AFTER_HOUR,
        'courier_external_id': eats_courier_id,
        'dispatch_delivery_type': 'courier',
        'taxi_driver_uuid': driver_id,
        **courier_vin,
        **courier_type,
    }

    order.update()

    assert order.dispatch_performer.driver_id == driver_id
    assert order.dispatch_performer.eats_courier_id == eats_courier_id
    assert order.dispatch_performer.courier_full_name == courier_full_name
    assert order.dispatch_performer.balance_client_id == balance_client_id
    assert order.dispatch_performer.personal_tin_id == 'tin_id_123'


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
async def test_other_driver_id(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_dispatch,
        grocery_cart,
        processing,
        _prepare,
):
    other_driver_id = 'other_driver_id_123'
    dispatch_track_version = 10

    order = _prepare(
        transport_type='bicycle', eats_courier_id='eats_courier_id_123',
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': other_driver_id,
            'dispatch_track_version': dispatch_track_version,
            'payload': {},
        },
    )

    assert response.status_code == 200
    assert grocery_dispatch.times_performer_info_called() == 0
    assert grocery_supply.times_courier_called() == 0


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
@pytest.mark.now(NOW)
async def test_cargo_fail(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_dispatch,
        grocery_cart,
        processing,
        _prepare,
):
    driver_id = 'driver_id_123'
    dispatch_track_version = 10
    event_policy = {'retry_interval': 3600, 'retry_count': 2}
    retry_event_policy = {'retry_interval': 3600, 'retry_count': 3}

    order = _prepare(
        transport_type='bicycle', eats_courier_id='eats_courier_id_123',
    )
    grocery_dispatch.set_data(performer_info_error=404)

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': driver_id,
            'dispatch_track_version': dispatch_track_version,
            'event_policy': event_policy,
            'payload': {},
        },
    )

    assert response.status_code == 200

    assert grocery_dispatch.times_performer_info_called() == 1
    assert grocery_supply.times_courier_called() == 0

    events = list(processing.events(scope='grocery', queue='processing'))

    assert len(events) == 1
    event = events[0]

    assert event.due == AFTER_HOUR

    assert event.payload == {
        'reason': 'dispatch_new_performer',
        'order_id': order.order_id,
        'driver_id': driver_id,
        'event_policy': retry_event_policy,
        'flow_version': order.grocery_flow_version,
        'dispatch_track_version': dispatch_track_version,
    }


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
@TAXI_COURIER_INFO_EXPERIMENT
async def test_happy_path_taxi_courier(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_dispatch,
        grocery_cart,
        processing,
        _prepare,
        personal,
):
    driver_id = 'driver_id_123'
    courier_name = 'Ivan'
    dispatch_track_version = 10
    transport_type = 'car'

    order = _prepare(transport_type=transport_type, eats_courier_id='')

    grocery_supply.check_courier_service_info(
        courier_service_id=COURIER_SERVICE_ID,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': driver_id,
            'dispatch_track_version': dispatch_track_version,
            'payload': {},
        },
    )

    assert response.status_code == 200

    assert personal.times_tins_store_called() == 1
    assert grocery_dispatch.times_performer_info_called() == 1
    assert grocery_supply.times_courier_called() == 0
    assert grocery_supply.times_courier_service_called() == 1

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert len(events) == 1
    assert events[0].payload == {
        'order_id': order.order_id,
        'reason': 'courier_info_update',
        'flow_version': 'grocery_flow_v1',
        'depot_id': order.depot_id,
        'related_orders': [order.order_id],
        'courier_name': courier_name,
        'courier_type': 'human',
        'courier_delivery_promise': AFTER_HOUR,
        'dispatch_delivery_type': 'courier',
        'taxi_driver_uuid': driver_id,
    }

    order.update()
    assert order.dispatch_performer.driver_id == driver_id
    assert order.dispatch_performer.eats_courier_id == TAXI_EATS_COURIER_ID


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=False)
async def test_off(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_dispatch,
        grocery_cart,
        processing,
        _prepare,
):
    dispatch_track_version = 10

    order = _prepare(transport_type='bicycle', eats_courier_id='123')

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': order.dispatch_status_info.dispatch_id,
            'dispatch_track_version': dispatch_track_version,
            'payload': {},
        },
    )

    assert response.status_code == 200

    assert grocery_dispatch.times_performer_info_called() == 0
    assert grocery_supply.times_courier_called() == 0


@pytest.mark.parametrize(
    'courier_billing_type,'
    ' client_id,'
    ' cs_client_id,'
    ' expected_client_id',
    [
        ('courier_service', 'client_id', 'cs_client_id', 'cs_client_id'),
        ('self_employed', 'client_id', 'cs_client_id', 'client_id'),
        ('self_employed', None, 'cs_client_id', 'cs_client_id'),
        ('self_employed', None, None, None),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
async def test_billing_client_id_from_service(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_dispatch,
        grocery_cart,
        processing,
        _prepare,
        courier_billing_type,
        client_id,
        cs_client_id,
        expected_client_id,
):
    transport_type = 'rover'
    driver_id = 'driver_id_123'
    eats_courier_id = 'eats_courier_id_123'
    dispatch_track_version = 10
    order = _prepare(
        transport_type=transport_type,
        eats_courier_id=eats_courier_id,
        courier_billing_type=courier_billing_type,
        balance_client_id=client_id,
        courier_service={
            'name': 'name',
            'courier_service_id': int(COURIER_SERVICE_ID),
            'billing_client_id': cs_client_id,
        },
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': driver_id,
            'dispatch_track_version': dispatch_track_version,
            'payload': {},
        },
    )

    assert response.status_code == 200

    assert grocery_dispatch.times_performer_info_called() == 1
    assert grocery_supply.times_courier_called() == 1

    order.update()
    assert order.dispatch_performer.balance_client_id == expected_client_id


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
async def test_stop_after(
        taxi_grocery_orders,
        grocery_dispatch,
        processing,
        mocked_time,
        _prepare,
):
    mocked_time.set(consts.NOW_DT)

    driver_id = 'driver_id_123'
    dispatch_track_version = 10

    order = _prepare(
        transport_type='bicycle', eats_courier_id='eats_courier_id_123',
    )
    event_policy = {
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_count': 2,
    }

    mocked_time.set(helpers.skip_minutes_dt(consts.STOP_AFTER_MINUTES + 1))

    grocery_dispatch.set_data(performer_info_error=404)
    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': driver_id,
            'dispatch_track_version': dispatch_track_version,
            'event_policy': event_policy,
            'payload': {},
        },
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
async def test_error_after(
        processing,
        mocked_time,
        taxi_grocery_orders,
        grocery_dispatch,
        _prepare,
):
    mocked_time.set(consts.NOW_DT)

    driver_id = 'driver_id_123'
    dispatch_track_version = 10

    order = _prepare(
        transport_type='bicycle', eats_courier_id='eats_courier_id_123',
    )
    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'retry_count': 2,
    }

    mocked_time.set(helpers.skip_minutes_dt(consts.ERROR_AFTER_MINUTES + 1))

    grocery_dispatch.set_data(performer_info_error=404)
    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': driver_id,
            'dispatch_track_version': dispatch_track_version,
            'event_policy': event_policy,
            'payload': {},
        },
    )

    assert response.status_code == 500

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


@pytest.mark.parametrize('eats_courier_id', ['eats_courier_id_123', ''])
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
@pytest.mark.parametrize('app_name', ['lavka_iphone', 'eda_webview_iphone'])
@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
@TAXI_COURIER_INFO_EXPERIMENT
async def test_send_courier_info_to_stq(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_dispatch,
        grocery_cart,
        processing,
        _prepare,
        grocery_eats_gateway,
        mockserver,
        app_name,
        eats_courier_id,
):
    dispatch_track_version = 10

    claim_id_ok = 'claim_id_good'
    claim_id_not_ok = 'claim_id_bad'

    order = _prepare(
        transport_type='bicycle',
        eats_courier_id=eats_courier_id,
        dispatch_id=str(uuid.uuid4()),
    )
    order.upsert(app_info=f'app_name={app_name}')
    grocery_dispatch.set_data(performer_name='Ivan')

    grocery_eats_gateway.set_courier_data(
        suffix_stq_task_id='42',
        eats_courier_id=eats_courier_id,
        courier_name='Ivan',
        claim_id=claim_id_ok,
    )
    if eats_courier_id == '':
        grocery_eats_gateway.set_courier_data(
            eats_courier_id=TAXI_EATS_COURIER_ID,
            courier_name='Ivan',
            claim_id=claim_id_ok,
        )

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/admin/info',
    )
    def claim_info(request):
        return {
            'dispatches': [
                {
                    'dispatch_id': order.dispatch_status_info.dispatch_id,
                    'cargo_details': [
                        {
                            'claim_id': claim_id_ok,
                            'claim_status': 'new',
                            'is_current_claim': True,
                        },
                        {
                            'claim_id': claim_id_not_ok,
                            'claim_status': 'cancelled',
                        },
                    ],
                },
            ],
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': 'driver_id_123',
            'dispatch_track_version': dispatch_track_version,
            'payload': {},
            'times_called': 42,
        },
    )

    assert response.status_code == 200
    assert grocery_eats_gateway.times_stq_couriers() == (
        1 if app_name == 'eda_webview_iphone' else 0
    )
    assert claim_info.times_called == (
        1 if app_name == 'eda_webview_iphone' else 0
    )
