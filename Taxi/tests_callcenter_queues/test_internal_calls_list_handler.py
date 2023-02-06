import pytest

# В БД лежит 6 звонков, 3 из которых имеют статус 'completed'


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_response_200(taxi_callcenter_queues):
    response = await taxi_callcenter_queues.post(
        '/v1/calls/list/', json={'limit': 3},
    )
    assert response.status == 200
    response_json = response.json()
    assert len(response_json['calls']) == 3
    assert response_json['next_cursor'] == 3
    assert response_json['calls'][0]['sip_username'] == '1'
    assert response_json['calls'][1]['sip_username'] == '2'
    assert response_json['calls'][2]['sip_username'] == '3'


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_negative_cursor(taxi_callcenter_queues):
    response = await taxi_callcenter_queues.post(
        '/v1/calls/list/', json={'cursor': -4, 'limit': 3},
    )
    assert response.status == 400


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_negative_limit(taxi_callcenter_queues):
    response = await taxi_callcenter_queues.post(
        '/v1/calls/list/', json={'cursor': 4, 'limit': -6},
    )
    assert response.status == 400


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_zero_limit(taxi_callcenter_queues):
    response = await taxi_callcenter_queues.post(
        '/v1/calls/list/', json={'cursor': 2, 'limit': 0},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json['next_cursor'] == 2
    assert not response_json['calls']


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_big_cursor(taxi_callcenter_queues):
    response = await taxi_callcenter_queues.post(
        '/v1/calls/list/', json={'cursor': 999999999999999999, 'limit': 2},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json['next_cursor'] == 999999999999999999
    assert not response_json['calls']


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_big_limit(taxi_callcenter_queues):
    response = await taxi_callcenter_queues.post(
        '/v1/calls/list/', json={'cursor': 1, 'limit': 999999999},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json['next_cursor'] == 6
    assert len(response_json['calls']) == 5


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_big_cursor_and_limit(taxi_callcenter_queues):
    response = await taxi_callcenter_queues.post(
        '/v1/calls/list/',
        json={'cursor': 9223372036854775807, 'limit': 2147483647},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json['next_cursor'] == 9223372036854775807
    assert not response_json['calls']
