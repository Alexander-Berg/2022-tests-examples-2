from test_taxi_exp.helpers import filters

CONSUMER = 'launch'


async def test_consumers_with_service(taxi_exp_client):
    assert not await filters.get_consumers(taxi_exp_client)

    # adding consumer with metadata
    response = await taxi_exp_client.post(
        '/v1/consumers/kwargs/',
        headers={'X-Ya-Service-Ticket': '123'},
        json={
            'consumer': CONSUMER,
            'kwargs': [],
            'metadata': {'supported_features': ['hello_screen']},
        },
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/experiments/filters/consumers/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONSUMER},
    )
    assert response.status == 200, await response.text()
    result = await response.json()
    assert result['consumers'][0] == {
        'merge_tags': [],
        'name': 'launch',
        'supported_features': ['hello_screen'],
    }
