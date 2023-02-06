import asyncio
import io

import pytest


async def test_get_and_set_value(taxi_api_cache):

    response = await taxi_api_cache.get('v1/cached-value/source?key=key')
    assert response.status_code == 404

    response = await taxi_api_cache.put(
        'v1/cached-value/source?key=key',
        data=io.StringIO('string of bytes'),
        headers={'Content-Type': 'application/octet-stream'},
    )
    assert response.status_code == 200

    response = await taxi_api_cache.get('v1/cached-value/source?key=key')
    assert response.status_code == 200
    assert response.content == b'string of bytes'


@pytest.mark.parametrize(
    'request_headers',
    [
        pytest.param(
            {
                'Content-Type': 'application/octet-stream',
                'Cache-Control': 'max-age=1',
            },
            id='header ttl',
        ),
        pytest.param(
            {
                'Content-Type': 'application/octet-stream',
                'Cache-Control': 'max-age=100',
            },
            marks=[
                pytest.mark.config(
                    API_CACHE_REDIS_TTL_SETTINGS={
                        'enabled': True,
                        'max-ttl-seconds': 1,
                    },
                ),
            ],
            id='header ttl, override by config',
        ),
        pytest.param(
            {'Content-Type': 'application/octet-stream'},
            marks=[
                pytest.mark.config(
                    API_CACHE_REDIS_TTL_SETTINGS={
                        'enabled': True,
                        'max-ttl-seconds': 1,
                    },
                ),
            ],
            id='no header ttl, use config',
        ),
    ],
)
async def test_time_to_live(taxi_api_cache, request_headers):
    response = await taxi_api_cache.put(
        'v1/cached-value/source?key=key',
        data=io.StringIO('string of bytes'),
        headers=request_headers,
    )
    assert response.status_code == 200

    response = await taxi_api_cache.get('v1/cached-value/source?key=key')
    assert response.status_code == 200
    assert response.content == b'string of bytes'

    # make sure the key has already expired
    await asyncio.sleep(1.5)

    response = await taxi_api_cache.get('v1/cached-value/source?key=key')
    assert response.status_code == 404


async def test_key_escaping(taxi_api_cache):
    response = await taxi_api_cache.put(
        'v1/cached-value/a?key=b:c',
        data=io.StringIO('string of bytes'),
        headers={'Content-Type': 'application/octet-stream'},
    )
    assert response.status_code == 200

    response = await taxi_api_cache.get('v1/cached-value/a?key=b:c')
    assert response.status_code == 200
    assert response.content == b'string of bytes'

    response = await taxi_api_cache.get('v1/cached-value/a:b?key=c')
    assert response.status_code == 404
    response = await taxi_api_cache.get(r'v1/cached-value/a:b\?key=c')
    assert response.status_code == 404


async def test_key_deletion(taxi_api_cache):
    # it's ok to delete non-existing key
    response = await taxi_api_cache.delete('v1/cached-value/source?key=key')
    assert response.status_code == 200

    response = await taxi_api_cache.put(
        'v1/cached-value/source?key=key',
        data=io.StringIO('string of bytes'),
        headers={'Content-Type': 'application/octet-stream'},
    )
    assert response.status_code == 200

    response = await taxi_api_cache.get('v1/cached-value/source?key=key')
    assert response.status_code == 200
    assert response.content == b'string of bytes'

    response = await taxi_api_cache.delete('v1/cached-value/source?key=key')
    assert response.status_code == 200

    response = await taxi_api_cache.get('v1/cached-value/source?key=key')
    assert response.status_code == 404
