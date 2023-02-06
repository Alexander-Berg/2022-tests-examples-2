import contextlib

import pytest
import requests

from tests_plugins.daemons import service_daemon

SERVICE_WAIT_ERROR = (
    'In order to use --service-wait flag you have to disable output capture '
    'with -s flag.'
)


class _DaemonScope:
    def __init__(self, name, spawn):
        self.name = name
        self._spawn = spawn

    def spawn(self):
        daemon = self._spawn()
        process = daemon.__enter__()
        return _DaemonInstance(daemon, process)


class _DaemonInstance:
    def __init__(self, daemon, process):
        self._daemon = daemon
        self.process = process

    def close(self):
        self._daemon.__exit__(None, None, None)


class _DaemonStore:
    def __init__(self):
        self.cells = {}

    def close(self):
        for daemon in self.cells.values():
            daemon.close()
        self.cells = {}

    @contextlib.contextmanager
    def scope(self, name, spawn):
        scope = _DaemonScope(name, spawn)
        try:
            yield scope
        finally:
            daemon = self.cells.pop(name, None)
            if daemon:
                daemon.close()

    def request(self, scope):
        if scope.name in self.cells:
            daemon = self.cells[scope.name]
            if daemon.process.poll() is None:
                return daemon
        self.close()
        daemon = scope.spawn()
        self.cells[scope.name] = daemon
        return daemon


@pytest.yield_fixture(scope='session')
def _global_daemon_store():
    store = _DaemonStore()
    with contextlib.closing(store):
        yield store


@pytest.fixture(scope='session')
def register_daemon_scope(_global_daemon_store):
    return _global_daemon_store.scope


@pytest.fixture
def ensure_daemon_started(_global_daemon_store, request):
    requests = []

    def do_ensure_daemon_started(scope):
        requests.append(scope.name)
        if len(requests) > 1:
            pytest.fail('Test requested multiple daemons: %r' % (requests,))
        return _global_daemon_store.request(scope)

    return do_ensure_daemon_started


@pytest.fixture(scope='session')
def service_client_options(request, pytestconfig):
    return {
        'session': requests.session(),
        'timeout': pytestconfig.getoption('--service-timeout') or None,
    }


@pytest.fixture(scope='session')
def service_spawner(pytestconfig):
    reporter = pytestconfig.pluginmanager.getplugin('terminalreporter')

    def create_spawner(
            args, check_url, *, settings=None, subprocess_options=None,
    ):
        def spawn():
            if pytestconfig.option.service_wait:
                # It looks like pytest 3.8's global_and_fixture_disabled would
                # help here to re-enable console output. Throw error now.
                if pytestconfig.option.capture != 'no':
                    raise RuntimeError(SERVICE_WAIT_ERROR)
                return service_daemon.service_wait(
                    args, check_url, reporter=reporter, settings=settings,
                )
            if pytestconfig.option.service_disable:
                return service_daemon.start_dummy_process()
            return service_daemon.start(
                args,
                check_url=check_url,
                settings=settings,
                subprocess_options=subprocess_options,
            )

        return spawn

    return create_spawner


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
