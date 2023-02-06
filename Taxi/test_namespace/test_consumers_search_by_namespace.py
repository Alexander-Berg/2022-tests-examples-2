from test_taxi_exp.helpers import filters


async def test_consumers_search_by_namespace(taxi_exp_client):
    assert not await filters.get_consumers(taxi_exp_client)
    assert not await filters.get_applications(taxi_exp_client)

    # adding consumers
    response = await filters.add_consumer(
        taxi_exp_client, name='test_consumer_1',
    )
    assert response.status == 200

    response = await filters.add_consumer(
        taxi_exp_client, name='test_consumer_2', namespace='market',
    )
    assert response.status == 200

    assert len(await filters.get_consumers(taxi_exp_client)) == 1

    assert (
        len(await filters.get_consumers(taxi_exp_client, namespace='market'))
        == 1
    )
