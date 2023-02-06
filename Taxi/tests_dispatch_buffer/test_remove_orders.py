import json

import pytest


def get_removed_orders_count(psql):
    cursor = psql.cursor()
    cursor.execute(
        'SELECT dispatch_status FROM dispatch_buffer.dispatch_meta;',
    )
    return len(list(1 for r in cursor if r[0] == 'removed'))


@pytest.mark.config(
    DISPATCH_BUFFER_LOGBROKER_SETTINGS={
        'remove_orders_consumer': {
            'enabled': True,
            'chunk_size': 2,
            'queue_timeout_ms': 100,
            'config_poll_period_ms': 1000,
        },
    },
)
@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
async def test_message(taxi_dispatch_buffer, pgsql, testpoint):
    @testpoint('dispatch-buffer-remove-orders::ProcessAndLog')
    def processed(data):
        pass

    psql = pgsql['driver_dispatcher']
    assert get_removed_orders_count(psql) == 0

    # Эмуляция записи сообщения в логброкер
    orders = [{'order_id': 'order_id_1'}, {'order_id': 'order_id_2'}]
    for order_info in orders:
        response = await taxi_dispatch_buffer.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'dispatch-buffer-remove-orders',
                    'data': json.dumps(order_info),
                    'topic': 'dispatch-buffer-remove-orders',
                    'cookie': 'cookie1',  # строка, которая будет
                },
            ),
        )
        assert response.status_code == 200

    await processed.wait_call()

    assert get_removed_orders_count(psql) == 2
