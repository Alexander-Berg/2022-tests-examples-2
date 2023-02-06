import contextlib
import subprocess
from typing import Any
from typing import AsyncContextManager
from typing import AsyncGenerator
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Sequence

import aiohttp
import pytest

from testsuite import annotations
from testsuite._internal import fixture_class
from testsuite._internal import fixture_types

from . import service_client
from . import service_daemon

SERVICE_WAIT_ERROR = (
    'In order to use --service-wait flag you have to disable output capture '
    'with -s flag.'
)


class _DaemonScope:
    def __init__(self, name: str, spawn: Callable) -> None:
        self.name = name
        self._spawn = spawn

    async def spawn(self) -> 'DaemonInstance':
        daemon = await self._spawn()
        process = await daemon.__aenter__()
        return DaemonInstance(daemon, process)


class DaemonInstance:
    process: Optional[subprocess.Popen]

    def __init__(self, daemon, process) -> None:
        self._daemon = daemon
        self.process = process

    async def close(self) -> None:
        await self._daemon.__aexit__(None, None, None)


class _DaemonStore:
    cells: Dict[str, DaemonInstance]

    def __init__(self) -> None:
        self.cells = {}

    async def close(self) -> None:
        for daemon in self.cells.values():
            await daemon.close()
        self.cells = {}

    @contextlib.asynccontextmanager
    async def scope(self, name, spawn) -> AsyncGenerator[_DaemonScope, None]:
        scope = _DaemonScope(name, spawn)
        try:
            yield scope
        finally:
            daemon = self.cells.pop(name, None)
            if daemon:
                await daemon.close()

    async def request(self, scope: _DaemonScope) -> DaemonInstance:
        if scope.name in self.cells:
            daemon = self.cells[scope.name]
            if daemon.process is None:
                return daemon
            if daemon.process.poll() is None:
                return daemon
        await self.close()
        daemon = await scope.spawn()
        self.cells[scope.name] = daemon
        return daemon

    def has_running_daemons(self) -> bool:
        for daemon in self.cells.values():
            if daemon.process and daemon.process.poll() is None:
                return True
        return False


class EnsureDaemonStartedFixture(fixture_class.Fixture):
    """Fixture that starts requested service."""

    _fixture__global_daemon_store: _DaemonStore

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._requests = []

    async def __call__(self, scope: _DaemonScope) -> DaemonInstance:
        self._requests.append(scope.name)
        if len(self._requests) > 1:
            pytest.fail('Test requested multiple daemons: %r' % self._requests)
        return await self._fixture__global_daemon_store.request(scope)


class ServiceSpawnerFixture(fixture_class.Fixture):
    _fixture_pytestconfig: Any

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._reporter = self._fixture_pytestconfig.pluginmanager.getplugin(
            'terminalreporter',
        )

    def __call__(
            self,
            args: Sequence[str],
            check_url: str,
            *,
            base_command: Optional[Sequence[str]] = None,
            env: Optional[Dict[str, str]] = None,
            graceful_shutdown: bool = True,
            poll_retries: int = service_daemon.POLL_RETRIES,
            ping_request_timeout: float = service_daemon.PING_REQUEST_TIMEOUT,
            subprocess_options: Optional[Dict[str, Any]] = None,
            setup_service: Optional[Callable[[subprocess.Popen], None]] = None,
    ):
        """Creates service spawner.

        :param args: Service executable arguments list.
        :param check_url: Service /ping url used to ensure that service
            is up and running.
        """

        pytestconfig = self._fixture_pytestconfig

        async def spawn():
            if pytestconfig.option.service_wait:
                # It looks like pytest 3.8's global_and_fixture_disabled would
                # help here to re-enable console output. Throw error now.
                if pytestconfig.option.capture != 'no':
                    raise RuntimeError(SERVICE_WAIT_ERROR)
                return service_daemon.service_wait(
                    args,
                    check_url,
                    reporter=self._reporter,
                    base_command=base_command,
                    ping_request_timeout=ping_request_timeout,
                )
            if pytestconfig.option.service_disable:
                return service_daemon.start_dummy_process()
            return service_daemon.start(
                args,
                check_url,
                base_command=base_command,
                env=env,
                graceful_shutdown=graceful_shutdown,
                poll_retries=poll_retries,
                ping_request_timeout=ping_request_timeout,
                subprocess_options=subprocess_options,
                setup_service=setup_service,
            )

        return spawn


