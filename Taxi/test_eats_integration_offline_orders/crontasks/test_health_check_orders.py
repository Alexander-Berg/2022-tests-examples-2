import datetime

import pytest

from eats_integration_offline_orders.generated.cron import run_cron


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'orders.sql',
        'restaurants_options.sql',
        'payment_transactions.sql',
    ],
)
@pytest.mark.now('2022-05-04T12:30:00.0+03:00')
async def test_health_check_orders(
        cron_context, load_json, stq, place_id, restaurant_slug,
):

    await run_cron.main(
        [
            'eats_integration_offline_orders.crontasks.health_check_orders',
            '-t',
            '0',
        ],
    )
    check_task_queued(
        stq.ei_offline_orders_health_check,
        {
            'pos_type': 'rkeeper',
            'place_id': 'place_id__1',
            'table_pos_id': 'table_id__1',
        },
        eta=datetime.datetime(2022, 5, 4, 9, 30),
    )
    check_task_queued(
        stq.ei_offline_orders_health_check,
        {
            'pos_type': 'rkeeper',
            'place_id': 'place_id__1',
            'table_pos_id': 'table_id__2',
        },
        eta=datetime.datetime(2022, 5, 4, 9, 45),
    )
    check_task_queued(
        stq.ei_offline_orders_health_check,
        {
            'pos_type': 'rkeeper',
            'place_id': 'place_id__2',
            'table_pos_id': 'table_id__3',
        },
        eta=datetime.datetime(2022, 5, 4, 9, 30),
    )


def check_task_queued(queue, kwargs, eta, drop=()):
    task = queue.next_call()
    assert task.pop('id')
    assert task.pop('queue')
    for arg in drop:
        assert task['kwargs'].pop(arg)
    assert task == {'args': [], 'kwargs': kwargs, 'eta': eta}
