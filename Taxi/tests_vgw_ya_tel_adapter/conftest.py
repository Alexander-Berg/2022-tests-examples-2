# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json
import typing
import uuid

import grpc
import pytest
import telephony_platform_pb2 as tel_pb
import telephony_platform_pb2_grpc as tel_pb_grpc

from vgw_ya_tel_adapter_plugins import *  # noqa: F403 F401

from tests_vgw_ya_tel_adapter import consts
from tests_vgw_ya_tel_adapter import telephony_mock


@pytest.fixture(scope='session')
def _grpc_port(get_free_port) -> int:
    return get_free_port()


@pytest.fixture(name='mock_ya_tel_grpc')
async def _mock_ya_tel_grpc(_grpc_port, load_json, mocked_time):
    redirections = load_json('redirections.json')
    service_numbers = load_json('service_numbers.json')
    for number in service_numbers.values():
        if number['state'] == 'active':
            number['state'] = tel_pb.ServiceNumberState.ACTIVE
        elif number['state'] == 'removed':
            number['state'] = tel_pb.ServiceNumberState.REMOVED
        elif number['state'] == 'in_quarantine':
            number['state'] = tel_pb.ServiceNumberState.IN_QUARANTINE
    mocked_data = telephony_mock.MockedYaTelData(
        redirections=redirections, service_numbers=service_numbers,
    )

    server = grpc.aio.server()
    servicer = telephony_mock.TelephonyPlatformServiceServicer(
        mocked_data,
        mocked_time.now(),
        consts.MockGrpc.TVM_TICKET,
        consts.MockGrpc.TEL_TICKET,
    )
    tel_pb_grpc.add_TelephonyPlatformServiceServicer_to_server(
        servicer, server,
    )
    server.add_insecure_port(f'{consts.MockGrpc.HOST}:{_grpc_port}')
    await server.start()
    yield mocked_data
    await server.stop(consts.MockGrpc.TIMEOUT)


def _check_headers(headers: typing.Dict[str, str]):
    assert uuid.UUID(headers['X-Request-Id'])
    assert headers['X-Ya-Service-Ticket'] == consts.MockGrpc.TVM_TICKET


@pytest.fixture(name='mock_ya_tel')
def _mock_ya_tel(mockserver, load_binary, _grpc_port):
    class Context:
        @staticmethod
        @mockserver.json_handler('/ya-tel/tickets')
        def tickets(request):
            _check_headers(request.headers)
            return {
                'ticketId': consts.MockGrpc.TEL_TICKET,
                'apiHost': consts.MockGrpc.HOST,
                'apiPort': _grpc_port,
                'ttl': 3000,
                'apiKind': 'admin-api',
            }

        @staticmethod
        @mockserver.handler(r'/ya-tel/records/(?P<record_id>.+)', regex=True)
        def records_by_id(request, record_id):
            _check_headers(request.headers)
            if record_id == '231f7ae3-1d3a-7c9-cc1e-b471ba1142f3':
                return mockserver.make_response(
                    load_binary('call.wav'),
                    status=200,
                    content_type='audio/wav',
                )
            return mockserver.make_response(status=404)

    return Context()


@pytest.fixture(name='mock_vgw_api')
async def _mock_vgw_api(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/vgw-api/v1/talks/')
        def talks(request):
            return mockserver.make_response(status=200, json={})

        @staticmethod
        @mockserver.json_handler('/vgw-api/v1/forwardings/state')
        def forwardings_state(request):
            return mockserver.make_response(status=200, json={})

    return Context()


@pytest.fixture(name='mock_vgw_api_fail')
async def _mock_vgw_api_fail(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/vgw-api/v1/talks/')
        def talks(request):
            return mockserver.make_response(status=500)

        @staticmethod
        @mockserver.json_handler('/vgw-api/v1/forwardings/state')
        def forwardings_state(request):
            return mockserver.make_response(status=500)

    return Context()


@pytest.fixture(name='lb_message_sender')
async def _lb_message_sender(taxi_vgw_ya_tel_adapter, load, testpoint):
    class Sender:
        @staticmethod
        async def send(message, prefix, **kwargs):
            if not isinstance(message, list):
                messages = [message]
            else:
                messages = message
            for msg in messages:
                raw = not msg.endswith('.json')
                response = await taxi_vgw_ya_tel_adapter.post(
                    'tests/logbroker/messages',
                    data=json.dumps(
                        {
                            'consumer': f'{prefix}_consumer',
                            'data': msg if raw else load(msg),
                            'topic': f'{prefix}-topic',
                            'cookie': 'cookie1',
                            **kwargs,
                        },
                    ),
                )
                assert response.status_code == 200

    return Sender()
