# pylint: disable=redefined-outer-name

import random
import string
import uuid

import aiohttp
import pytest

from taxi_corp.clients import protocol
from taxi_corp.util import hdrs as taxi_hdrs

DEFAULT_TIMEOUT = 1.0


def generate_id():
    """Generate UUID"""
    return uuid.uuid4().hex


CLIENT_ID = generate_id()
LOG_EXTRA = {'_link': generate_id()}


@pytest.fixture
async def http_session(loop):
    from taxi.clients import http_client

    async with http_client.HTTPClient(loop=loop) as session:
        yield session


@pytest.fixture
def make_handler():
    def maker(response, callback):
        async def handler(request):
            await callback(request)
            return aiohttp.web.json_response(response or {})

        return handler

    return maker


@pytest.fixture
def make_client(aiohttp_server, make_handler, http_session):
    async def maker(endpoint, response, callback):
        app = aiohttp.web.Application()
        app.router.add_post(endpoint, make_handler(response, callback))

        server = await aiohttp_server(app)
        host = 'http://{}:{}'.format(server.host, server.port)

        return protocol.ProtocolClient(http_session, host, DEFAULT_TIMEOUT)

    return maker


@pytest.fixture
def raw_headers(request):
    def _random_string():
        return ''.join(random.choices(string.ascii_letters, k=10))

    return {k: _random_string() for k in request.param}


def check_raw_headers(request_headers, raw_headers):
    """Check what raw_headers are filtered correctly"""

    proto_headers = [k for k in raw_headers if k in protocol.PROTOCOL_HEADERS]
    other_headers = [
        k for k in raw_headers if k not in protocol.PROTOCOL_HEADERS
    ]

    assert all(k in request_headers for k in proto_headers)
    assert all(k not in request_headers for k in other_headers)
    assert all(request_headers[k] == raw_headers[k] for k in proto_headers)


async def test_base(make_client):
    response = {'hello': 'protocol'}
    url = '/base'

    async def callback(request):
        assert str(request.url) == protocol_client.build_url(url)
        assert request.headers[taxi_hdrs.X_YAREQUEST_ID] == LOG_EXTRA['_link']

    protocol_client = await make_client(url, response, callback)

    data = await protocol_client.request(url, log_extra=LOG_EXTRA)
    assert data == response


async def test_nearest(make_client):
    point = {'lat': 37.0, 'long': 55.0}
    response = {'nearest_zone': 'test_zone'}

    async def callback(request):
        request_json = await request.json()
        assert request_json['point'] == point
        assert request_json['id'] == CLIENT_ID

    protocol_client = await make_client('/3.0/nearestzone', response, callback)

    data = await protocol_client.nearestzone(point=point, client_id=CLIENT_ID)

    assert data == 'test_zone'
