import pytest

from taxi_tests.environment.services import nginx


@pytest.fixture(scope='session')
def nginx_service(request, ensure_service_started, nginx_port):
    if not request.config.getoption('--no-nginx'):
        ensure_service_started('nginx', port=nginx_port)


@pytest.fixture(scope='session')
def nginx_port(worker_id, get_free_port):
    if worker_id == 'master':
        return nginx.DEFAULT_PORT
    return get_free_port()


def pytest_addoption(parser):
    group = parser.getgroup('nginx')
    group.addoption(
        '--no-nginx', help='Disable nginx startup', action='store_true',
    )
