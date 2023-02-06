import datetime

import pytest

from . import utils


PERIODIC_NAME = 'eta-periodic-updater'
DB_ORDERS_UPDATE_OFFSET = 5


@utils.eats_eta_settings_config3()
async def test_update_eta_empty_db(taxi_eats_eta, redis_store):
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert not redis_store.keys()


@pytest.mark.parametrize(
    'order_status', ['complete', 'auto_complete', 'cancelled'],
)
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_update_eta_no_orders_to_update(
        taxi_eats_eta,
        now_utc,
        make_order,
        db_insert_order,
        redis_store,
        order_status,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET + 1),
            delivery_type='native',
            order_status=order_status,
        )
        for i in range(3)
    ]
    for order in orders:
        db_insert_order(order)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert not redis_store.keys()


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@pytest.mark.config(
    EATS_ETA_PERIODICS_SETTINGS={
        '__default__': {'tasks_count': 3, 'interval': 1, 'enabled': False},
    },
)
async def test_update_eta_disabled(
        taxi_eats_eta, now_utc, make_order, db_insert_order, redis_store,
):
    order = make_order(status_changed_at=now_utc, order_status='created')
    db_insert_order(order)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert not redis_store.keys()


@pytest.mark.redis_testcase(True)
async def test_update_eta(
        eta_testcase, taxi_eats_eta, check_redis_value, db_select_orders,
):
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)

    for testcase_order in eta_testcase['orders']:
        order = testcase_order['order']
        expected_estimations = testcase_order['expected_estimations']

        for key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], key, order[key])
        for key, data in expected_estimations.items():
            check_redis_value(order['order_nr'], key, data['value'])

        if 'order_update' in testcase_order:
            order.update(testcase_order['order_update'])
            assert db_select_orders(order_nr=order['order_nr']) == [order]
