import datetime

import pytest
import pytz

from . import utils


PERIODIC_NAME = 'cargo-info-synchronizer'

TERMINAL_CARGO_ORDER_STATUSES = [
    'delivered',
    'delivered_finish',
    'failed',
    'cancelled',
    'cancelled_with_payment',
    'cancelled_by_taxi',
    'cancelled_with_items_on_hands',
    'auto_complete',
]

PERFORMER_FOUND_STATUSES = [
    'pickup_arrived',
    'pickuped',
    'pay_waiting',
    'delivered',
    'delivered_finish',
    'failed',
    'cancelled',
    'cancelled_with_payment',
    'cancelled_by_taxi',
    'cancelled_with_items_on_hands',
    'returning',
    'returned',
]


@pytest.mark.now('2021-06-08 10:00:00+05')
@utils.cargo_info_synchronizer_config()
@pytest.mark.parametrize(
    'order_state', ['new', 'picking', 'complete', 'cancelled'],
)
@pytest.mark.parametrize(
    'cargo_order_status',
    [
        None,
        'estimating',
        'accepted',
        'pickup_arrived',
        'pickuped',
        'pay_waiting',
    ],
)
@pytest.mark.parametrize(
    'cargo_order_status_new',
    [
        'estimating',
        'accepted',
        'pickup_arrived',
        'pickuped',
        'pay_waiting',
        'delivered',
        'delivered_finish',
        'failed',
        'cancelled',
        'cancelled_with_payment',
        'cancelled_by_taxi',
        'cancelled_with_items_on_hands',
    ],
)
async def test_sync_cargo_info_cargo_order_status(
        taxi_eats_picker_orders,
        now,
        create_order,
        get_order,
        cargo_environment,
        order_state,
        cargo_order_status,
        cargo_order_status_new,
):
    claim_id = 'claim_id_0'
    order_id = create_order(
        eats_id='order_0',
        claim_id=claim_id,
        state=order_state,
        cargo_order_status=cargo_order_status,
    )

    now = now.replace(tzinfo=pytz.utc)

    point_id_0 = cargo_environment.create_point(
        'source', 'pending', now + datetime.timedelta(minutes=10),
    )
    point_id_1 = cargo_environment.create_point(
        'destination', 'pending', now + datetime.timedelta(minutes=20),
    )
    phone_id = cargo_environment.create_phone('88005553535', '1234', 3600)
    courier_id = cargo_environment.create_courier(
        'courier_id_0', 'courier_name_0', phone_id, 42, 14,
    )
    cargo_environment.create_claim(
        claim_id, cargo_order_status_new, courier_id, [point_id_0, point_id_1],
    )

    await taxi_eats_picker_orders.run_distlock_task(PERIODIC_NAME)

    expected_times_called = (
        1 if (cargo_order_status_new in PERFORMER_FOUND_STATUSES) else 0
    )

    assert cargo_environment.mock_cargo_claims_bulk_info.times_called == 1
    assert (
        cargo_environment.mock_cargo_external_performer.times_called
        == expected_times_called
    )
    assert (
        cargo_environment.mock_cargo_driver_voiceforwarding.times_called
        == expected_times_called
    )
    assert (
        cargo_environment.mock_cargo_performer_position.times_called
        == expected_times_called
    )

    order = get_order(order_id)

    assert order['cargo_order_status'] == cargo_order_status_new
    if cargo_order_status != cargo_order_status_new:
        assert order['cargo_order_status_changed_at'] == now


