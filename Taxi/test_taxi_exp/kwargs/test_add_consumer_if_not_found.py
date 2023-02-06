import pytest

from taxi_exp.util import pg_helpers


async def check_consumer_found(app, consumer):
    query = 'SELECT name FROM clients_schema.consumers WHERE name=$1'
    pool = app['pool']
    response = await pg_helpers.fetchrow(pool, query, consumer)
    return response is not None


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_adding_consumer_if_not_found(taxi_exp_client):
    assert not await check_consumer_found(
        taxi_exp_client.app, 'non_existed_consumer',
    )

    response = await taxi_exp_client.post(
        '/v1/consumers/kwargs/',
        headers={'X-Ya-Service-Ticket': '123'},
        json={'consumer': 'non_existed_consumer', 'kwargs': []},
    )
    assert response.status == 200

    assert await check_consumer_found(
        taxi_exp_client.app, 'non_existed_consumer',
    )
