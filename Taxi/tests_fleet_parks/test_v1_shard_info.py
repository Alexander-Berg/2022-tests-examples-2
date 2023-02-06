from tests_fleet_parks import utils

ENDPOINT = 'v1/shard/info'


async def test_not_separate_table(taxi_fleet_parks):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    request = {'park_id': 'park_id'}
    expected_response = {
        'orders': {'table_name': 'orders_1', 'shard_number': 1},
        'payments': {'table_name': 'payments_1', 'shard_number': 1},
        'transactions': {'table_name': 'transactions_1', 'shard_number': 0},
        'payments_agg': {'table_name': 'payments_agg_1', 'shard_number': 0},
        'changes': {'table_name': 'changes_1', 'shard_number': 0},
        'feedbacks': {'table_name': 'feedbacks_1', 'shard_number': 1},
        'passengers': {'table_name': 'passengers_1', 'shard_number': 0},
    }

    response = await taxi_fleet_parks.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == expected_response, response.text


async def test_separate_table(taxi_fleet_parks):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    request = {'park_id': 'park_id1'}
    expected_response = {
        'orders': {'table_name': 'orders_park_id1', 'shard_number': 0},
        'payments': {'table_name': 'payments_park_id1', 'shard_number': 1},
        'transactions': {
            'table_name': 'transactions_park_id1',
            'shard_number': 0,
        },
        'payments_agg': {
            'table_name': 'payments_agg_park_id1',
            'shard_number': 0,
        },
        'changes': {'table_name': 'changes_park_id1', 'shard_number': 0},
        'feedbacks': {'table_name': 'feedbacks_park_id1', 'shard_number': 1},
        'passengers': {'table_name': 'passengers_park_id1', 'shard_number': 0},
    }

    response = await taxi_fleet_parks.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == expected_response, response.text
