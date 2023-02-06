import dataclasses
import os
import pathlib
import socket
import typing

from testsuite.environment import service
from testsuite.environment import utils

DEFAULT_HOSTNAME = 'localhost'
DEFAULT_HTTP_PROXY_PORT = 18000
DEFAULT_RPC_PROXY_PORT = 18002
DEFAULT_PORTS_RANGE_START = 18010

PLUGIN_DIR = pathlib.Path(__file__).parent
SCRIPTS_DIR = PLUGIN_DIR.joinpath('scripts')
HEALTHCHECK_SCRIPT = SCRIPTS_DIR.joinpath('healthcheck')


@dataclasses.dataclass(frozen=True)
class ConnectionInfo:
    hostname: str = DEFAULT_HOSTNAME
    http_proxy_port: int = DEFAULT_HTTP_PROXY_PORT

    @property
    def connection_string(self):
        return f'{self.hostname}:{self.http_proxy_port}'

    def replace(self, **kwargs) -> 'ConnectionInfo':
        """Returns new instance with attributes updated."""
        return dataclasses.replace(self, **kwargs)


@dataclasses.dataclass(frozen=True)
class ServiceSettings:
    hostname: str
    http_proxy_port: int
    rpc_proxy_port: int
    ports_range_start: int

    def get_conninfo(self) -> ConnectionInfo:
        return ConnectionInfo(
            hostname=self.hostname, http_proxy_port=self.http_proxy_port,
        )


def create_service(
        service_name: str,
        working_dir: str,
        settings: typing.Optional[ServiceSettings] = None,
        env: typing.Optional[typing.Dict[str, str]] = None,
):
    if settings is None:
        settings = get_service_settings()
    return service.ScriptService(
        service_name=service_name,
        script_path=str(SCRIPTS_DIR.joinpath('service-yt')),
        working_dir=working_dir,
        environment={
            'YT_TMPDIR': working_dir,
            'YT_HTTP_PROXY_PORT': str(settings.http_proxy_port),
            'YT_RPC_PROXY_PORT': str(settings.rpc_proxy_port),
            'YT_PORTS_RANGE_START': str(settings.ports_range_start),
            'YT_HOSTNAME': str(settings.hostname),
            'YT_HEALTHCHECK_SCRIPT': str(HEALTHCHECK_SCRIPT),
            **(env or {}),
        },
        check_ports=[settings.http_proxy_port, settings.rpc_proxy_port],
    )


def get_service_settings():
    return ServiceSettings(
        hostname=os.getenv('TESTSUITE_YT_HOSTNAME', DEFAULT_HOSTNAME),
        http_proxy_port=utils.getenv_int(
            'TESTSUITE_YT_HTTP_PROXY_PORT', DEFAULT_HTTP_PROXY_PORT,
        ),
        rpc_proxy_port=utils.getenv_int(
            'TESTSUITE_YT_RPC_PROXY_PORT', DEFAULT_RPC_PROXY_PORT,
        ),
        ports_range_start=utils.getenv_int(
            'TESTSUITE_YT_PORTS_RANGE_START', DEFAULT_PORTS_RANGE_START,
        ),
    )


def parse_connection_info(connstr: str) -> ConnectionInfo:
    hostname, port = connstr.split(':', 1)
    # resolve hostname since ytlib cannot resolve docker hosts
    address = socket.gethostbyname(hostname)
    return ConnectionInfo(hostname=address, http_proxy_port=int(port))
