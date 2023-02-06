# pylint: skip-file
# flake8: noqa
import os
import pathlib
import sys

import pytest

from taxi_testsuite.plugins import api_coverage

from tests_plugins import userver_client
from testsuite.utils import approx

try:
    import library.python.resource
    import yatest.common
    IS_ARCADIA = True
except ImportError:
    IS_ARCADIA = False

USERVER_BASEURL = 'http://localhost:1180/'
USERVER_BASEURL_MONITOR = 'http://localhost:1188/'


@pytest.fixture(scope='session')
def schema_endpoints():
    return [
        api_coverage.SchemaEndpoint(
            http_path='/v1/run',
            http_method='POST',
            path_params=[
                api_coverage.PathParam(
                    name=name, type_param=type_, value_enum=value_enum,
                )
                for name, type_, value_enum in []
            ],
            status_code=200,
            content_type='',
        ),
        api_coverage.SchemaEndpoint(
            http_path='/v1/run',
            http_method='POST',
            path_params=[
                api_coverage.PathParam(
                    name=name, type_param=type_, value_enum=value_enum,
                )
                for name, type_, value_enum in []
            ],
            status_code=400,
            content_type='',
        ),
        api_coverage.SchemaEndpoint(
            http_path='/openapi/v1/run',
            http_method='POST',
            path_params=[
                api_coverage.PathParam(
                    name=name, type_param=type_, value_enum=value_enum,
                )
                for name, type_, value_enum in []
            ],
            status_code=200,
            content_type='application/json',
        ),
        api_coverage.SchemaEndpoint(
            http_path='/openapi/v1/run',
            http_method='POST',
            path_params=[
                api_coverage.PathParam(
                    name=name, type_param=type_, value_enum=value_enum,
                )
                for name, type_, value_enum in []
            ],
            status_code=400,
            content_type='application/json',
        ),
    ]


@pytest.fixture(scope='session')
def uservice_daemon_factory_test_service(
        register_daemon_scope, userver_service_spawner, regenerate_config,
        testsuite_build_dir, service_build_dir,
        secdist_service_generate,
):

    if IS_ARCADIA:
        service_binary_path = yatest.common.binary_path(
            'taxi/uservices/services/test-service/yandex-taxi-test-service',
        )
    else:
        service_binary_path = service_build_dir / 'yandex-taxi-test-service'

    configs_dir = testsuite_build_dir / 'configs'

    def factory(suffix='session', config_hooks=(), local_request=None):
        args = [
            str(service_binary_path),
            '-c',
            regenerate_config(
                configs_dir,
                suffix=suffix,
                hooks=config_hooks,
                local_request=local_request,
            ),
        ]
        return register_daemon_scope(
                name=f'yandex-taxi-{suffix}-test-service',
                spawn=userver_service_spawner(
                    args, ping_url=USERVER_BASEURL + 'ping',
                ),
        )

    return factory


@pytest.fixture(scope='session')
async def uservice_session_daemon_test_service(
        uservice_daemon_factory_test_service
):
    async with uservice_daemon_factory_test_service() as scope:
        yield scope


@pytest.fixture
async def uservice_daemon_test_service(
        uservice_session_daemon_test_service,
        uservice_daemon_factory_test_service,
        request,
):
    uservice_oneshot = request.node.get_closest_marker('uservice_oneshot')
    if uservice_oneshot:
        config_hooks = list(uservice_oneshot.kwargs.get('config_hooks', ()))
        config_hooks.append('disable_first_update_hook')
        async with uservice_daemon_factory_test_service(
                suffix='oneshot',
                config_hooks=config_hooks,
                local_request=request,
        ) as scope:
            yield scope
    else:
        yield uservice_session_daemon_test_service


@pytest.fixture(scope='session')
def periodic_tasks_state_test_service():
    return userver_client.PeriodicTasksState()


