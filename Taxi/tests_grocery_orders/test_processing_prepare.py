import datetime
import decimal

# pylint: disable=import-error
from grocery_mocks.models import country as country_models
import pytest

from . import configs
from . import consts
from . import headers
from . import helpers
from . import models
from . import order_log
from . import processing_noncrit


ERROR_AFTER_DT = consts.NOW_DT + datetime.timedelta(
    minutes=processing_noncrit.ERROR_AFTER_MINUTES,
)
STOP_RETRY_AFTER_DT = consts.NOW_DT + datetime.timedelta(
    minutes=processing_noncrit.STOP_RETRY_AFTER_MINUTES,
)


def enable_add_address(experiments3, enable: bool):
    experiments3.add_config(
        name='grocery_orders_enable_add_address',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enable': enable},
            },
        ],
    )


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_STATUS_SHOW_NOTIFICATION=True)
@pytest.mark.config(GROCERY_ORDERS_SEND_ATLAS_EVENTS=True)
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize(
    'init_status,status_code',
    [('closed', 409), ('draft', 200), ('checked_out', 200)],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_marketing,
        processing,
        init_status,
        status_code,
):
    taxi_user_id = 'taxi-user-id'
    app_name = 'mobileweb_yango_android'
    app_info = f'app_name={app_name}'
    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        meet_outside=True,
        no_door_call=False,
        taxi_user_id=taxi_user_id,
        app_info=app_info,
    )

    assert order.status == init_status

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items([models.GroceryCartItem('parcel_item_id:st-pa')])
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_order_conditions(delivery_cost='500', max_eta=15)
    grocery_cart.set_delivery_type('courier')

    depot = grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    assert grocery_cart.set_order_id_times_called() == 0
    order.update()

    assert response.status_code == status_code
    if status_code == 200:
        event_policy = {
            'stop_retry_after': STOP_RETRY_AFTER_DT.isoformat(),
            'error_after': ERROR_AFTER_DT.isoformat(),
            'retry_interval': processing_noncrit.RETRY_INTERVAL_MINUTES * 60,
            'retry_count': 1,
        }
        create_event = processing_noncrit.check_noncrit_event(
            processing,
            order.order_id,
            'created',
            taxi_user_id=taxi_user_id,
            app_name=app_name,
            depot_id=order.depot_id,
            event_policy=event_policy,
            check_auth_context=True,
        )
        assert create_event is not None

        notify_event = processing_noncrit.check_noncrit_event(
            processing, order.order_id, 'order_notification',
        )

        assert notify_event is not None
        notification_expected = {
            'order_id': order.order_id,
            'reason': 'order_notification',
            'payload': {},
            'code': 'accepted',
        }
        processing_noncrit.check_push_notification(
            notify_event, notification_expected,
        )
        state_change_event = processing_noncrit.check_noncrit_event(
            processing, order.order_id, 'status_change',
        )
        order_log.check_order_log_payload(
            state_change_event,
            order,
            cart_items=[models.GroceryCartItem('parcel_item_id:st-pa')],
            depot=depot,
            is_checkout=True,
            delivery_cost='500',
        )

        assert (
            state_change_event['atlas_order_info']['order_id']
            == order.order_id
        )

        assert grocery_marketing.increment_times_called() == 1


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_STATUS_SHOW_NOTIFICATION=False)
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize(
    'init_status,status_code',
    [('closed', 409), ('draft', 200), ('checked_out', 200)],
)
async def test_status_show(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        init_status,
        status_code,
):
    order = models.Order(pgsql=pgsql, status=init_status)

    assert order.status == init_status

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items([models.GroceryCartItem('parcel_item_id:st-pa')])
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_order_conditions(delivery_cost='500')

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    order.update()

    assert response.status_code == status_code
    if status_code == 200:
        notify_event = processing_noncrit.check_noncrit_event(
            processing, order.order_id, 'notification',
        )
        assert notify_event is None


