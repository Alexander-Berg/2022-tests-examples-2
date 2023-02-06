import pytest

from test_taxi_exp.helpers import db


@pytest.mark.pgsql(
    'taxi_exp',
    queries=[
        db.ADD_CONSUMER.format('launch'),
        db.ADD_KWARGS.format(
            consumer='launch',
            kwargs="""[
                {"name":"uuid", "type":"string"},
                {"name":"zone", "type":"string"}
            ]""",
            metadata='{}',
            library_version='1',
        ),
    ],
)
async def test(taxi_exp_client):
    # check first update cache (full)
    await taxi_exp_client.app.ctx.kwargs_cache.refresh_cache()
    assert (
        taxi_exp_client.app.ctx.kwargs_cache.get_kwargs_by_consumer('launch')
        == [
            {'name': 'uuid', 'type': 'string'},
            {'name': 'zone', 'type': 'string'},
        ]
    )

    # add new consumer data
    data = {
        'consumer': 'test_consumer',
        'kwargs': [{'name': 'phone_id', 'type': 'string'}],
        'metadata': {'supported_features': ['geozone_matching']},
    }
    response = await taxi_exp_client.post(
        '/v1/consumers/kwargs/',
        headers={'X-Ya-Service-Ticket': '123'},
        json=data,
    )
    assert response.status == 200, await response.text()

    # check second update cache (partial)
    await taxi_exp_client.app.ctx.kwargs_cache.refresh_cache()
    assert (
        taxi_exp_client.app.ctx.kwargs_cache.get_kwargs_by_consumer('launch')
        == [
            {'name': 'uuid', 'type': 'string'},
            {'name': 'zone', 'type': 'string'},
        ]
    )
    assert taxi_exp_client.app.ctx.kwargs_cache.get_kwargs_by_consumer(
        'test_consumer',
    ) == [{'name': 'phone_id', 'type': 'string'}]