@pytest.fixture(scope='session')
def library_paths(get_source_path, testsuite_build_dir):
    paths = [
      get_source_path("libraries/codegen/testsuite/static/default"),
      get_source_path("libraries/codegen/testsuite"),
      get_source_path("libraries/codegen-clients/testsuite/static/default"),
      get_source_path("libraries/codegen-clients/testsuite"),
      get_source_path("libraries/segmented-dict/testsuite/static/default"),
      get_source_path("libraries/segmented-dict/testsuite"),
      get_source_path("libraries/set-rules-matcher/testsuite/static/default"),
      get_source_path("libraries/set-rules-matcher/testsuite"),
      get_source_path("libraries/solomon-stats/testsuite/static/default"),
      get_source_path("libraries/solomon-stats/testsuite"),
    ]
    if IS_ARCADIA:
        merged_taxi_config = library.python.resource.find(
            'testsuite:merged_taxi_config.json',
        )
        merged_taxi_config_path = pathlib.Path(
            testsuite_build_dir,
            'taxi_config',
            'config.json',
        )
        merged_taxi_config_path.parent.mkdir(parents=True, exist_ok=True)
        merged_taxi_config_path.write_bytes(merged_taxi_config)
        paths.append(merged_taxi_config_path.parent)
    else:
        paths.append(get_source_path("build/services/test-service/testsuite/taxi_config"))
    return paths


@pytest.fixture
async def taxi_test_service_aiohttp(
        request, taxi_config, mocked_time, ensure_daemon_started,
        uservice_daemon_test_service,
        periodic_tasks_state_test_service,
        service_client_default_headers,
        service_client_options, testpoint, testpoint_control, mockserver,
        disabled_first_update_caches, cleanup_userver_dumps,
        userver_log_capture,
        statistics,
):
    await ensure_daemon_started(uservice_daemon_test_service)

    # To avoid leaking dumps created during service startup into the first
    # test, dumps must be cleaned before each test, but after the service
    # has started.
    cleanup_userver_dumps()

    headers = {
        **service_client_default_headers,
        mockserver.trace_id_header: mockserver.trace_id,
    }
    client = userver_client.AiohttpClient(
        USERVER_BASEURL,
        periodic_tasks_state_test_service,
        mocked_time=mocked_time,
        testpoint=testpoint,
        testpoint_control=testpoint_control,
        headers=headers,
        cache_blocklist=disabled_first_update_caches,
        log_capture_fixture=userver_log_capture,
        **service_client_options,
    )
    marker = request.node.get_closest_marker('suspend_periodic_tasks')
    tasks_to_suspend = marker and marker.args or ()
    await client.suspend_periodic_tasks(tasks_to_suspend)
    try:
        yield client
    finally:
        await client.resume_all_periodic_tasks()


@pytest.fixture
def is_api_coverage_enabled():
    return False


@pytest.fixture
def taxi_test_service(
        taxi_test_service_aiohttp
):
    return userver_client.Client(
        taxi_test_service_aiohttp,
    )


@pytest.fixture
def taxi_test_service_monitor_aiohttp(
        taxi_test_service,
        service_client_default_headers,
        service_monitor_client_options, mockserver,
):
    headers = {
        **service_client_default_headers,
        mockserver.trace_id_header: mockserver.trace_id,
    }
    client = userver_client.AiohttpClientMonitor(
        USERVER_BASEURL_MONITOR,
        headers=headers,
        **service_monitor_client_options,
    )
    yield client


@pytest.fixture
def taxi_test_service_monitor(
        taxi_test_service_monitor_aiohttp
):
    return userver_client.ClientMonitor(
        taxi_test_service_monitor_aiohttp,
    )


@pytest.fixture(scope='session')
def service_build_dir(build_dir):
    return pathlib.Path(build_dir) / 'services/test-service'


@pytest.fixture(scope='session')
def service_source_dir(get_source_path):
    return get_source_path('services/test-service')


@pytest.fixture(scope='session')
def testsuite_build_dir(service_build_dir):
    if IS_ARCADIA:
        working_dir = pathlib.Path(yatest.common.work_path())
    else:
        working_dir = service_build_dir
    return working_dir / 'testsuite'


@pytest.fixture(scope='session')
def testsuite_source_dir(service_source_dir):
    return service_source_dir / 'testsuite'


@pytest.fixture(scope='session')
def load_json_defaults():
    return {'parse_float': approx.Float}


@pytest.fixture(scope='session')
def api_coverage_non_decreasing():
    return False
