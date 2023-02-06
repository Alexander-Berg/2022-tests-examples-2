from test_taxi_exp.helpers import filters


async def test_consumers_with_service(taxi_exp_client):
    assert not await filters.get_consumers(taxi_exp_client)

    # adding consumer with service name
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_1', 'service': 'service_name'},
    )
    assert response.status == 200
    assert len(await filters.get_consumers(taxi_exp_client)) == 1

    # adding consumer with same service name
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_2', 'service': 'service_name'},
    )
    assert response.status == 200
    assert len(await filters.get_consumers(taxi_exp_client)) == 2

    # adding consumer with other service name
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_3', 'service': 'other_service_name'},
    )
    assert response.status == 200
    assert len(await filters.get_consumers(taxi_exp_client)) == 3

    assert (
        len(await filters.get_consumers(taxi_exp_client, service='other')) == 1
    )
    assert (
        len(await filters.get_consumers(taxi_exp_client, service='service'))
        == 3
    )

    # adding consumer with empty service name
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_4'},
    )
    response = await filters.get_consumers(
        taxi_exp_client, name='test_consumer_4',
    )
    assert 'service' not in response[0]
    assert 'description' not in response[0]
