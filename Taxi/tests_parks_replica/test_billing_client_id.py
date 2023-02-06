import pytest


async def test_billing_client_id_404(taxi_parks_replica):
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id/retrieve',
        params={'consumer': 'test', 'park_id': 'unknown_park_id'},
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'park_id not found'}


@pytest.mark.parametrize(
    'park_id, timestamp, value',
    [
        ('park_id_1', '1970-01-15T06:55:07.001Z', 'billing_id2'),
        ('park_id_1', '1970-01-15T06:55:07.001+00:00', 'billing_id2'),
        ('park_id_1', '1970-01-15T06:56:07.000Z', 'billing_id3'),
        ('park_id_1', '1970-01-15T06:54:06.000Z', None),
        ('park_id_2', '1970-01-15T06:56:07.000Z', 'billing_id4'),
        ('park_id_3', '1970-01-15T06:56:07.000Z', None),
    ],
)
async def test_billing_client_id(
        taxi_parks_replica, park_id, timestamp, value,
):
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id/retrieve',
        params={
            'consumer': 'test',
            'park_id': park_id,
            'timestamp': timestamp,
        },
    )
    if value is None:
        expected_json = {}
    else:
        expected_json = {'billing_client_id': value}
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.now('1970-01-15T06:55:07.001Z')
async def test_billing_client_id_no_ts(taxi_parks_replica):
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id/retrieve',
        params={'consumer': 'test', 'park_id': 'park_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {'billing_client_id': 'billing_id2'}


async def test_billing_client_id_history_404(taxi_parks_replica):
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id_history/retrieve',
        params={'consumer': 'test', 'park_id': 'unknown_park_id'},
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'park_id not found'}


async def test_billing_client_id_history_no_date(taxi_parks_replica):
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id_history/retrieve',
        params={'consumer': 'test', 'park_id': 'park_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'billing_client_ids': [
            {
                'billing_client_id': 'billing_id1',
                'start': '1970-01-15T06:54:07+00:00',
                'end': '1970-01-15T06:55:07+00:00',
            },
            {
                'billing_client_id': 'billing_id2',
                'start': '1970-01-15T06:55:07+00:00',
                'end': '1970-01-15T06:56:07+00:00',
            },
            {
                'billing_client_id': 'billing_id3',
                'start': '1970-01-15T06:56:07+00:00',
            },
        ],
    }


async def test_billing_client_id_history(taxi_parks_replica):
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id_history/retrieve',
        params={
            'consumer': 'test',
            'park_id': 'park_id_1',
            'from': '1970-01-15T06:54:07.500Z',
            'to': '1970-01-15T06:55:07+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'billing_client_ids': [
            {
                'billing_client_id': 'billing_id1',
                'start': '1970-01-15T06:54:07+00:00',
                'end': '1970-01-15T06:55:07+00:00',
            },
            {
                'billing_client_id': 'billing_id2',
                'start': '1970-01-15T06:55:07+00:00',
                'end': '1970-01-15T06:56:07+00:00',
            },
        ],
    }
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id_history/retrieve',
        params={
            'consumer': 'test',
            'park_id': 'park_id_1',
            'from': '1970-01-15T06:58:07+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'billing_client_ids': [
            {
                'billing_client_id': 'billing_id3',
                'start': '1970-01-15T06:56:07+00:00',
            },
        ],
    }


async def test_billing_client_id_history_no_versions(taxi_parks_replica):
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id_history/retrieve',
        params={
            'consumer': 'test',
            'park_id': 'park_id_2',
            'from': '1970-01-15T06:54:07.500Z',
            'to': '1970-01-15T06:55:07+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'billing_client_ids': [{'billing_client_id': 'billing_id4'}],
    }
    response = await taxi_parks_replica.get(
        'v1/parks/billing_client_id_history/retrieve',
        params={
            'consumer': 'test',
            'park_id': 'park_id_3',
            'from': '1970-01-15T06:54:07.500Z',
            'to': '1970-01-15T06:55:07+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'billing_client_ids': []}
