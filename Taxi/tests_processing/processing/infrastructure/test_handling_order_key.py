import pytest


@pytest.mark.processing_queue_config(
    'simple_example.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
async def test_handling_order_key(taxi_processing, pgsql, ydb, use_ydb):
    item_id = '123456789'
    for i in range(3):
        resp = await taxi_processing.post(
            '/v1/testsuite/example/create-event',
            params={'item_id': item_id},
            headers={'X-Idempotency-Token': f'event_{i}'},
            json={},
        )
        event_id = resp.json()['event_id']
        # trigger handling order key calculation
        await taxi_processing.get(
            '/v1/testsuite/example/events',
            params={'item_id': item_id, 'show_unapproached': True},
        )
        if use_ydb:
            db_name = '`events`'
            cursor = ydb.execute(
                'SELECT item_id, event_id, order_key, handling_order_key '
                'FROM {} WHERE event_id="{}"'.format(db_name, event_id),
            )
            assert len(cursor) == 1
            row = cursor[0].rows[0]
            assert row['item_id'].decode('utf-8') == item_id
            assert row['event_id'].decode('utf-8') == event_id
            assert row['order_key'] == i
            assert row['handling_order_key'] == i
        else:
            cursor = pgsql['processing_db'].cursor()
            cursor.execute(
                'SELECT item_id, event_id, order_key, handling_order_key '
                'FROM processing.events '
                'WHERE event_id=%(event_id)s',
                {'event_id': event_id},
            )
            assert list(cursor) == [(item_id, event_id, i, i)]
