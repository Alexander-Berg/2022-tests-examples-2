import datetime

import pytest


@pytest.mark.pgsql(
    'eats_orders_tracking',
    queries=[
        """INSERT INTO eats_orders_tracking.orders_eta
        (order_nr, eta)
        VALUES ('order_nr_1', '2019-12-31T23:59:59.000+00:00')""",
    ],
)
async def test_green_flow(stq_runner, pgsql):
    await stq_runner.eats_orders_tracking_orders_eta.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'orders': [
                {
                    'order_nr': 'order_nr_1',
                    'eta': '2020-01-01T00:00:00.000+00:00',
                },
                {
                    'order_nr': 'order_nr_2',
                    'eta': '2020-01-01T00:00:01.000+00:00',
                },
                {
                    'order_nr': 'order_nr_3',
                    'eta': '2020-01-01T00:00:02.000+00:00',
                },
            ],
        },
    )

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""
        select order_nr, eta
        from eats_orders_tracking.orders_eta
        """,
    )
    assert list(cursor) == [
        (
            'order_nr_1',
            datetime.datetime.fromisoformat('2020-01-01T00:00:00.000+00:00'),
        ),  # updated
        (
            'order_nr_2',
            datetime.datetime.fromisoformat('2020-01-01T00:00:01.000+00:00'),
        ),  # inserted
        (
            'order_nr_3',
            datetime.datetime.fromisoformat('2020-01-01T00:00:02.000+00:00'),
        ),  # inserted
    ]


def make_config_stq_retry(
        max_exec_tries, max_reschedule_counter, reschedule_seconds,
):
    return {
        'stq_orders': {
            'max_exec_tries': 100,
            'max_reschedule_counter': 100,
            'reschedule_seconds': 100,
        },
        'stq_couriers': {
            'max_exec_tries': 100,
            'max_reschedule_counter': 100,
            'reschedule_seconds': 100,
        },
        'stq_orders_eta': {
            'max_exec_tries': max_exec_tries,
            'max_reschedule_counter': max_reschedule_counter,
            'reschedule_seconds': reschedule_seconds,
        },
        'stq_picker_orders': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_cargo_waybill_changes': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_order_to_another_eater_sms': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
    }
