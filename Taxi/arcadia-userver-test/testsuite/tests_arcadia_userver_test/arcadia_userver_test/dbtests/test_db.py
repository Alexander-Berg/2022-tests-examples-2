import pytest


@pytest.mark.pgsql('arcadia_test', files=['postgres.sql'])
async def test_pg_values_are_inserted(taxi_arcadia_userver_test, pgsql):
    response = await taxi_arcadia_userver_test.post(
        '/databases/postgres/insert', data='foobar',
    )

    assert response.status_code == 200, response.text

    inserted_id = response.json()['entry_id']
    cursor = pgsql['arcadia_test'].cursor()
    cursor.execute(
        f'SELECT stored_value FROM test_values WHERE id = {inserted_id}',
    )
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == 'foobar'


@pytest.mark.redis_store(['set', 'foo', 'bar'])
async def test_redis_cache_works(taxi_arcadia_userver_test):
    response = await taxi_arcadia_userver_test.get(
        '/databases/redis/value', params={'key': 'foo'},
    )
    assert response.status_code == 200, response.text
    assert response.json()['value'] == 'bar'


@pytest.mark.redis_store(file='redis')
async def test_redis_cache_works_with_populate_script(
        taxi_arcadia_userver_test,
):
    await test_redis_cache_works(taxi_arcadia_userver_test)


@pytest.mark.filldb(dump_sample='default')
async def test_mongo_fetch_works_with_populate_script(
        taxi_arcadia_userver_test,
):
    response = await taxi_arcadia_userver_test.get(
        '/databases/mongo/value', params={'key': 'foo'},
    )
    assert response.status_code == 200, response.text
    assert response.json()['value'] == 'bar'


@pytest.mark.clickhouse('arcadia_test', files=['ch.sql'])
async def test_clickhouse_works_with_populate_script(
        taxi_arcadia_userver_test,
):
    response = await taxi_arcadia_userver_test.get(
        '/databases/clickhouse/value', params={'key': 'foo'},
    )
    assert response.status_code == 200, response.text
    assert response.json()['value'] == 'bar'
