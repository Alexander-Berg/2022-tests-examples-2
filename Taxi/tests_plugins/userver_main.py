# pylint: disable=invalid-name,redefined-outer-name
import contextlib
import pathlib
import subprocess
import sys
import tempfile
import threading
import traceback
import typing
import logging

import aiohttp
import pytest

from testsuite.logging import logger

from . import colorize
from . import service_logs_dumper_plugin

try:
    import yatest.common
    IS_ARCADIA = True
except ImportError:
    IS_ARCADIA = False

pytest_plugins = ['tests_plugins.mongodb_settings']

USERVER_CONFIG_HOOKS = ['_userver_configure_listeners']

root_logger = logging.getLogger()

CORE_PATTERN: str = '/coredumps/*.%p.%s'


class ColorLogger(logger.Logger):
    def __init__(
            self, *, writer: logger.LineLogger, verbose, colors_enabled,
    ) -> None:
        super().__init__(writer)
        self._colorizer = colorize.Colorizer(
            verbose=verbose, colors_enabled=colors_enabled,
        )

    def log_service_line(self, line) -> None:
        line = self._colorizer.colorize_line(line)
        if line:
            self.writeline(line)

    def log_entry(self, entry: dict) -> None:
        line = self._colorizer.colorize_tskv_row(entry)
        if line:
            self.writeline(line)


