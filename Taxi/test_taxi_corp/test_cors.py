# pylint: disable=invalid-name

import aiohttp.hdrs
import aiohttp.web
import pytest

pytestmark = pytest.mark.config(
    CORP_CORS_SETTINGS=[
        {
            'path': r'/client/\w+/handler',
            'methods': ['POST', 'GET'],
            'hosts': ['front.com', 'com.front'],
        },
    ],
)


async def test_cors(taxi_corp_real_auth_client):

    response = await taxi_corp_real_auth_client.request(
        aiohttp.hdrs.METH_OPTIONS, '/client/client_id_1/handler',
    )

    assert response.status == 204

    allow_hosts = response.headers[aiohttp.hdrs.ACCESS_CONTROL_ALLOW_ORIGIN]
    assert allow_hosts == 'front.com com.front'

    allow_headers = response.headers[aiohttp.hdrs.ACCESS_CONTROL_ALLOW_HEADERS]
    assert allow_headers == aiohttp.hdrs.CONTENT_TYPE

    allow_methods = response.headers[aiohttp.hdrs.ACCESS_CONTROL_ALLOW_METHODS]
    assert allow_methods == 'POST GET'


async def test_cors_405(taxi_corp_real_auth_client):

    response = await taxi_corp_real_auth_client.request(
        aiohttp.hdrs.METH_OPTIONS, '/handler',
    )

    assert response.status == 404
