import pytest

from taxi_tests.environment import control

# pylint: disable=protected-access


@pytest.fixture(scope='session')
def ensure_service_started(request):
    taxi_env = request.session._taxi_env

    def _ensure_service_started(service_name, **kwargs):
        if taxi_env:
            taxi_env.ensure_started(service_name, **kwargs)

    return _ensure_service_started


def pytest_addoption(parser):
    group = parser.getgroup('env', 'Testsuite environment')
    group.addoption(
        '--no-env',
        action='store_true',
        dest='no_env',
        help='Disable environment initialization.',
    )


def pytest_sessionstart(session):
    if session.config.option.no_env:
        session._taxi_env = None
        return

    session._taxi_env = _create_taxi_env(session)


def pytest_sessionfinish(session):
    if session._taxi_env:
        session._taxi_env.close()


def _create_taxi_env(session):
    build_dir = session.config.getoption('--build-dir')
    worker_id = 'master'
    if hasattr(session.config, 'workerinput'):
        worker_id = session.config.workerinput['workerid']
    elif session.config.pluginmanager.getplugin('dsession'):
        return None

    return control.TestsuiteEnvironment(
        worker_id=worker_id, build_dir=build_dir,
    )
