import pytest

from tests_grocery_uber_gw import consts
from tests_grocery_uber_gw import events
from tests_grocery_uber_gw import sql_queries


def _should_change_status(status, current_uber_status):

    return status not in consts.STATUS_MAPPING['skip_processing'] and (
        not current_uber_status
        or status not in consts.STATUS_MAPPING[current_uber_status]
    )


@pytest.mark.parametrize(
    'current_uber_status', [None, 'started', 'arriving', 'delivered'],
)
@pytest.mark.parametrize(
    'order_status',
    [
        'draft',
        'checked_out',
        'reserving',
        'reserved',
        'assembling',
        'assembled',
        'delivering',
        'closed',
        'canceled',
        'pending_cancel',
    ],
)
async def test_basic(
        taxi_grocery_uber_gw,
        grocery_uber_gw_db,
        testpoint,
        mock_uber_api,
        push_event,
        order_status,
        current_uber_status,
):
    """ Checking that the cache is being built correctly """

    uber_order_id = 'dd3ccd3e-8a25-4b8d-af08-1b8d06b38bda'
    grocery_order_id = 'fb36e8ac-7161-48a5-86bb-625192b0cdff-grocery'
    event = events.OrderStateChangedEvent(
        order_id=grocery_order_id, order_status=order_status,
    )

    grocery_uber_gw_db.apply_sql_query(
        sql_queries.insert_order(
            uber_order_id,
            grocery_order_id,
            delivery_status=current_uber_status,
        ),
    )

    await taxi_grocery_uber_gw.invalidate_caches()

    records = grocery_uber_gw_db.fetch_from_sql(
        'select * from grocery_uber_gw.orders_correspondence',
    )
    print(records)

    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    await push_event(event, event.consumer)

    await taxi_grocery_uber_gw.run_task(f'{event.consumer}-consumer-task')

    await event_commit.wait_call()

    if order_status in ['canceled', 'pending_cancel']:
        assert mock_uber_api.cancel_order_times_called == 1
    else:
        assert mock_uber_api.upd_delivery_stat_times_called == (
            1
            if _should_change_status(order_status, current_uber_status)
            else 0
        )

    # WRITE YOUR TEST CODE HERE AFTER ADD HANDLE-LOGIC
