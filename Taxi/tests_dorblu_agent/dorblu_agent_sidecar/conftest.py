import asyncio
import contextlib
import socket
import struct

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from dorblu_agent_sidecar_plugins import *  # noqa: F403 F401
# pylint: disable=import-error
import dorblu_pb2
from google.protobuf import json_format
import pytest


USERVER_CONFIG_HOOKS = [
    'patch_log_path',
    'patch_log_format_path',
    'patch_dorblu_config_path',
]
ACCESS_LOG_FNAME = 'nginx-access.log'
LOG_FORMAT_FNAME = 'nginx-01-accesslog.conf'
DORBLU_CONFIG_FNAME = 'dorblu-config.conf'


async def recvall(loop, sock, size):
    bytes_left = size
    chunks = []

    while bytes_left:
        chunk = await loop.sock_recv(sock, bytes_left)
        chunks.append(chunk)
        bytes_left -= len(chunk)

    data = b''.join(chunks)

    assert len(data) == size

    return data


@pytest.fixture
def request_agent():
    async def _impl(
            request_message: dorblu_pb2.MainMessage,
    ) -> dorblu_pb2.MainMessage:
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with contextlib.closing(sock):
            await loop.sock_connect(sock, ('127.0.0.1', 3033))

            request_message_str = request_message.SerializeToString()
            await loop.sock_sendall(
                sock, struct.pack('i', len(request_message_str)),
            )
            await loop.sock_sendall(sock, request_message_str)

            response_message_size = struct.unpack(
                'i', await recvall(loop, sock, 4),
            )[0]
            response_message_str = await recvall(
                loop, sock, response_message_size,
            )
            response_message = dorblu_pb2.MainMessage()
            response_message.ParseFromString(response_message_str)

            return response_message

    return _impl


@pytest.fixture(scope='session', name='default_log_path')
def default_log_path_fixture(testsuite_output_dir):
    return testsuite_output_dir / ACCESS_LOG_FNAME


@pytest.fixture(scope='session', name='default_log_format_path')
def default_log_format_path_fixture(testsuite_output_dir):
    return testsuite_output_dir / LOG_FORMAT_FNAME


@pytest.fixture(scope='session', name='dorblu_config_path')
def dorblu_config_path_fixture(testsuite_output_dir):
    return testsuite_output_dir / DORBLU_CONFIG_FNAME


@pytest.fixture(scope='session')
def patch_log_path(worker_id, default_log_path):
    def patch_config(config, config_vars):
        config_vars['default_log_path'] = str(default_log_path)

    return patch_config


@pytest.fixture(scope='session')
def patch_log_format_path(worker_id, default_log_format_path):
    def patch_config(config, config_vars):
        config_vars['default_log_format_path'] = str(default_log_format_path)

    return patch_config


@pytest.fixture(scope='session')
def patch_dorblu_config_path(worker_id, dorblu_config_path):
    def patch_config(config, config_vars):
        config_vars['dorblu_config_path'] = str(dorblu_config_path)

    return patch_config


@pytest.fixture
def fill_default_access_log(load, default_log_path):
    def _impl(fname):
        with default_log_path.open('w') as outfile:
            outfile.write(load(fname))

    return _impl


@pytest.fixture
def fill_default_log_format(load, default_log_format_path):
    def _impl(fname):
        with default_log_format_path.open('w') as outfile:
            outfile.write(load(fname))

    return _impl


@pytest.fixture
def reset_agent_metrics(testpoint):
    @testpoint('reset_metrics')
    def _reset_metrics(data):
        return {'reset_metrics': True}


@pytest.fixture
def load_json_message(load_json):
    def _impl(fname):
        return json_format.ParseDict(
            load_json(fname), dorblu_pb2.MainMessage(),
        )

    return _impl


@pytest.fixture(autouse=True)
async def setup_dorblu(
        taxi_dorblu_agent_sidecar,
        default_log_path,
        default_log_format_path,
        dorblu_config_path,
):
    if default_log_path.exists():
        default_log_path.unlink()
    if default_log_format_path.exists():
        default_log_format_path.unlink()
    if dorblu_config_path.exists():
        dorblu_config_path.unlink()

    yield

    await taxi_dorblu_agent_sidecar.run_task('dorblu_agent/stop')


@pytest.fixture
def start_dorblu_agent(taxi_dorblu_agent_sidecar):
    async def _impl():
        await taxi_dorblu_agent_sidecar.run_task('dorblu_agent/start')

    return _impl
