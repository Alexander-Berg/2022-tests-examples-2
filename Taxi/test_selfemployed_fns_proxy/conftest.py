# pylint: disable=redefined-outer-name
import datetime as dt
import logging

import aiohttp.web
import pytest

from testsuite.utils import http

import selfemployed_fns_proxy.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'selfemployed_fns_proxy.generated.service.pytest_plugins',
    'test_selfemployed_fns_proxy.fns_message_generator',
]

logger = logging.getLogger(__name__)

logging.getLogger('zeep').setLevel(logging.INFO)


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'unmock_fns_auth: do not mock fns auth handlers',
    )


@pytest.fixture(autouse=True)
def mock_fns_auth(mockserver, fns_messages, request):
    if 'unmock_fns_auth' in request.keywords:
        logger.debug('skip mocking fns auth')
        return

    @mockserver.handler('/FnsAuthService')
    async def _handle(request: http.Request):
        request_xml = fns_messages.format_xml(request.get_data().decode())
        assert request_xml == fns_messages.fns_auth_request('SECRET')

        expiry_time = dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(
            days=365,
        )
        return aiohttp.web.Response(
            body=fns_messages.fns_auth_response(
                auth_token='AUTH_TOKEN', expire_time=expiry_time,
            ),
            content_type='application/xml',
        )


@pytest.fixture
def mock_simple_fns_communication(fns_messages, mockserver):
    def _fixture(
            send_message_request,
            send_message_response,
            get_message_request,
            get_message_response,
    ):
        @mockserver.handler('/SmzIntegrationService')
        async def _request(request: http.Request):
            request_xml = fns_messages.format_xml(request.get_data().decode())
            if request_xml == send_message_request:
                return aiohttp.web.Response(
                    body=send_message_response, content_type='application/xml',
                )
            if request_xml == get_message_request:
                return aiohttp.web.Response(
                    body=get_message_response, content_type='application/xml',
                )
            raise AssertionError('Invalid request')

    return _fixture


@pytest.fixture
def mock_fns_unavailable(fns_messages, mockserver):
    @mockserver.handler('/SmzIntegrationService')
    async def _request(*args, **kwargs):
        return aiohttp.web.Response(body='FNS Unavailable', status=503)


@pytest.fixture
def mock_personal_service(mock_personal):
    def _mock(pd_type: str, raw: str, pd_id: str):
        @mock_personal(f'/v1/{pd_type}/retrieve')
        async def _mock_retrieve(request: http.Request):
            assert request.json['id'] == pd_id
            return {'value': raw, 'id': pd_id}

        @mock_personal(f'/v1/{pd_type}/store')
        async def _mock_store(request: http.Request):
            assert request.json['value'] == raw
            return {'value': raw, 'id': pd_id}

    return _mock
