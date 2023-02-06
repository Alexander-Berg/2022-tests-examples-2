import signal

import pytest

from testsuite.daemons import service_client
from testsuite.daemons import spawn
from testsuite.utils import net

try:
    import yatest
except ImportError:
    yatest = None


class BaseError(Exception):
    pass


class RTJobFailed(BaseError):
    pass


LD_SERVICES_RETRIES = 3

if yatest:
    extra_plugins = ['plugins.arcadia']
else:
    extra_plugins = ['plugins.direct']

pytest_plugins = [
    'testsuite.pytest_plugin',
    'testsuite.databases.pgsql.pytest_plugin',
    'taxi_testsuite.plugins.config',
    'taxi_testsuite.plugins.experiments3',
    'taxi_testsuite.plugins.mocks.configs_service',
    'plugins.common',
    'plugins.fixtures',
    'plugins.mocks',
    *extra_plugins,
]


@pytest.fixture
def mockserver_client(
        mockserver, service_client_default_headers, service_client_options,
) -> service_client.Client:
    return service_client.Client(
        mockserver.base_url,
        headers={
            **service_client_default_headers,
            mockserver.trace_id_header: mockserver.trace_id,
        },
        **service_client_options,
    )


@pytest.fixture
async def logistic_platform(
        ensure_daemon_started,
        # Service process holder
        _service_scope,
        # Service dependencies
        mockserver,
        pgsql,
        basic_mocks,
        testpoint,
):
    await basic_mocks()

    # Start service if not started yet
    for _ in range(LD_SERVICES_RETRIES):
        try:
            await ensure_daemon_started(_service_scope)
        except spawn.ExitCodeError:
            continue
        return
    await ensure_daemon_started(_service_scope)


@pytest.fixture
async def logistic_platform_client(
        create_service_client, _service_baseurl, logistic_platform,
):
    # Create service client instance
    return create_service_client(_service_baseurl)


@pytest.fixture(scope='session')
def service_port(pytestconfig, is_arcadia):
    if not is_arcadia and pytestconfig.option.service_port:
        return pytestconfig.option.service_port
    socket = net.bind_socket()
    port = socket.getsockname()[1]
    socket.close()
    return port


@pytest.fixture(scope='session')
def _service_baseurl(pytestconfig, service_port):
    return f'http://localhost:{service_port}/'


# TODO: must be session for perfomace reasons please fix
@pytest.fixture
async def _service_scope(
        pytestconfig,
        create_daemon_scope,
        mockserver_info,
        _service_baseurl,
        pgsql_local,
        logistic_platform_dir,
        logistic_platform_binary,
        secdist_path,
        service_port,
):
    config_path = str(
        logistic_platform_dir.joinpath(
            'platform/configs/config_testsuite',
        ),
    )

    async with create_daemon_scope(
            args=[
                logistic_platform_binary,
                config_path,
                '-V',
                'LogDir=logs/taxi-logistic-platform',
                '-V',
                f'BasePort={service_port}',
                '-V',
                'ControllerPort=0',
                '-V',
                'HomeDir=/work',
                '-V',
                f'MockserverPort={mockserver_info.port}',
                '-V',
                f'MockserverHost={mockserver_info.host}',
                '--secdist',
                secdist_path,
                '--secdist-service',
                'logistic-platform',
            ],
            ping_url=_service_baseurl + 'ping',
            shutdown_signal=signal.SIGQUIT,
    ) as scope:
        yield scope


@pytest.fixture
def config_service_defaults(load_json):
    return load_json('config-defaults.json')


@pytest.fixture
def rt_robot_execute(logistic_platform_client):
    async def execute(job_name):
        response = await logistic_platform_client.post(
            'testsuite/rt-robot-execute', json={'robot_name': job_name},
        )
        if response.status_code != 200:
            raise RTJobFailed(response.content)

    return execute


@pytest.fixture(name='load_json_var')
def _load_json_var(load_json):
    def load_json_var(path, **variables):
        def var_hook(obj):
            varname = obj['$var']
            return variables[varname]

        return load_json(path, object_hook={'$var': var_hook})

    return load_json_var
