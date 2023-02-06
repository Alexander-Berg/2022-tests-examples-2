import datetime

import pytest
import pytz

from . import utils


@pytest.mark.now('2021-09-23T14:01:00+00:00')
@pytest.mark.config(
    EATS_PICKER_ORDERS_NOT_PAID_COMPLETION={
        'period_seconds': 10,
        'select_batch_size': 10,
        'insert_batch_size': 1,
        'core_apply_status_delay_ms': 1,
    },
)
@pytest.mark.parametrize(
    'time_zone, should_be_completed',
    [('Europe/Moscow', False), ('Asia/Vladivostok', True)],
)
@utils.send_order_events_config()
async def test_complete_outdated_not_paid_orders(
        mocked_time,
        create_order,
        create_order_status,
        mockserver,
        taxi_eats_picker_orders,
        time_zone,
        should_be_completed,
        get_cursor,
        mock_processing,
):
    now = mocked_time.now().replace(tzinfo=pytz.utc)
    place_id = 101
    eats_id = 'eats_id_1'
    payment_limit = 1000
    current_limit = 100

    order_id = create_order(
        eats_id=eats_id,
        place_id=place_id,
        picker_id='3',
        state='picking',
        created_at=now - datetime.timedelta(hours=10),
        payment_limit=payment_limit,
    )
    create_order_status(
        order_id=order_id,
        state='picking',
        created_at=now - datetime.timedelta(hours=10),
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(_):
        return mockserver.make_response(
            json={'order_id': eats_id, 'amount': current_limit}, status=200,
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage(request):
        assert request.method == 'POST'
        return {
            'places': [
                {
                    'id': place_id,
                    'revision_id': 20,
                    'updated_at': '2021-08-01T00:00:0Z',
                    'region': {
                        'id': 1,
                        'geobase_ids': [],
                        'name': 'name',
                        'time_zone': time_zone,
                    },
                },
            ],
            'not_found_place_ids': [],
        }

    @mockserver.json_handler(
        '/eats-retail-order-history/api/v1/customer/order/status',
    )
    def _mock_retail_order_history(request):
        assert request.method == 'POST'
        assert request.json['order_nrs']
        return {
            'orders_statuses': [
                {
                    'order_nr': request.json['order_nrs'][0],
                    'status': 'in_delivery',
                },
            ],
        }

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_apply_state(request):
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    await taxi_eats_picker_orders.run_distlock_task(
        'complete-outdated-not-paid-orders',
    )

    pg_cursor = get_cursor()
    pg_cursor.execute(
        f"""
        select * from eats_picker_orders.orders
        where eats_id = '{eats_id}'
    """,
    )
    orders = pg_cursor.fetchall()
    pg_cursor.execute(
        f"""
        select * from eats_picker_orders.order_statuses
        where order_id = {order_id}
        order by created_at DESC
        LIMIT 1
    """,
    )
    statuses = pg_cursor.fetchall()

    assert len(orders) == 1
    assert len(statuses) == 1

    assert _mock_eats_catalog_storage.times_called == 1

    if should_be_completed:
        assert orders[0]['state'] == 'complete'
        assert statuses[0]['state'] == 'complete'
        assert orders[0]['spent'] == payment_limit - current_limit
        assert _mock_apply_state.times_called == 1
        assert _mock_retail_order_history.times_called == 1
        assert mock_processing.times_called == 1
    else:
        assert orders[0]['state'] == 'picking'
        assert statuses[0]['state'] == 'picking'
        assert not orders[0]['spent']
        assert _mock_apply_state.times_called == 0
        assert _mock_retail_order_history.times_called == 0
        assert mock_processing.times_called == 0


@pytest.mark.now('2021-09-23T14:01:00+00:00')
@pytest.mark.config(
    EATS_PICKER_ORDERS_NOT_PAID_COMPLETION={
        'period_seconds': 10,
        'select_batch_size': 10,
        'insert_batch_size': 1,
        'core_apply_status_delay_ms': 1,
        'close_after_seconds': 3600,
    },
)
@pytest.mark.parametrize(
    'time_delta, should_be_completed',
    [
        (datetime.timedelta(seconds=3599), False),
        (datetime.timedelta(seconds=3601), True),
    ],
)
@utils.send_order_events_config()
async def test_complete_outdated_not_paid_orders_after_seconds(
        mocked_time,
        create_order,
        create_order_status,
        mockserver,
        taxi_eats_picker_orders,
        time_delta,
        should_be_completed,
        get_cursor,
        mock_processing,
):
    now = mocked_time.now().replace(tzinfo=pytz.utc)
    place_id = 101
    eats_id = 'eats_id_1'
    payment_limit = 1000
    current_limit = 100

    order_id = create_order(
        eats_id=eats_id,
        place_id=place_id,
        picker_id='3',
        state='picking',
        created_at=now - time_delta,
        payment_limit=payment_limit,
    )
    create_order_status(
        order_id=order_id, state='picking', created_at=now - time_delta,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(_):
        return mockserver.make_response(
            json={'order_id': eats_id, 'amount': current_limit}, status=200,
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage(request):
        pass

    @mockserver.json_handler(
        '/eats-retail-order-history/api/v1/customer/order/status',
    )
    def _mock_retail_order_history(request):
        assert request.method == 'POST'
        assert request.json['order_nrs']
        return {
            'orders_statuses': [
                {
                    'order_nr': request.json['order_nrs'][0],
                    'status': 'in_delivery',
                },
            ],
        }

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_apply_state(request):
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    await taxi_eats_picker_orders.run_distlock_task(
        'complete-outdated-not-paid-orders',
    )

    pg_cursor = get_cursor()
    pg_cursor.execute(
        f"""
        select * from eats_picker_orders.orders
        where eats_id = '{eats_id}'
    """,
    )
    orders = pg_cursor.fetchall()
    pg_cursor.execute(
        f"""
        select * from eats_picker_orders.order_statuses
        where order_id = {order_id}
        order by created_at DESC
        LIMIT 1
    """,
    )
    statuses = pg_cursor.fetchall()

    assert len(orders) == 1
    assert len(statuses) == 1

    assert _mock_eats_catalog_storage.times_called == 0

    if should_be_completed:
        assert orders[0]['state'] == 'complete'
        assert statuses[0]['state'] == 'complete'
        assert orders[0]['spent'] == payment_limit - current_limit
        assert _mock_apply_state.times_called == 1
        assert _mock_retail_order_history.times_called == 1
        assert mock_processing.times_called == 1
    else:
        assert orders[0]['state'] == 'picking'
        assert statuses[0]['state'] == 'picking'
        assert _mock_apply_state.times_called == 0
        assert _mock_retail_order_history.times_called == 0
        assert mock_processing.times_called == 0
