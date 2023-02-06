from test_taxi_exp.helpers import filters


async def test_consumers_exists_error(taxi_exp_client):
    assert not await filters.get_consumers(taxi_exp_client)
    assert not await filters.get_applications(taxi_exp_client)

    # add consumer
    response = await filters.add_consumer(
        taxi_exp_client, name='test', namespace='frozen',
    )
    assert response.status == 200
    # fail to add consumer with same name and different namespace
    response = await filters.add_consumer(
        taxi_exp_client, name='test', namespace='market',
    )
    assert response.status == 409
    assert (await response.json()) == {
        'code': 'CONSUMER_ALREADY_EXISTS',
        'message': (
            'Consumer with this name already exists. '
            'We suggest using market/test'
        ),
    }
    # fail to add consumer with same name and no namespace
    response = await filters.add_consumer(
        taxi_exp_client, name='test', namespace=None,
    )
    assert response.status == 409
    assert (await response.json()) == {
        'code': 'CONSUMER_ALREADY_EXISTS',
        'message': (
            'Consumer with this name already exists. '
            'We suggest using consumer service name as a prefix'
        ),
    }
    # fail to add consumer with same name and namespace
    response = await filters.add_consumer(
        taxi_exp_client, name='test', namespace='frozen',
    )
    assert response.status == 409
    assert (await response.json()) == {
        'code': 'DATABASE_ERROR',
        'message': (
            'duplicate key value violates unique constraint '
            '"consumers_name_key"\n'
            'DETAIL:  Key (name)=(test) already exists.'
        ),
    }