class ServiceLogFile:
    _file: typing.Optional[typing.BinaryIO]

    def __init__(self, path: pathlib.Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = path.open('wb')
        self._write_lock = threading.Lock()

    def write(self, line: bytes) -> None:
        with self._write_lock:
            if self._file is not None:
                try:
                    self._file.write(line)
                    # flake8: noqa
                except:
                    self._file = None
                    traceback.print_exc(file=sys.stderr)

    def flush(self) -> None:
        with self._write_lock:
            if self._file is not None:
                self._file.flush()


class ServiceProgressWatcher:
    def __init__(self):
        self.out_filename = None
        self.err_filename = None

    def open(self, command, process, out_file, err_file):
        if out_file:
            self.out_filename = pathlib.Path(out_file.name)
        if err_file:
            self.err_filename = pathlib.Path(err_file.name)

    def close(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


def pytest_addoption(parser) -> None:
    group = parser.getgroup('services')
    group.addoption(
        '--build-dir',
        default=pathlib.Path.cwd() / '.build',
        type=pathlib.Path,
        help='Path to build directory.',
    )
    group.addoption(
        '--service-log-level',
        type=str.lower,
        choices=['trace', 'debug', 'info', 'warning', 'error', 'critical'],
    )
    group.addoption(
        '--service-logs-file',
        type=pathlib.Path,
        help='Write service output to specified file',
    )
    group.addoption(
        '--service-logs-pretty',
        action='store_true',
        help='Enable pretty print and colorize service logs',
    )
    group.addoption(
        '--service-logs-pretty-verbose',
        dest='service_logs_pretty',
        action='store_const',
        const='verbose',
        help='Enable pretty print and colorize service logs in verbose mode',
    )
    group.addoption(
        '--service-logs-pretty-disable',
        action='store_false',
        dest='service_logs_pretty',
        help='Disable pretty print and colorize service logs',
    )
    group.addoption(
        '--original-logs',
        action='store_true',
        help='Force original logs behaviour',
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'suspend_periodic_tasks: '
        'Stop specified periodic tasks for the duration of the test. '
        'each argument is a name of task',
    )
    config.addinivalue_line(
        'markers',
        'uservice_oneshot(config_hooks=[...]): '
        'Use oneshot uservice daemon instance. Use config_hooks to specify per '
        'test configuration file hook.',
    )


# library_paths gets overridden by unit pytest plugins,
# so this fixture must remain in function scope to avoid
# getting stuck with library_paths for another unit
@pytest.fixture
def initial_data_path(
        library_paths, service_source_dir, get_source_path,
) -> typing.List[pathlib.Path]:
    return [
        service_source_dir / 'testsuite/static',
        service_source_dir / 'testsuite',
        get_source_path('testsuite/default_fixtures').resolve(),
        *library_paths,
    ]


@pytest.fixture(name='build_dir', scope='session')
def _build_dir(request) -> pathlib.Path:
    if IS_ARCADIA:
        return pathlib.Path(yatest.common.build_path('build'))
    return pathlib.Path(request.config.getoption('--build-dir'))


class LogsCollector:
    join_timeout = 2.0

    def __init__(self, testsuite_logger, uservice_logfile):
        self.thread = None
        self.testsuite_logger = testsuite_logger
        self.uservice_logfile = uservice_logfile

    def start_collector(self, process):
        if self.thread:
            raise RuntimeError('Collector thread already started')
        self.thread = threading.Thread(
            target=_process_service_stderr,
            args=(self.testsuite_logger, self.uservice_logfile, process),
        )
        self.thread.daemon = True
        self.thread.start()

    def try_join(self):
        if self.thread:
            self.thread.join(timeout=self.join_timeout)
            if self.thread.is_alive():
                root_logger.warning(
                    'Child process logging thread did not finished',
                )


class CoreDumpsCollector:
    def __init__(
            self,
            service_logs_dumper: service_logs_dumper_plugin.ServiceLogsDumper,
    ):
        self.service_logs_dumper = service_logs_dumper

    def get_spawner_process(self, args, **kwargs):
        return subprocess.Popen(args, **kwargs)

    def collect_core_dumps(self) -> None:
        pass


class ArcadiaCoreDumpsCollector(CoreDumpsCollector):
    execution_object = None

    def get_spawner_process(self, args, **kwargs):
        process_progress_listener = ServiceProgressWatcher()
        self.execution_object = yatest.common.execute(
            args,
            **kwargs,
            wait=False,
            core_pattern=CORE_PATTERN,
            collect_cores=True,
            process_progress_listener=process_progress_listener,
        )
        for fp_name in (
                process_progress_listener.err_filename,
                process_progress_listener.out_filename,
        ):
            if fp_name is None:
                continue
            self.service_logs_dumper.register_log(fp_name)
        return self.execution_object.process

    def collect_core_dumps(self) -> None:
        root_logger.info('Collect core dumps')
        if self.execution_object:
            root_logger.info('Verify no core dumps')
            self.execution_object.verify_no_coredumps()


@pytest.fixture(scope='session')
def userver_service_spawner(
        pytestconfig,
        service_spawner,
        testsuite_logger,
        _uservice_logfile: typing.Optional[ServiceLogFile],
        service_logs_dumper,
):
    service_logs_pretty = pytestconfig.option.service_logs_pretty
    if service_logs_pretty:
        logger_plugin = pytestconfig.pluginmanager.getplugin(
            'testsuite_logger',
        )
        logger_plugin.enable_logs_suspension()

    core_dumps_factory: typing.Type[CoreDumpsCollector]
    if IS_ARCADIA and not pytestconfig.option.original_logs:
        include_logs_collector = False
        core_dumps_factory = ArcadiaCoreDumpsCollector
    else:
        include_logs_collector = service_logs_pretty or bool(_uservice_logfile)
        core_dumps_factory = CoreDumpsCollector

    def spawner(*args, **kwargs):
        # TODO: cleanup interface, see TAXIDATA-2623
        @contextlib.asynccontextmanager
        async def spawn_cm():
            logs_collector = None
            if include_logs_collector:
                logs_collector = LogsCollector(
                    testsuite_logger, _uservice_logfile,
                )
                # Start reading thread logs right after process is started to
                # avoid possible pipe deadlock.
                kwargs['setup_service'] = logs_collector.start_collector
                kwargs['subprocess_options'] = {'stderr': subprocess.PIPE}

            core_dumps_collector = core_dumps_factory(service_logs_dumper)
            kwargs[
                'subprocess_spawner'
            ] = core_dumps_collector.get_spawner_process
            orig_spawn = service_spawner(*args, **kwargs)

            try:
                async with (await orig_spawn()) as process:
                    yield process
            finally:
                if include_logs_collector:
                    logs_collector.try_join()
                core_dumps_collector.collect_core_dumps()

        async def spawn():
            return spawn_cm()

        return spawn

    return spawner


@pytest.fixture(scope='session')
def service_client_session_factory(
        userver_socket_path,
) -> typing.Callable[..., aiohttp.ClientSession]:
    def make_session(*, socket_path=userver_socket_path):
        socket_connector = aiohttp.UnixConnector(path=str(socket_path))
        return aiohttp.ClientSession(connector=socket_connector)

    return make_session


@pytest.fixture
async def service_monitor_client_options(
        userver_monitor_socket_path,
        service_client_session_factory,
        service_client_options,
) -> typing.AsyncGenerator[dict, None]:
    session = service_client_session_factory(
        socket_path=userver_monitor_socket_path,
    )
    async with session:
        monitor_options = service_client_options.copy()
        monitor_options['session'] = session
        yield monitor_options


@pytest.fixture(scope='session')
def _userver_configure_listeners(
        userver_socket_path, userver_monitor_socket_path,
):
    def configure_listeners(config, config_vars):
        # reconfigure userver to explicitly use unix sockets
        components = config['components_manager']['components']
        components['server']['listener'].pop('port', None)
        components['server']['listener']['unix-socket'] = str(
            userver_socket_path,
        )
        components['server']['listener-monitor'].pop('port', None)
        components['server']['listener-monitor']['unix-socket'] = str(
            userver_monitor_socket_path,
        )

        config_vars.update(
            {
                key: value.replace(
                    '$service_socket_path', str(userver_socket_path),
                )
                for key, value in config_vars.items()
                if isinstance(value, str) and '$service_socket_path' in value
            },
        )

    return configure_listeners


@pytest.fixture(scope='session')
def userver_socket_path(_userver_socket_dir) -> pathlib.Path:
    return _userver_socket_dir / 'server.sock'


@pytest.fixture(scope='session')
def userver_monitor_socket_path(_userver_socket_dir) -> pathlib.Path:
    return _userver_socket_dir / 'monitor.sock'


@pytest.fixture(scope='session')
def _userver_socket_dir() -> typing.Generator[pathlib.Path, None, None]:
    with tempfile.TemporaryDirectory(prefix='userver-') as temporary_dir:
        yield pathlib.Path(temporary_dir)


@pytest.fixture(scope='session')
def _uservice_logfile(pytestconfig) -> typing.Optional[ServiceLogFile]:
    path = pytestconfig.option.service_logs_file
    if not path:
        return None
    return ServiceLogFile(path)


def pytest_override_testsuite_logger(
        config, line_logger: logger.LineLogger, colors_enabled: bool,
) -> typing.Optional[logger.Logger]:
    pretty_logs = config.option.service_logs_pretty
    if not pretty_logs:
        return None
    return ColorLogger(
        writer=line_logger,
        verbose=pretty_logs == 'verbose',
        colors_enabled=colors_enabled,
    )


def _process_service_stderr(
        testsuite_logger,
        service_log_file: typing.Optional[ServiceLogFile],
        process,
):
    for line_binary in process.stderr:
        if service_log_file is not None:
            service_log_file.write(line_binary)
        try:
            line = line_binary.decode('utf-8').rstrip('\r\n')
            testsuite_logger.log_service_line(line)
        # flake8: noqa
        except:
            traceback.print_exc(file=sys.stderr)
    if service_log_file is not None:
        service_log_file.flush()


@pytest.fixture(scope='session')
def get_service_name(service_source_dir):
    return service_source_dir.parts[-1]
