import datetime

import pytest

from . import utils


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_picker_orders_complete_outdated_orders',
    consumers=['eats-picker-orders/complete-outdated-orders'],
    clauses=[],
    default_value={'completion_timeout': 1},
)
@pytest.mark.now('2021-02-01T12:00:00+0000')
@utils.send_order_events_config()
async def test_complete_outdated_paid_orders(
        mocked_time,
        get_cursor,
        testpoint,
        create_order,
        mockserver,
        taxi_eats_picker_orders,
        mock_processing,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json['status'] == 'complete'
        assert request.json['reason'] == 'periodic-auto-complete'
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    create_order(
        eats_id='picking_packing_1',
        picker_id='1',
        state='picking',
        flow_type='picking_packing',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )
    create_order(
        eats_id='picking_packing_2',
        picker_id='2',
        state='paid',
        flow_type='picking_packing',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )
    create_order(
        eats_id='picking_packing_3',
        picker_id='3',
        state='packing',
        flow_type='picking_packing',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )
    create_order(
        eats_id='picking_handing_1',
        picker_id='4',
        state='complete',
        flow_type='picking_handing',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )
    create_order(
        eats_id='picking_handing_2',
        picker_id='5',
        state='paid',
        flow_type='picking_handing',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )
    create_order(
        eats_id='picking_handing_3',
        picker_id='6',
        state='picked_up',
        flow_type='picking_handing',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )
    create_order(
        eats_id='picking_only_1',
        picker_id='7',
        state='assigned',
        flow_type='picking_only',
        created_at=mocked_time.now(),
    )
    create_order(
        eats_id='picking_only_2',
        picker_id='8',
        state='paid',
        flow_type='picking_only',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )
    create_order(
        eats_id='picking_only_3',
        picker_id='9',
        state='picking',
        flow_type='picking_only',
        created_at=mocked_time.now() - datetime.timedelta(seconds=2),
    )

    @testpoint('eats_picker_orders::complete-outdated-paid-orders')
    def handle_finished(arg):
        pass

    await taxi_eats_picker_orders.run_distlock_task(
        'complete-outdated-paid-orders',
    )
    handle_finished.next_call()

    pg_cursor = get_cursor()
    pg_cursor.execute(
        """
        select * from eats_picker_orders.orders
        where eats_id in (
        'picking_packing_2',
        'picking_packing_3',
        'picking_handing_2',
        'picking_only_2')
         and state = 'complete'
    """,
    )
    rows = pg_cursor.fetchall()
    assert len(rows) == 4
    assert _mock_eats_core_picker_orders.times_called == 4

    assert mock_processing.times_called == 4
