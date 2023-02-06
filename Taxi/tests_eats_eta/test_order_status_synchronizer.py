import datetime

import pytest

from . import utils


PERIODIC_NAME = 'order-status-synchronizer'
UPDATE_STATUS_OFFSET = 600
AUTOCOMPLETE_OFFSET = 86400


@utils.eats_eta_settings_config3()
async def test_order_status_synchronizer_empty_db(
        taxi_eats_eta, db_select_orders,
):
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == []


@utils.eats_eta_settings_config3(update_status_offset=UPDATE_STATUS_OFFSET)
@pytest.mark.parametrize(
    'core_status', ['awaiting_payment', 'confirmed', 'cooking', 'in_delivery'],
)
async def test_order_status_synchronizer_no_orders_to_update(
        taxi_eats_eta,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        orders_retrieve,
        core_status,
):
    orders = [
        make_order(
            id=0,
            order_nr='order_nr-0',
            status_changed_at=now_utc
            - datetime.timedelta(seconds=UPDATE_STATUS_OFFSET - 1),
            order_status='created',
            eater_passport_uid='yandex_uid',
        ),
        make_order(
            id=1,
            order_nr='order_nr-1',
            status_changed_at=now_utc
            - datetime.timedelta(seconds=UPDATE_STATUS_OFFSET + 1),
            order_status='taken',
            eater_passport_uid='yandex_uid',
        ),
        make_order(
            id=2,
            order_nr='order_nr-2',
            status_changed_at=now_utc
            - datetime.timedelta(seconds=UPDATE_STATUS_OFFSET + 1),
            order_status='auto_complete',
            eater_passport_uid='yandex_uid',
        ),
    ]
    for order in orders:
        db_insert_order(order)
        orders_retrieve.add_order(
            order['order_nr'], order['eater_passport_uid'], core_status,
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == orders
    assert orders_retrieve.mock.times_called == 1


@utils.eats_eta_settings_config3(
    update_status_offset=UPDATE_STATUS_OFFSET,
    db_orders_autocomplete_offset=AUTOCOMPLETE_OFFSET,
)
@pytest.mark.parametrize(
    'order_status, autocomplete',
    [
        ['created', True],
        ['paid', True],
        ['confirmed', True],
        ['taken', True],
        ['cancelled', False],
        ['complete', False],
        ['auto_complete', False],
    ],
)
async def test_order_status_synchronizer_autocomplete(
        taxi_eats_eta,
        now_utc,
        orders_retrieve,
        make_order,
        db_insert_order,
        db_select_orders,
        order_status,
        autocomplete,
):
    orders = [
        make_order(
            id=0,
            order_nr='order_nr-{}'.format(0),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=AUTOCOMPLETE_OFFSET),
            order_status=order_status,
            eater_passport_uid='yandex_uid',
        ),
        make_order(
            id=1,
            order_nr='order_nr-{}'.format(1),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=AUTOCOMPLETE_OFFSET),
            order_status=order_status,
        ),
    ]
    for order in orders:
        db_insert_order(order)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    for order in orders:
        db_order = db_select_orders(order_nr=order['order_nr'])[0]
        if order['eater_passport_uid'] is not None or not autocomplete:
            assert db_order == order
        else:
            assert db_order['order_status'] == 'auto_complete'


@utils.eats_eta_settings_config3(update_status_offset=UPDATE_STATUS_OFFSET)
@pytest.mark.parametrize(
    'core_status, new_order_status',
    [
        ['confirmed', 'created'],
        ['cooking', 'confirmed'],
        ['in_delivery', 'taken'],
        ['arrived_to_customer', 'taken'],
        ['delivered', 'complete'],
        ['cancelled', 'cancelled'],
    ],
)
async def test_order_status_synchronizer_status_updated(
        taxi_eats_eta,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        orders_retrieve,
        core_status,
        new_order_status,
):
    order = make_order(
        id=0,
        order_nr='order_nr-{}'.format(0),
        status_changed_at=now_utc
        - datetime.timedelta(seconds=UPDATE_STATUS_OFFSET + 1),
        order_status='created',
        eater_passport_uid='yandex_uid',
    )
    db_insert_order(order)
    orders_retrieve.add_order(
        order['order_nr'], order['eater_passport_uid'], core_status,
    )
    order['order_status'] = new_order_status
    if new_order_status != 'created':
        order['status_changed_at'] = now_utc
    if new_order_status == 'taken':
        order['delivery_started_at'] = now_utc

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == [order]
    assert orders_retrieve.mock.times_called == 1


@utils.eats_eta_settings_config3(update_status_offset=UPDATE_STATUS_OFFSET)
@pytest.mark.parametrize('order_yandex_uid', [None, 'unknown'])
async def test_order_status_synchronizer_orders_not_found(
        taxi_eats_eta,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        orders_retrieve,
        order_yandex_uid,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=UPDATE_STATUS_OFFSET + i),
            order_status='created',
            eater_passport_uid=order_yandex_uid,
        )
        for i in range(3)
    ]
    for order in orders:
        db_insert_order(order)
        orders_retrieve.add_order(order['order_nr'], 'yandex_uid', 'delivered')

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == orders
    assert orders_retrieve.mock.times_called == 3 * int(
        order_yandex_uid is not None,
    )


@utils.eats_eta_settings_config3(update_status_offset=UPDATE_STATUS_OFFSET)
async def test_order_status_synchronizer_core_error(
        taxi_eats_eta,
        now_utc,
        mockserver,
        make_order,
        db_insert_order,
        db_select_orders,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=UPDATE_STATUS_OFFSET + i),
            order_status='created',
            eater_passport_uid='yandex_uid',
        )
        for i in range(3)
    ]
    for order in orders:
        db_insert_order(order)

    @mockserver.json_handler('/eats-core-orders-retrieve/orders/retrieve')
    def _eats_core_orders_retrieve(request):
        return mockserver.make_response(status=500)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == orders
    assert _eats_core_orders_retrieve.times_called == 3