def enable_antifraud_grocery_cycle(enable_antifraud: bool, experiments3):
    experiments3.add_config(
        name='grocery_orders_enable_antifraud',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'enable_eats_order_cycle': False,
            'enable_grocery_order_cycle': enable_antifraud,
        },
    )


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_STATUS_SHOW_NOTIFICATION=True)
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize(
    'is_banned, antifraud_enabled',
    [(True, True), (True, False), (False, True), (False, False)],
)
@pytest.mark.parametrize('additional_phone_code', [None, '777'])
async def test_antifraud(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        antifraud,
        experiments3,
        is_banned,
        antifraud_enabled,
        additional_phone_code,
):
    user_agent = 'user-agent'
    appmetrica_device_id = 'appmetrica_id'
    order = models.Order(
        pgsql=pgsql,
        status='draft',
        user_agent=user_agent,
        comment='order_comment',
        appmetrica_device_id=appmetrica_device_id,
        additional_phone_code=additional_phone_code,
    )
    short_address = f'{order.city}, {order.street} {order.house} {order.flat}'

    enable_antifraud_grocery_cycle(antifraud_enabled, experiments3)
    antifraud.set_is_fraud(is_banned)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items([models.GroceryCartItem('parcel_item_id:st-pa')])
    payment_method_type = 'card'
    payment_method_id = 'test_payment_method_id'
    grocery_cart.set_payment_method(
        {'type': payment_method_type, 'id': payment_method_id},
    )
    delivery_cost = 500
    grocery_cart.set_order_conditions(delivery_cost=str(delivery_cost))

    items_price = sum(
        [
            decimal.Decimal(item.price) * decimal.Decimal(item.quantity)
            for item in grocery_cart.get_items()
        ],
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    antifraud.check_antifraud_request(
        user_id=headers.YANDEX_UID,
        user_id_service='passport',
        user_personal_phone_id=headers.PERSONAL_PHONE_ID,
        client_ip=headers.USER_IP,
        user_agent=user_agent,
        application_type='yango_android',
        service_name='grocery',
        order_amount=str(items_price + delivery_cost),
        order_currency=grocery_cart.get_items()[0].currency,
        short_address=short_address,
        address_comment=order.comment,
        order_coordinates={
            'lon': order.location_as_point()[1],
            'lat': order.location_as_point()[0],
        },
        payment_method_id=payment_method_id,
        payment_method=payment_method_type,
        user_device_id=appmetrica_device_id,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers={**headers.HEADER_APP_INFO_YANGO},
    )

    order.update()

    if is_banned and antifraud_enabled and not additional_phone_code:
        assert response.status_code == 409

        basic_events = list(
            processing.events(scope='grocery', queue='processing'),
        )
        assert len(basic_events) == 1
        assert basic_events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_type': 'fraud',
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_message': 'fraud detected',
            'times_called': 0,
        }

        assert order.desired_status == 'canceled'
    else:
        assert response.status_code == 200


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_STATUS_SHOW_NOTIFICATION=True)
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
async def test_antifraud_kwargs(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        antifraud,
        experiments3,
):
    user_agent = 'user-agent'
    appmetrica_device_id = 'appmetrica_id'
    order = models.Order(
        pgsql=pgsql,
        status='draft',
        user_agent=user_agent,
        comment='order_comment',
        appmetrica_device_id=appmetrica_device_id,
    )

    enable_antifraud_grocery_cycle(
        enable_antifraud=True, experiments3=experiments3,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items([models.GroceryCartItem('parcel_item_id:st-pa')])
    payment_method_type = 'card'
    payment_method_id = 'test_payment_method_id'
    grocery_cart.set_payment_method(
        {'type': payment_method_type, 'id': payment_method_id},
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    exp3_recorder = experiments3.record_match_tries(
        'grocery_orders_enable_antifraud',
    )

    await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers={**headers.HEADER_APP_INFO_YANGO},
    )

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert (
        exp3_kwargs['country_iso3']
        == country_models.Country.Russia.country_iso3
    )
    assert exp3_kwargs['consumer'] == 'grocery-orders/submit'
    assert exp3_kwargs['region_id'] == 213
    assert exp3_kwargs['personal_phone_id'] == headers.PERSONAL_PHONE_ID
    assert exp3_kwargs['payment_method_type'] == payment_method_type


@configs.GROCERY_PAYMENT_METHOD_VALIDATION
@pytest.mark.parametrize('is_invalid_pm', [False, True])
@pytest.mark.now(consts.NOW)
async def test_payment_method_validation(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_payments,
        grocery_depots,
        processing,
        is_invalid_pm,
):
    pm_type = 'card'
    pm_id = 'payment_method:123'

    order = models.Order(pgsql=pgsql, status='draft')

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method({'type': pm_type, 'id': pm_id})

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    if is_invalid_pm:
        grocery_payments.mock_validate(
            errors=[
                {
                    'method': {'id': pm_id, 'type': pm_type},
                    'error_code': 'not_exists',
                },
            ],
        )

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    order.update()

    if is_invalid_pm:
        assert response.status_code == 200

        basic_events = list(
            processing.events(scope='grocery', queue='processing'),
        )
        assert len(basic_events) == 1
        assert basic_events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_type': 'invalid_payment_method',
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_message': pm_type,
            'times_called': 0,
        }

        assert order.desired_status == 'canceled'
    else:
        assert response.status_code == 200