class CreateDaemonScope(fixture_class.Fixture):
    """Create daemon scope for daemon with command to start."""

    _fixture__global_daemon_store: _DaemonStore
    _fixture_service_spawner: ServiceSpawnerFixture

    def __call__(
            self,
            *,
            args: Sequence[str],
            check_url: str,
            name: Optional[str] = None,
            base_command: Optional[Sequence] = None,
            env: Optional[Dict[str, str]] = None,
            graceful_shutdown: bool = True,
            poll_retries: int = service_daemon.POLL_RETRIES,
            ping_request_timeout: float = service_daemon.PING_REQUEST_TIMEOUT,
            subprocess_options: Optional[Dict[str, Any]] = None,
            setup_service: Optional[Callable[[subprocess.Popen], None]] = None,
    ) -> AsyncContextManager[_DaemonScope]:
        """
        :param args: command arguments
        :param check_url: service health check url, service is considered up
            when 200 received.
        :param base_command: Arguments to be prepended to ``args``.
        :param env: Environment variables dictionary.
        :param graceful_shutdown: Kill service gracefully if set
        :param poll_retries: Number of tries for service health check
        :param ping_request_timeout: Timeout for check_url request
        :param subprocess_options: Custom subprocess options.
        :param setup_service: Function to be called right after service
            is started.
        :returns: Returns internal daemon scope instance to be used with
            ``ensure_daemon_started`` fixture.
        """
        if name is None:
            name = ' '.join(args)
        return self._fixture__global_daemon_store.scope(
            name=name,
            spawn=self._fixture_service_spawner(
                args=args,
                check_url=check_url,
                base_command=base_command,
                env=env,
                graceful_shutdown=graceful_shutdown,
                poll_retries=poll_retries,
                ping_request_timeout=ping_request_timeout,
                subprocess_options=subprocess_options,
                setup_service=setup_service,
            ),
        )


class CreateServiceClientFixture(fixture_class.Fixture):
    """Creates service client instance.

    Example:

    .. code-block:: python

        def my_client(create_service_client):
            return create_service_client('http://localhost:9999/')
    """

    _fixture_service_client_default_headers: Dict[str, str]
    _fixture_service_client_options: Dict[str, Any]

    def __call__(
            self,
            base_url: str,
            *,
            client_class=service_client.Client,
            **kwargs,
    ):
        """
        :param base_url: base url for http client
        :param client_class: client class to use
        :returns: ``client_class`` instance
        """
        return client_class(
            base_url,
            headers=self._fixture_service_client_default_headers,
            **self._fixture_service_client_options,
            **kwargs,
        )


ensure_daemon_started = fixture_class.create_fixture_factory(
    EnsureDaemonStartedFixture,
)
service_spawner = fixture_class.create_fixture_factory(
    ServiceSpawnerFixture, scope='session',
)
create_daemon_scope = fixture_class.create_fixture_factory(
    CreateDaemonScope, scope='session',
)
create_service_client = fixture_class.create_fixture_factory(
    CreateServiceClientFixture,
)


def pytest_addoption(parser):
    group = parser.getgroup('services')
    group.addoption(
        '--service-timeout',
        metavar='TIMEOUT',
        help=(
            'Service client timeout in seconds. 0 means no timeout. '
            'Default is %(default)s'
        ),
        default=120.0,
        type=float,
    )
    group.addoption(
        '--service-disable',
        action='store_true',
        help='Do not start service daemon from testsuite',
    )
    group.addoption(
        '--service-wait',
        action='store_true',
        help='Wait for service to start outside of testsuite itself, e.g. gdb',
    )
    group.addoption(
        '--service-log-level',
        type=lambda value: value.lower(),
        choices=['debug', 'info', 'warning', 'error', 'critical'],
    )


@pytest.fixture(scope='session')
def register_daemon_scope(_global_daemon_store: _DaemonStore):
    """Context manager that registers service process session.

    Yields daemon scope instance.

    :param name: service name
    :spawn spawn: spawner function
    """
    return _global_daemon_store.scope


@pytest.fixture
async def service_client_session() -> annotations.AsyncYieldFixture[
        aiohttp.ClientSession,
]:
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
def service_client_default_headers() -> Dict[str, str]:
    """Default service client headers.

    Fill free to override in your conftest.py
    """
    return {}


@pytest.fixture
def service_client_options(
        pytestconfig,
        service_client_session: aiohttp.ClientSession,
        mockserver: fixture_types.MockserverFixture,
) -> annotations.YieldFixture[Dict[str, Any]]:
    """Returns service client options dictionary."""
    yield {
        'session': service_client_session,
        'timeout': pytestconfig.option.service_timeout or None,
        'span_id_header': mockserver.span_id_header,
    }


@pytest.fixture(scope='session')
async def _global_daemon_store(loop):
    store = _DaemonStore()
    try:
        yield store
    finally:
        await store.close()
