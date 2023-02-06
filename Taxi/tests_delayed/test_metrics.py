import datetime

import pytest

from tests_delayed import mock_utils


@pytest.mark.pgsql(
    'delayed_orders', files=['metrics_delayed_orders_count.sql'],
)
async def test_delayed_orders_metric(
        taxi_delayed, taxi_delayed_monitor, mocked_time,
):
    mocked_time.set(datetime.datetime(2019, 2, 3, 3, 0, 0))
    await mock_utils.successful_update_metrics_run(taxi_delayed)

    mocked_time.set(datetime.datetime(2019, 2, 3, 3, 0, 6))
    await taxi_delayed.tests_control(invalidate_caches=False)

    metrics_prefix = 'delayed_business_metrics'
    metrics = (await taxi_delayed_monitor.get_metrics(metrics_prefix))[
        metrics_prefix
    ]

    assert metrics['delayed_orders_count']['moscow']['econom'] == 7
    assert metrics['now_to_due_in_db_min']['moscow']['econom']['p0'] == 60
    assert metrics['now_to_due_in_db_min']['moscow']['econom']['p60'] == 61


@pytest.mark.pgsql(
    'delayed_orders', files=['metrics_delayed_processing_status.sql'],
)
@pytest.mark.config(
    DELAYED_ENABLED=True,
    DELAYED_DISPATCHED_ORDERS_STAY_SEC=1,
    DELAYED_ORDERS_CONFIGURATION={
        '__default__': [
            {
                'time_until_due_min': 30,
                'needed_drivers_count': 20,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 20,
                'needed_drivers_count': 10,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 5,
                'needed_drivers_count': 0,
                'maximum_route_time_min': 0,
            },
        ],
    },
)
async def test_delayed_proc_status_metric(
        taxi_delayed, taxi_delayed_monitor, driver_eta, archive, mocked_time,
):
    arrive_time = datetime.datetime(2019, 2, 3, 4, 0, 0)
    created = datetime.datetime(2019, 2, 2)

    def build_order(order_id, status=None):
        default_status = archive.STATIC_ORDER_PROC['order']['status']

        return {
            '_id': order_id,
            'order': {
                '_id': order_id,
                'status': status if status else default_status,
                'created': created,
                'request': {'due': arrive_time},
            },
        }

    # Setting up mocks
    archive.set_order_procs(
        [
            build_order('dispatched_delayed_order_id_1'),
            build_order('dispatched_delayed_order_id_2'),
            build_order('success_delayed_order_id_1'),
            build_order('removed_delayed_order_id_1', status='cancelled'),
        ],
    )

    driver_eta.set_drivers_for_order(
        {
            'dispatched_delayed_order_id_1': mock_utils.build_eta_drivers(
                5, 10,
            ),
            'dispatched_delayed_order_id_2': mock_utils.build_eta_drivers(
                0, 0,
            ),  # does not matter
            'removed_delayed_order_id_1': mock_utils.build_eta_drivers(
                0, 0,
            ),  # does not matter
            'success_delayed_order_id_1': mock_utils.build_eta_drivers(20, 10),
        },
    )

    mocked_time.set(datetime.datetime(2019, 2, 3, 3, 40, 0))
    await taxi_delayed.tests_control()

    await mock_utils.successful_processing_run(taxi_delayed)
    mocked_time.set(datetime.datetime(2019, 2, 3, 3, 40, 30))
    await mock_utils.successful_update_metrics_run(taxi_delayed)

    metrics_prefix = 'delayed_business_metrics'
    metric_name = 'delayed_processing_status'

    for _ in range(2):
        metrics = (await taxi_delayed_monitor.get_metrics(metrics_prefix))[
            metrics_prefix
        ]

        for status, check_value in [
                ('removed', 1),
                ('dispatched', 2),
                ('failed', 1),
                ('succeed', 1),
                ('ignored', 0),
        ]:
            assert metrics[metric_name][status] == check_value

        assert metrics['proceed_orders_task_time'] is not None
        assert metrics['now_to_due_on_dispatch_min']['']['']['p0'] == 20
        assert metrics['time_until_due_min']['']['']['p0'] == 20

    mocked_time.set(datetime.datetime(2019, 2, 3, 3, 42, 0))
    await mock_utils.successful_update_metrics_run(taxi_delayed)

    metrics = (await taxi_delayed_monitor.get_metrics(metrics_prefix))[
        metrics_prefix
    ]

    for status, check_value in [
            ('removed', 0),
            ('dispatched', 0),
            ('failed', 0),
            ('succeed', 0),
            ('ignored', 0),
    ]:
        assert metrics[metric_name][status] == check_value