@pytest.mark.now('2021-06-08 10:00:00+05')
@utils.cargo_info_synchronizer_config()
async def test_sync_cargo_info_cargo_order_status_batch(
        taxi_eats_picker_orders,
        now,
        create_order,
        get_order,
        cargo_environment,
):
    claim_id_0 = 'claim_id_0'
    claim_id_1 = 'claim_id_1'
    order_id_0 = create_order(
        eats_id='order_0', claim_id=claim_id_0, cargo_order_status='new',
    )
    order_id_1 = create_order(
        eats_id='order_1', claim_id=claim_id_1, cargo_order_status='new',
    )

    now = now.replace(tzinfo=pytz.utc)

    point_id_0 = cargo_environment.create_point(
        'source', 'pending', now + datetime.timedelta(minutes=10),
    )
    point_id_1 = cargo_environment.create_point(
        'destination', 'pending', now + datetime.timedelta(minutes=20),
    )
    phone_id = cargo_environment.create_phone('88005553535', '1234', 3600)
    courier_id = cargo_environment.create_courier(
        'courier_id_0', 'courier_name_0', phone_id, 42, 14,
    )
    cargo_environment.create_claim(
        claim_id_0,
        'cancelled_with_items_on_hands',
        courier_id,
        [point_id_0, point_id_1],
    )
    cargo_environment.create_claim(
        claim_id_1, 'new', courier_id, [point_id_0, point_id_1],
    )

    await taxi_eats_picker_orders.run_distlock_task(PERIODIC_NAME)

    assert cargo_environment.mock_cargo_claims_bulk_info.times_called == 1
    assert cargo_environment.mock_cargo_external_performer.times_called == 1
    assert (
        cargo_environment.mock_cargo_driver_voiceforwarding.times_called == 1
    )
    assert cargo_environment.mock_cargo_performer_position.times_called == 1

    order_0 = get_order(order_id_0)
    order_1 = get_order(order_id_1)

    assert order_0['cargo_order_status'] == 'cancelled_with_items_on_hands'
    assert order_0['cargo_order_status_changed_at'] == now

    assert order_1['cargo_order_status'] == 'new'
    assert order_1['cargo_order_status_changed_at'] is None


@pytest.mark.now('2021-06-08T10:00:00+05:00')
@utils.cargo_info_synchronizer_config()
@pytest.mark.parametrize(
    'courier_id, courier_name, courier_phone, phone_changed',
    [
        (
            'courier_id_0',
            'courier_name_0',
            (
                '+7-555-444-33-22',
                datetime.datetime.fromisoformat('2021-06-08T11:00:00+05:00'),
            ),
            False,
        ),
        ('courier_id_0', 'courier_name_0', None, True),
        (
            'courier_id_0',
            'courier_name_0',
            (
                '+7-555-444-33-22',
                datetime.datetime.fromisoformat('2021-06-08T09:00:00+05:00'),
            ),
            True,
        ),
        (None, None, None, True),
        (
            None,
            None,
            (
                '+7-555-444-33-22',
                datetime.datetime.fromisoformat('2021-06-08T09:00:00+05:00'),
            ),
            True,
        ),
    ],
)
async def test_sync_cargo_info_courier_phone(
        taxi_eats_picker_orders,
        now,
        create_order,
        get_order,
        cargo_environment,
        courier_id,
        courier_name,
        courier_phone,
        phone_changed,
):
    claim_id = 'claim_id_0'
    order_id = create_order(
        eats_id='order_0',
        claim_id=claim_id,
        cargo_order_status='new',
        courier_id=courier_id,
        courier_name=courier_name,
        courier_phone=courier_phone,
    )

    now = now.replace(tzinfo=pytz.utc)

    point_id_0 = cargo_environment.create_point(
        'source', 'pending', now + datetime.timedelta(minutes=10),
    )
    point_id_1 = cargo_environment.create_point(
        'destination', 'pending', now + datetime.timedelta(minutes=20),
    )
    phone_id = cargo_environment.create_phone('88005553535', '1234', 3600)
    courier_id = cargo_environment.create_courier(
        'courier_id_0', 'courier_name_0', phone_id, 42, 14,
    )
    cargo_environment.create_claim(
        claim_id, 'pay_waiting', courier_id, [point_id_0, point_id_1],
    )

    await taxi_eats_picker_orders.run_distlock_task(PERIODIC_NAME)

    assert cargo_environment.mock_cargo_claims_bulk_info.times_called == 1
    assert cargo_environment.mock_cargo_external_performer.times_called == 1
    assert (
        cargo_environment.mock_cargo_driver_voiceforwarding.times_called
        == phone_changed
    )
    assert cargo_environment.mock_cargo_performer_position.times_called == 1

    order = get_order(order_id)

    assert order['cargo_order_status'] == 'pay_waiting'
    assert order['courier_id'] == courier_id
    assert order['courier_name'] == 'courier_name_0'
    assert (
        order['courier_phone']
        == ('88005553535,,1234', now + datetime.timedelta(hours=1))
        if phone_changed
        else courier_phone
    )
    assert order['courier_location'] == [42, 14]
    assert order['courier_pickup_expected_at'] is None


