# pylint: disable=too-many-statements

from test_taxi_exp.helpers import filters


async def test_filters(taxi_exp_client):
    assert not await filters.get_consumers(taxi_exp_client)
    assert not await filters.get_applications(taxi_exp_client)

    # adding consumers
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_1'},
    )
    assert response.status == 200

    assert len(await filters.get_consumers(taxi_exp_client)) == 1

    # adding application
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/applications/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_application_1'},
    )
    assert response.status == 200

    assert len(await filters.get_applications(taxi_exp_client)) == 1

    # adding consumer with the same name
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_1'},
    )
    assert response.status == 409

    # adding application with the same name
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/applications/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_application_1'},
    )
    assert response.status == 409

    # delete consumer which doesn't exist
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_2'},
    )
    assert response.status == 404

    # delete application which doesn't exist
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/application/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_application_2'},
    )
    assert response.status == 404

    # delete consumer
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer_1'},
    )
    assert response.status == 200

    # delete application
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/applications/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_application_1'},
    )
    assert response.status == 200

    assert not await filters.get_consumers(taxi_exp_client)
    assert not await filters.get_applications(taxi_exp_client)
