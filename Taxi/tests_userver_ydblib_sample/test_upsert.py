import json


async def test_upsert_row(taxi_userver_ydblib_sample, ydb):
    response = await taxi_userver_ydblib_sample.post(
        'ydblib/upsert-row',
        json={
            'id': 'id-upsert',
            'name': 'name-upsert',
            'service': 'srv',
            'channel': 123,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    cursor = ydb.execute('SELECT * FROM events WHERE id = "id-upsert"')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1

    row = cursor[0].rows[0]
    assert row.pop('created') > 0
    assert row == {
        'id': b'id-upsert',
        'name': 'name-upsert',
        'service': b'srv',
        'channel': 123,
        'state': None,
    }


async def test_upsert_row_with_state(taxi_userver_ydblib_sample, ydb):
    response = await taxi_userver_ydblib_sample.post(
        'ydblib/upsert-row',
        json={
            'id': 'id-upsert-state',
            'name': 'name-upsert-state',
            'service': 'srv',
            'channel': 123,
            'state': {'qwe': 'asd', 'zxc': 123},
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    cursor = ydb.execute('SELECT * FROM events WHERE id = "id-upsert-state"')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1

    row = cursor[0].rows[0]
    assert row.pop('created') > 0
    assert json.loads(row.pop('state')) == {'qwe': 'asd', 'zxc': 123}
    assert row == {
        'id': b'id-upsert-state',
        'name': 'name-upsert-state',
        'service': b'srv',
        'channel': 123,
    }