@pytest.mark.now('2021-06-08T10:00:00+05:00')
@utils.cargo_info_synchronizer_config()
@pytest.mark.parametrize(
    'cargo_order_status, point_visit_status, is_source, is_destination',
    [
        ('new', 'pending', True, False),
        ('estimating', 'pending', True, False),
        ('accepted', 'pending', True, False),
        ('pickup_arrived', 'pending', True, False),
        ('pickuped', 'pending', False, True),
        ('pay_waiting', 'pending', False, True),
        ('returning', 'pending', False, True),
        ('returned', 'pending', False, True),
        ('new', 'arrived', False, False),
        ('new', 'visited', False, False),
        ('new', 'skipped', False, False),
        ('accepted', 'arrived', False, False),
        ('accepted', 'visited', False, False),
        ('accepted', 'skipped', False, False),
    ],
)
async def test_sync_cargo_info_route_points(
        taxi_eats_picker_orders,
        now,
        create_order,
        get_order,
        cargo_environment,
        cargo_order_status,
        point_visit_status,
        is_source,
        is_destination,
):
    claim_id = 'claim_id_0'
    order_id = create_order(
        eats_id='order_0',
        claim_id=claim_id,
        cargo_order_status='new',
        courier_id=None,
        courier_name=None,
        courier_phone_id=None,
        courier_phone=None,
    )

    now = now.replace(tzinfo=pytz.utc)

    point_id_0 = cargo_environment.create_point(
        'source', point_visit_status, now + datetime.timedelta(minutes=10),
    )
    point_id_1 = cargo_environment.create_point(
        'destination',
        point_visit_status,
        now + datetime.timedelta(minutes=20),
    )
    phone_id = cargo_environment.create_phone('88005553535', '1234', 3600)
    courier_id = cargo_environment.create_courier(
        'courier_id_0', 'courier_name_0', phone_id, 42, 14,
    )
    cargo_environment.create_claim(
        claim_id, cargo_order_status, courier_id, [point_id_0, point_id_1],
    )

    await taxi_eats_picker_orders.run_distlock_task(PERIODIC_NAME)

    expected_times_called = (
        1 if (cargo_order_status in PERFORMER_FOUND_STATUSES) else 0
    )

    assert cargo_environment.mock_cargo_claims_bulk_info.times_called == 1
    assert (
        cargo_environment.mock_cargo_external_performer.times_called
        == expected_times_called
    )
    assert (
        cargo_environment.mock_cargo_driver_voiceforwarding.times_called
        == expected_times_called
    )
    assert (
        cargo_environment.mock_cargo_performer_position.times_called
        == expected_times_called
    )

    order = get_order(order_id)

    if cargo_order_status in PERFORMER_FOUND_STATUSES:
        assert order['courier_id'] == courier_id
        assert order['courier_name'] == 'courier_name_0'
        assert order['courier_phone'] == (
            '88005553535,,1234',
            now + datetime.timedelta(hours=1),
        )
        assert order['courier_location'] == [42, 14]
    else:
        assert order['courier_id'] is None
        assert order['courier_name'] is None
        assert order['courier_phone'] is None
        assert order['courier_location'] is None

    if is_source:
        assert order['courier_pickup_expected_at'] == now + datetime.timedelta(
            minutes=10,
        )
    else:
        assert order['courier_pickup_expected_at'] is None

    if is_destination:
        assert order[
            'courier_delivery_expected_at'
        ] == now + datetime.timedelta(minutes=20)
    else:
        assert order['courier_delivery_expected_at'] is None


