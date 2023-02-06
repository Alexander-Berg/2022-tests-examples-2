import json

import pytest


@pytest.mark.processing_queue_config(
    'taxi_stub.yaml', scope='taxi', queue='stub',
)
async def test_run_test_in_ydb(
        mockserver, processing, stq, testpoint, ydb, pgsql,
):
    @testpoint('added_event_to_ydb')
    def added_event_to_ydb(data):
        pass

    item_id = '1234'
    event_id = await processing.taxi.stub.send_event(
        item_id, payload={'kind': 'create'},
    )
    # no event in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT item_id, event_id, payload '
        'FROM processing.events '
        'WHERE item_id=%(item_id)s',
        {'item_id': item_id},
    )
    rows = list(cursor)
    assert not rows
    # one event in ydb
    db_name = '`events`'
    await added_event_to_ydb.wait_call()
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    rows = cursor[0].rows
    assert len(rows) == 1
    row = cursor[0].rows[0]
    assert row['item_id'].decode('utf-8') == item_id
    assert row['event_id'].decode('utf-8') == event_id
    json_payload = json.loads(row['payload_v2'])
    assert json_payload['kind'] == 'create'


@pytest.mark.processing_queue_config(
    'testsuite_example.yaml', scope='testsuite', queue='example',
)
async def test_run_test_in_pg(
        mockserver, processing, stq, testpoint, ydb, pgsql,
):
    item_id = '5678'
    event_id = await processing.testsuite.example.send_event(
        item_id, payload={'kind': 'create'},
    )
    # one event in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT item_id, event_id, payload '
        'FROM processing.events '
        'WHERE item_id=%(item_id)s',
        {'item_id': item_id},
    )
    rows = list(cursor)
    assert len(rows) == 1
    row = rows[0]
    assert row[0] == item_id
    assert row[1] == event_id
    json_payload = row[2]
    assert json_payload['kind'] == 'create'
    # no event in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    rows = cursor[0].rows
    assert not rows
