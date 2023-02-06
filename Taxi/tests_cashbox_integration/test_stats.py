import pytest


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        """
            ALTER TYPE cashbox_integration.receipt_status_t
            ADD VALUE 'unknown_status';
        """,
        """
        INSERT INTO cashbox_integration.receipts(
            park_id,
            driver_id,
            order_id,
            cashbox_id,
            external_id,
            status,
            created_at,
            updated_at
        ) VALUES (
            'park_id_1',
            'driver_id_1',
            'order_id_1',
            'cashbox_id_1',
            'idempotency_key_1',
            'push_to_cashbox',
            '2019-10-01T10:05:00',
            '2019-10-01T10:05:00'
        ), (
            'park_id_1',
            'driver_id_1',
            'order_id_2',
            'cashbox_id_1',
            'idempotency_key_2',
            'need_order_info',
            '2019-10-01T10:05:00',
            '2019-10-01T10:05:00'
        ), (
            'park_id_1',
            'driver_id_1',
            'order_id_3',
            'cashbox_id_1',
            'idempotency_key_3',
            'wait_status',
            '2019-10-01T10:05:00',
            '2019-10-01T10:05:00'
        ), (
            'park_id_1',
            'driver_id_1',
            'order_id_4',
            'cashbox_id_1',
            'idempotency_key_4',
            'complete',
            '2019-10-01T10:05:00',
            '2019-10-01T10:05:00'
        ), (
            'park_id_1',
            'driver_id_1',
            'order_id_5',
            'cashbox_id_1',
            'idempotency_key_5',
            'complete',
            '2019-10-01T10:05:00',
            '2019-10-01T10:05:00'
        ), (
            'park_id_1',
            'driver_id_1',
            'order_id_7',
            'cashbox_id_1',
            'idempotency_key_7',
            'push_to_cashbox',
            '2019-10-01T10:05:00',
            '2019-10-01T10:05:00'
        ), (
            'park_id_1',
            'driver_id_1',
            'order_id_8',
            'cashbox_id_1',
            'idempotency_key_8',
            'unknown_status',
            '2019-10-01T10:05:00',
            '2019-10-01T10:05:00'
        );
        """,
    ],
)
async def test_metrics(
        taxi_cashbox_integration, taxi_cashbox_integration_monitor,
):
    await taxi_cashbox_integration.run_periodic_task('StatsGather_0')
    metrics = await taxi_cashbox_integration_monitor.get('receipts-statuses')
    assert metrics.json()['receipts-statuses'] == {
        '0': {
            'done': 2,
            'need_order_info': 1,
            'push_to_cashbox': 2,
            'wait_status': 1,
            'fail': 0,
            'invalid': 0,
            'expired': 0,
        },
    }
