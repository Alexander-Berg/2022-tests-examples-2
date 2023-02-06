async def test_insert_retrieve(taxi_userver_clickhouse_sample):
    await _insert(taxi_userver_clickhouse_sample, 1, 'first')
    data = await _retrieve(taxi_userver_clickhouse_sample)
    assert data == [{'id': 1, 'value': 'first'}]

    await _insert(taxi_userver_clickhouse_sample, 2, 'second')
    data = await _retrieve(taxi_userver_clickhouse_sample)
    assert data == [{'id': 1, 'value': 'first'}, {'id': 2, 'value': 'second'}]


async def _insert(taxi_userver_clickhouse_sample, entity_id, value):
    response = await taxi_userver_clickhouse_sample.post(
        '/api/v1/insert', json={'id': entity_id, 'value': value},
    )
    assert response.status_code == 200


async def _retrieve(taxi_userver_clickhouse_sample):
    response = await taxi_userver_clickhouse_sample.post('/api/v1/retrieve')
    assert response.status_code == 200

    return response.json()['data']
