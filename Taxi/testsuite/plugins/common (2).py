import getpass
import json
import pathlib
import time

import pytest

from testsuite.databases.pgsql import discover


@pytest.fixture
def config_service_defaults(load_json):
    return load_json('config-defaults.json')


def pytest_addoption(parser):
    group = parser.getgroup('Example service')
    group.addoption(
        '--service-port',
        help='Bind example services to this port (default is %(default)s)',
        default=8000,
        type=int,
    )


@pytest.fixture(scope='session')
def pgsql_local(pgsql_local_create, logistic_dispatcher_dir):
    databases = discover.find_schemas(
        'ld', [logistic_dispatcher_dir.joinpath('database/pgmigrate')],
    )
    return pgsql_local_create(list(databases.values()))


@pytest.fixture(scope='session')
def secdist_path(
        tmp_path_factory, logistic_dispatcher_dir, pgsql_local, is_arcadia,
):
    secdist = json.loads(
        logistic_dispatcher_dir.joinpath('testsuite/secdist.json').read_text(),
    )
    secdist['postgresql_settings']['databases']['logistic_dispatcher'][0][
        'hosts'
    ] = [pgsql_local['ld'].get_dsn()]

    if is_arcadia:
        secdist_path = tmp_path_factory.mktemp('service').joinpath(
            'secdist.json',
        )
    else:
        secdist_path = pathlib.Path(
            f'/tmp/ld-secdist-{getpass.getuser()}.json',
        )
    secdist_path.write_text(json.dumps(secdist))
    return str(secdist_path)


@pytest.fixture
async def run_watchers(rt_robot_execute):
    await rt_robot_execute('employer_factors_watcher')
    time.sleep(1)
