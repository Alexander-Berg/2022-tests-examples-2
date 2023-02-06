import contextlib
import os
import time
import typing

import requests
import requests.exceptions

from tests_plugins.daemons import spawn


class ServiceSettings:
    BASE_COMMAND: typing.List[str] = []
    GRACEFUL_SHUTDOWN = True
    POLL_RETRIES = 2000
    PING_REQUEST_TIMEOUT = 1.0


class _DummyProcess:
    def poll(self):  # pylint: disable=no-self-use
        return None


def _service_wait(url, process, settings):
    for _ in range(settings.POLL_RETRIES):
        if _service_wait_iteration(url, process, settings):
            return True
    raise RuntimeError('service daemon is not ready')


def _service_wait_iteration(url, process, settings):
    if process.poll() is not None:
        raise RuntimeError('service daemon is not running')
    try:
        response = requests.get(url, timeout=settings.PING_REQUEST_TIMEOUT)
        if response.status_code == 200:
            return True
    except requests.exceptions.Timeout:
        return False  # skip sleep as we've waited enough
    except requests.exceptions.ConnectionError:
        pass
    time.sleep(0.05)
    return False


def _prepare_env(env):
    result_env = os.environ.copy()
    if env is not None:
        result_env.update(env)
    asan_preload = os.getenv('ASAN_PRELOAD')
    if asan_preload is not None:
        result_env['LD_PRELOAD'] = asan_preload
    return result_env


@contextlib.contextmanager
def _service_daemon(args, check_url, settings, subprocess_options=None):
    options = subprocess_options or {}
    options['env'] = _prepare_env(options.get('env'))
    with spawn.spawned(
            settings.BASE_COMMAND + args,
            graceful_shutdown=settings.GRACEFUL_SHUTDOWN,
            **options,
    ) as process:
        _service_wait(check_url, process, settings)
        yield process


@contextlib.contextmanager
def start(args, check_url, settings=None, subprocess_options=None):
    if settings is None:
        settings = ServiceSettings()
    with _service_daemon(
            args, check_url, settings, subprocess_options=subprocess_options,
    ) as process:
        yield process


@contextlib.contextmanager
def service_wait(args, check_url, *, reporter, settings=None):
    if settings is None:
        settings = ServiceSettings()
    process = _DummyProcess()
    if not _service_wait_iteration(check_url, process, settings):
        command = ' '.join(settings.BASE_COMMAND + args)
        reporter.write_line('')
        reporter.write_line(
            'Service is not running yet you may want to start it from outside '
            'of testsuite, e.g. using gdb:',
            yellow=True,
        )
        reporter.write_line('')
        reporter.write_line('gdb --args {}'.format(command), green=True)
        reporter.write_line('')
        reporter.write('Waiting for service to start...')
        while not _service_wait_iteration(check_url, process, settings):
            reporter.write('.')
        reporter.write_line('')
    yield _DummyProcess()


@contextlib.contextmanager
def start_dummy_process():
    yield _DummyProcess()
