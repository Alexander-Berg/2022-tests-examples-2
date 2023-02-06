import pytest


CACHE_NAME = 'sample-postgres-cache'


async def test_postgres(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'count-payload-size', data='Hello world',
    )
    assert response.status_code == 200
    assert response.content == b'11'


async def test_postgres_shard(taxi_userver_sample):
    response = await taxi_userver_sample.get('ping-shard')
    assert response.status_code == 200
    assert response.content == b''


async def test_postgres_cache(taxi_userver_sample):
    response = await taxi_userver_sample.get('ping-pg-cache')
    assert response.status_code == 200
    assert response.content == b'3'


async def test_dump_write_read(taxi_userver_sample):
    await taxi_userver_sample.write_cache_dumps(names=[CACHE_NAME])
    await taxi_userver_sample.read_cache_dumps(names=[CACHE_NAME])


@pytest.mark.config(POSTGRES_HANDLERS_COMMAND_CONTROL={})
async def test_postgres_timeouts_not_set(taxi_userver_sample):
    response = await taxi_userver_sample.get('postgres-timeouts')
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.config(
    POSTGRES_HANDLERS_COMMAND_CONTROL={
        '/postgres-timeouts': {
            'GET': {'network_timeout_ms': 502, 'statement_timeout_ms': 251},
            'PUT': {'network_timeout_ms': 604, 'statement_timeout_ms': 302},
        },
    },
)
async def test_postgres_timeouts_per_handler(taxi_userver_sample):
    response = await taxi_userver_sample.get('postgres-timeouts')
    assert response.status_code == 200
    assert response.json() == {'execute': 502, 'statement': 251}

    response = await taxi_userver_sample.put('postgres-timeouts')
    assert response.status_code == 200
    assert response.json() == {'execute': 604, 'statement': 302}

    response = await taxi_userver_sample.post('postgres-timeouts')
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.config(
    POSTGRES_HANDLERS_COMMAND_CONTROL={
        '/ping': {
            'GET': {'network_timeout_ms': 1500, 'statement_timeout_ms': 750},
        },
        '/postgres-timeouts': {
            'GET': {'network_timeout_ms': 502, 'statement_timeout_ms': 251},
        },
        '/postgres/{param}/common-timeouts': {
            'GET': {'network_timeout_ms': 603, 'statement_timeout_ms': 303},
            'PUT': {'network_timeout_ms': 1000, 'statement_timeout_ms': 555},
        },
    },
)
async def test_postgres_timeouts_codegen_per_handler(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'postgres/some-param-value/common-timeouts',
    )
    assert response.status_code == 200
    assert response.json()['transaction_execute'] == 603
    assert response.json()['transaction_statement'] == 303


@pytest.mark.config(
    POSTGRES_QUERIES_COMMAND_CONTROL={
        'select1': {
            'network_timeout_ms': 11802,
            'statement_timeout_ms': 10901,
        },
    },
)
async def test_postgres_timeouts_per_query(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'postgres/some-param-value/common-timeouts',
    )
    assert response.status_code == 200
    assert response.json() == {'statement': 10901}


@pytest.mark.config(
    POSTGRES_QUERIES_COMMAND_CONTROL={
        'select1': {
            'network_timeout_ms': 11802,
            'statement_timeout_ms': 10901,
        },
    },
    POSTGRES_HANDLERS_COMMAND_CONTROL={
        '/postgres/{param}/common-timeouts': {
            'GET': {'network_timeout_ms': 603, 'statement_timeout_ms': 303},
        },
    },
)
async def test_postgres_timeouts_per_query_handler_mix(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'postgres/some-param-value/common-timeouts',
    )
    assert response.status_code == 200
    assert response.json() == {
        'transaction_execute': 603,
        'transaction_statement': 303,
        'statement': 10901,
    }