@configs.GROCERY_PAYMENT_METHOD_VALIDATION
@pytest.mark.parametrize(
    'need_track_payment, verified', [(True, False), (False, True)],
)
async def test_payments_validation(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_payments,
        grocery_depots,
        need_track_payment,
        verified,
):
    order = models.Order(
        pgsql=pgsql,
        status='draft',
        order_settings={'need_track_payment': need_track_payment},
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    meta = {'card': {'verified': verified, 'issuer_country': 'RUS'}}
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id', 'meta': meta})
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_payments.check_validate(
        payment_methods=[{'type': 'card', 'id': 'id', 'meta': meta}],
        need_track_payment=need_track_payment,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    assert response.status_code == 200
    assert grocery_payments.times_validate_called() == 1


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_STATUS_SHOW_NOTIFICATION=True)
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize('add_address_enabled', [True, False])
async def test_add_address(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        experiments3,
        add_address_enabled,
):
    enable_add_address(experiments3, add_address_enabled)
    order = models.Order(
        pgsql=pgsql,
        status='draft',
        left_at_door=True,
        meet_outside=True,
        no_door_call=True,
    )

    assert order.status == 'draft'

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items([models.GroceryCartItem('parcel_item_id:st-pa')])
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_order_conditions(delivery_cost='500', max_eta=15)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    order.update()

    assert response.status_code == 200

    add_address_event = processing_noncrit.check_noncrit_event(
        processing, order.order_id, 'add_address',
    )
    if add_address_enabled:
        assert add_address_event['order_id'] == order.order_id
        assert add_address_event['left_at_door'] is True
        assert add_address_event['meet_outside'] is True
        assert add_address_event['no_door_call'] is True
    else:
        assert add_address_event is None


@pytest.mark.parametrize(
    'has_promo, valid', [(True, True), (True, False), (False, True)],
)
async def test_promocode_reserve(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        coupons,
        processing,
        valid,
        has_promo,
):
    promocode = 'LAVKA100'
    phone_id = '238u2iod'
    yandex_uid = '12334321901'
    order = models.Order(
        pgsql=pgsql,
        status='checked_out',
        phone_id=phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    if has_promo:
        grocery_cart.set_promocode(code=promocode, valid=True)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    coupons.check_request(
        coupon_id=promocode,
        phone_id=phone_id,
        yandex_uid=yandex_uid,
        token='{}{}'.format(order.cart_id, promocode),
    )

    coupons.set_valid(valid=valid)

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert coupons.times_coupon_reserve_called() == (1 if has_promo else 0)

    events = list(processing.events(scope='grocery', queue='processing'))
    order.update()
    if not valid:
        assert response.status_code == 409

        assert len(events) == 1

        payload = events[0].payload
        assert payload['reason'] == 'cancel'
        assert order.desired_status == 'canceled'
    else:
        assert response.status_code == 200
        assert not events


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.config(GROCERY_ORDERS_STATUS_SHOW_NOTIFICATION=True)
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize(
    'set_order_id_status_code, prepare_status_code',
    [(200, 200), (400, 409), (404, 409), (409, 409), (500, 500)],
)
async def test_set_order_id(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        experiments3,
        set_order_id_status_code,
        prepare_status_code,
):
    order = models.Order(
        pgsql=pgsql, status='draft', grocery_flow_version='tristero_flow_v2',
    )

    assert order.status == 'draft'

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items([models.GroceryCartItem('parcel_item_id:st-pa')])
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_order_conditions(delivery_cost='500', max_eta=15)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_set_order_id_error(set_order_id_status_code)

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    assert response.status_code == prepare_status_code

    order.update()

    if prepare_status_code == 409:
        events = list(processing.events(scope='grocery', queue='processing'))

        assert len(events) == 1
        assert events[0].payload['order_id'] == order.order_id
        assert events[0].payload['reason'] == 'cancel'
        assert order.desired_status == 'canceled'


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
        'order_version': order.order_version,
        'reason': 'created',
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
        '/processing/v1/prepare', mocked_time, taxi_grocery_orders,
    )


@pytest.fixture
def _run_with_error(
        pgsql, grocery_depots, grocery_cart, taxi_grocery_orders, coupons,
):
    async def _do(expected_code, event_policy, times_called=1):
        order = models.Order(pgsql=pgsql, status='checked_out')
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_promocode(code='LAVKA100', valid=True)
        coupons.set_reserve_error_code(code=500)

        response = await taxi_grocery_orders.post(
            '/processing/v1/prepare',
            json={
                'order_id': order.order_id,
                'order_version': order.order_version,
                'times_called': times_called,
                'event_policy': event_policy,
                'payload': {},
            },
        )

        assert response.status_code == expected_code

        return order

    return _do


@pytest.mark.now(consts.NOW)
async def test_bad_fraud_response(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        antifraud,
        experiments3,
):
    order = models.Order(
        pgsql=pgsql, status='draft', grocery_flow_version='tristero_flow_v2',
    )

    antifraud.set_error_code(500)

    enable_antifraud_grocery_cycle(True, experiments3)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    assert response.status_code == 200
