import pytest

from . import models


def set_update(pgsql, order_id, create_delta, update_delta):
    query = """
            BEGIN;
            SET session_replication_role = replica;
            UPDATE orders.orders SET
                created = NOW() - INTERVAL %s,
                updated = NOW() - INTERVAL %s
            WHERE order_id = %s;
            SET session_replication_role = DEFAULT;
            COMMIT;
            """
    pg_db = pgsql['grocery_orders']
    cursor = pg_db.cursor()
    cursor.execute(query, [create_delta, update_delta, order_id])


def make_order(pgsql, create_delta, update_delta, status, reason=None):
    order = models.Order(pgsql=pgsql, status=status, cancel_reason_type=reason)
    set_update(pgsql, order.order_id, create_delta, update_delta)
    return order


@pytest.mark.suspend_periodic_tasks('orders-metrics-checker')
async def test_closed_orders_metrics(
        taxi_grocery_orders, pgsql, taxi_grocery_orders_monitor,
):
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['orders_timing_average'] == 0
    assert metrics['close_per_period'] == 0
    assert metrics['order_timings'] == {
        '$meta': {'solomon_children_labels': 'percentile'},
        'p0': 0,
        'p100': 0,
        'p50': 0,
        'p90': 0,
        'p95': 0,
        'p98': 0,
        'p99': 0,
        'p99_6': 0,
        'p99_9': 0,
    }

    make_order(pgsql, '3 minutes', '10 seconds', 'closed')
    make_order(pgsql, '2 minutes', '10 seconds', 'closed')
    make_order(pgsql, '2 minutes', '70 seconds', 'closed')
    make_order(pgsql, '2 minutes', '10 seconds', 'assembled')
    make_order(pgsql, '2 minutes', '10 seconds', 'delivering')
    make_order(pgsql, '2 minutes', '10 seconds', 'canceled')
    make_order(pgsql, '2 minutes', '10 seconds', 'pending_cancel')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['orders_timing_average'] == 140
    assert metrics['close_per_period'] == 2
    assert metrics['order_timings'] == {
        '$meta': {'solomon_children_labels': 'percentile'},
        'p0': 110,
        'p100': 170,
        'p50': 170,
        'p90': 170,
        'p95': 170,
        'p98': 170,
        'p99': 170,
        'p99_6': 170,
        'p99_9': 170,
    }

    make_order(pgsql, '2 minutes', '40 seconds', 'closed')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['orders_timing_average'] == 120
    assert metrics['close_per_period'] == 3
    assert metrics['order_timings'] == {
        '$meta': {'solomon_children_labels': 'percentile'},
        'p0': 80,
        'p100': 170,
        'p50': 110,
        'p90': 170,
        'p95': 170,
        'p98': 170,
        'p99': 170,
        'p99_6': 170,
        'p99_9': 170,
    }


@pytest.mark.suspend_periodic_tasks('orders-metrics-checker')
async def test_canceled_orders_metrics(
        taxi_grocery_orders, pgsql, taxi_grocery_orders_monitor,
):
    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 0
    assert metrics['cancel_by_reason'] == {
        'timeout': 0,
        'failure': 0,
        'user_request': 0,
        'payment_failed': 0,
        'admin_request': 0,
    }
    assert metrics['cancel_no_reason'] == 0

    make_order(pgsql, '2 minutes', '0 seconds', 'canceled')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 1
    assert metrics['cancel_by_reason'] == {
        'timeout': 0,
        'failure': 0,
        'user_request': 0,
        'payment_failed': 0,
        'admin_request': 0,
    }
    assert metrics['cancel_no_reason'] == 1

    make_order(pgsql, '2 minutes', '10 seconds', 'canceled', 'timeout')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 2
    assert metrics['cancel_by_reason'] == {
        'timeout': 1,
        'failure': 0,
        'user_request': 0,
        'payment_failed': 0,
        'admin_request': 0,
    }
    assert metrics['cancel_no_reason'] == 1

    make_order(pgsql, '3 minutes', '20 seconds', 'canceled', 'failure')
    make_order(pgsql, '3 minutes', '20 seconds', 'canceled', 'failure')
    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 4
    assert metrics['cancel_by_reason'] == {
        'timeout': 1,
        'failure': 2,
        'user_request': 0,
        'payment_failed': 0,
        'admin_request': 0,
    }
    assert metrics['cancel_no_reason'] == 1

    make_order(pgsql, '2 minutes', '30 seconds', 'canceled', 'user_request')
    make_order(pgsql, '2 minutes', '30 seconds', 'canceled', 'user_request')
    make_order(pgsql, '2 minutes', '30 seconds', 'canceled', 'user_request')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 7
    assert metrics['cancel_by_reason'] == {
        'timeout': 1,
        'failure': 2,
        'user_request': 3,
        'payment_failed': 0,
        'admin_request': 0,
    }
    assert metrics['cancel_no_reason'] == 1

    make_order(pgsql, '2 minutes', '40 seconds', 'canceled', 'payment_failed')
    make_order(pgsql, '2 minutes', '40 seconds', 'canceled', 'payment_failed')
    make_order(pgsql, '2 minutes', '40 seconds', 'canceled', 'payment_failed')
    make_order(pgsql, '2 minutes', '40 seconds', 'canceled', 'payment_failed')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 11
    assert metrics['cancel_by_reason'] == {
        'timeout': 1,
        'failure': 2,
        'user_request': 3,
        'payment_failed': 4,
        'admin_request': 0,
    }
    assert metrics['cancel_no_reason'] == 1

    make_order(pgsql, '2 minutes', '50 seconds', 'canceled', 'admin_request')
    make_order(pgsql, '2 minutes', '50 seconds', 'canceled', 'admin_request')
    make_order(pgsql, '2 minutes', '50 seconds', 'canceled', 'admin_request')
    make_order(pgsql, '2 minutes', '50 seconds', 'canceled', 'admin_request')
    make_order(pgsql, '2 minutes', '50 seconds', 'canceled', 'admin_request')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 16
    assert metrics['cancel_by_reason'] == {
        'timeout': 1,
        'failure': 2,
        'user_request': 3,
        'payment_failed': 4,
        'admin_request': 5,
    }
    assert metrics['cancel_no_reason'] == 1

    make_order(pgsql, '2 minutes', '70 seconds', 'canceled', 'timeout')
    make_order(pgsql, '3 minutes', '80 seconds', 'canceled', 'failure')
    make_order(pgsql, '2 minutes', '90 seconds', 'canceled', 'user_request')
    make_order(pgsql, '2 minutes', '95 seconds', 'canceled', 'payment_failed')
    make_order(pgsql, '2 minutes', '99 seconds', 'canceled', 'admin_request')

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')
    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')

    assert metrics['cancel_per_period'] == 16
    assert metrics['cancel_by_reason'] == {
        'timeout': 1,
        'failure': 2,
        'user_request': 3,
        'payment_failed': 4,
        'admin_request': 5,
    }
    assert metrics['cancel_no_reason'] == 1