@pytest.mark.now('2021-06-08T10:00:00+05:00')
@utils.cargo_info_synchronizer_config(auto_complete_delay=3600)
@pytest.mark.parametrize(
    'cargo_order_status, cargo_order_status_new, seconds_unchanged, '
    'is_auto_complete',
    [
        ('new', 'new', 3601, False),
        ('estimating', 'estimating', 3601, False),
        ('accepted', 'accepted', 3601, False),
        ('pickup_arrived', 'pickup_arrived', 3601, False),
        ('pickuped', 'pickuped', 3601, True),
        ('pay_waiting', 'pay_waiting', 3601, True),
        ('returning', 'returning', 3601, True),
        ('returned', 'returned', 3601, True),
        ('pickuped', 'pickuped', 3599, False),
        ('pay_waiting', 'pay_waiting', 3599, False),
        ('returning', 'returning', 3599, False),
        ('returned', 'returned', 3599, False),
        ('pickuped', 'delivered', 3601, False),
        ('returned', 'cancelled', 3601, False),
        ('pickuped', 'delivered', 3599, False),
        ('returned', 'cancelled', 3599, False),
    ],
)
async def test_sync_cargo_info_auto_complete(
        taxi_eats_picker_orders,
        now,
        create_order,
        get_order,
        cargo_environment,
        cargo_order_status,
        cargo_order_status_new,
        seconds_unchanged,
        is_auto_complete,
):
    now = now.replace(tzinfo=pytz.utc)

    claim_id = 'claim_id_0'
    order_id = create_order(
        eats_id='order_0',
        claim_id=claim_id,
        cargo_order_status=cargo_order_status,
        courier_id=None,
        courier_name=None,
        courier_phone_id=None,
        courier_phone=None,
        cargo_order_status_changed_at=now
        - datetime.timedelta(seconds=seconds_unchanged),
    )

    point_id_0 = cargo_environment.create_point('source', 'visited', now)
    point_id_1 = cargo_environment.create_point('destination', 'pending', now)
    phone_id = cargo_environment.create_phone('88005553535', '1234', 3600)
    courier_id = cargo_environment.create_courier(
        'courier_id_0', 'courier_name_0', phone_id, 42, 14,
    )
    cargo_environment.create_claim(
        claim_id, cargo_order_status_new, courier_id, [point_id_0, point_id_1],
    )

    await taxi_eats_picker_orders.run_distlock_task(PERIODIC_NAME)

    expected_times_called = (
        1 if (cargo_order_status in PERFORMER_FOUND_STATUSES) else 0
    )

    assert cargo_environment.mock_cargo_claims_bulk_info.times_called == 1
    assert (
        cargo_environment.mock_cargo_external_performer.times_called
        == expected_times_called
    )
    assert (
        cargo_environment.mock_cargo_driver_voiceforwarding.times_called
        == expected_times_called
    )
    assert (
        cargo_environment.mock_cargo_performer_position.times_called
        == expected_times_called
    )

    order = get_order(order_id)

    assert order['cargo_order_status'] == (
        'auto_complete' if is_auto_complete else cargo_order_status_new
    )
    if cargo_order_status in PERFORMER_FOUND_STATUSES:
        assert order['courier_id'] == courier_id
        assert order['courier_name'] == 'courier_name_0'
        assert order['courier_phone'] == (
            '88005553535,,1234',
            now + datetime.timedelta(hours=1),
        )
        assert order['courier_location'] == [42, 14]
    else:
        assert order['courier_id'] is None
        assert order['courier_name'] is None
        assert order['courier_phone'] is None
        assert order['courier_location'] is None
    assert order['courier_pickup_expected_at'] is None


@pytest.mark.now('2021-06-08 10:00:00+05')
@utils.cargo_info_synchronizer_config()
@pytest.mark.parametrize(
    'cargo_order_status',
    [
        None,
        'new',
        'estimating',
        'accepted',
        'pickup_arrived',
        'pickuped',
        'pay_waiting',
        'delivered',
        'delivered_finish',
        'failed',
        'cancelled',
        'cancelled_with_payment',
        'cancelled_by_taxi',
        'cancelled_with_items_on_hands',
        'auto_complete',
    ],
)
async def test_sync_cargo_info_terminal_cargo_order_status(
        taxi_eats_picker_orders,
        now,
        create_order,
        get_order,
        cargo_environment,
        cargo_order_status,
):
    claim_id = 'claim_id_0'
    order_id = create_order(
        eats_id='order_0',
        claim_id=claim_id,
        cargo_order_status=cargo_order_status,
    )

    now = now.replace(tzinfo=pytz.utc)

    point_id_0 = cargo_environment.create_point(
        'source', 'pending', now + datetime.timedelta(minutes=10),
    )
    point_id_1 = cargo_environment.create_point(
        'destination', 'pending', now + datetime.timedelta(minutes=20),
    )
    phone_id = cargo_environment.create_phone('88005553535', '1234', 3600)
    courier_id = cargo_environment.create_courier(
        'courier_id_0', 'courier_name_0', phone_id, 42, 14,
    )
    cargo_environment.create_claim(
        claim_id, 'delivered', courier_id, [point_id_0, point_id_1],
    )

    await taxi_eats_picker_orders.run_distlock_task(PERIODIC_NAME)

    do_sync = cargo_order_status not in TERMINAL_CARGO_ORDER_STATUSES

    assert (
        cargo_environment.mock_cargo_claims_bulk_info.times_called == do_sync
    )
    assert (
        cargo_environment.mock_cargo_external_performer.times_called == do_sync
    )
    assert (
        cargo_environment.mock_cargo_driver_voiceforwarding.times_called
        == do_sync
    )
    assert (
        cargo_environment.mock_cargo_performer_position.times_called == do_sync
    )

    order = get_order(order_id)

    assert order['cargo_order_status'] == (
        'delivered' if do_sync else cargo_order_status
    )
