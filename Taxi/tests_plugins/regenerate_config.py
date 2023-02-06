# pylint: disable=redefined-outer-name

import itertools
import pathlib
import types

import pytest
import yaml

try:
    import yatest.common
    import library.python.resource
    IS_ARCADIA = True
except ImportError:
    IS_ARCADIA = False


USERVER_CONFIG_HOOKS = [
    '_userver_config_http_client',
    '_userver_config_testsuite_support',
    '_userver_config_clear_fs_cache',
    '_userver_config_testsuite_tasks',
]


class UserverConfigPlugin:
    def __init__(self):
        self._config_hooks = []

    @property
    def userver_config_hooks(self):
        return self._config_hooks

    def pytest_plugin_registered(self, plugin, manager):
        if not isinstance(plugin, types.ModuleType):
            return
        uhooks = getattr(plugin, 'USERVER_CONFIG_HOOKS', None)
        if uhooks is not None:
            self._config_hooks.extend(uhooks)


def pytest_configure(config):
    config.pluginmanager.register(UserverConfigPlugin(), 'userver_config')


@pytest.fixture(scope='session')
def regenerate_config(
        request,
        worker_id,
        mockserver_info,
        pytestconfig,
        mockserver_ssl_info,
        service_source_dir,
):
    plugin = pytestconfig.pluginmanager.get_plugin('userver_config')

    def write_config(
            path: pathlib.Path, doc: dict, suffix: str,
    ) -> pathlib.Path:
        modified_path = path.parent.joinpath(
            f'{path.stem}_{worker_id}-{suffix}{path.suffix}',
        )
        with modified_path.open('w', encoding='utf-8') as fp:
            yaml.safe_dump(doc, fp, default_flow_style=False)
        return modified_path

    def load_yaml_config(content: str):
        if mockserver_ssl_info:
            content = content.replace(
                '$mockserver_https',
                _strip_trailing_separator(mockserver_ssl_info.base_url),
            )
        content = content.replace(
            '$mockserver', _strip_trailing_separator(mockserver_info.base_url),
        )
        content = content.replace(
            '$service_source_dir', str(service_source_dir),
        )

        if IS_ARCADIA:
            content = content.replace(
                '$test_build_dir', yatest.common.build_path(),
            )
            content = content.replace(
                '$test_work_dir', yatest.common.work_path(),
            )

        return yaml.safe_load(content)

    def build_config(
            testsuite_configs_dir: pathlib.Path,
            *,
            suffix='session',
            hooks=(),
            local_request=None,
            unit_name=None,
    ):
        local_request = local_request or request

        config_path = pathlib.Path(testsuite_configs_dir, 'service.yaml')

        if IS_ARCADIA:
            if unit_name:
                service_yaml_resource = (
                    f'testsuite:units/{unit_name}/service.yaml'
                )
                config_vars_yaml_resource = (
                    f'testsuite:units/{unit_name}/config_vars.testsuite.yaml'
                )
            else:
                service_yaml_resource = 'testsuite:service.yaml'
                config_vars_yaml_resource = (
                    'testsuite:config_vars.testsuite.yaml'
                )

            # pylint: disable=no-member
            testsuite_configs_dir.mkdir(parents=True, exist_ok=True)
            config_data = library.python.resource.find(service_yaml_resource)
            config = load_yaml_config(config_data.decode())
            # Tier0 tests pack generated config files into test resources,
            # but some test fixtures still access them from disk.
            # We will write those configs back to their respective locations
            # in the current test working dir
            # TODO(TAXITOOLS-5057): refactor mentioned fixtures
            #  so this is no longer necessary
            config_path.write_bytes(config_data)

            config_vars = load_yaml_config(
                library.python.resource.find(
                    config_vars_yaml_resource,
                ).decode(),
            )
            config_vars_path = testsuite_configs_dir / 'config_vars.yaml'

            components = config['components_manager']['components']

            if 'secdist' in components:
                secdist_path = testsuite_configs_dir / 'secdist.json'
                components['secdist']['config'] = str(secdist_path)

            components['dynamic-config']['fs-cache-path'] = str(
                testsuite_configs_dir / 'config_cache.json',
            )

            client_updater = components['dynamic-config-client-updater']
            fallback_path = testsuite_configs_dir / 'taxi_config_fallback.json'
            fallback_path.write_bytes(
                library.python.resource.find(
                    'testsuite:taxi_config_fallback.json',
                ),
            )
            client_updater['fallback-path'] = str(fallback_path)

            if 'configs-from-configs3-updater' in components:
                components['configs-from-configs3-updater'][
                    'fallback-path'
                ] = str(fallback_path)

        else:
            config = load_yaml_config(config_path.read_text())
            if 'config_vars' not in config:
                raise RuntimeError(f'No config_vars section in {config_path}')
            config_vars_path = pathlib.Path(config['config_vars'])
            config_vars = load_yaml_config(config_vars_path.read_text())

        for hook in itertools.chain(plugin.userver_config_hooks, hooks):
            if not callable(hook):
                hook_func = local_request.getfixturevalue(hook)
            else:
                hook_func = hook
            hook_func(config, config_vars)

        config['config_vars'] = str(
            write_config(config_vars_path, config_vars, suffix=suffix),
        )
        return str(write_config(config_path, config, suffix=suffix))

    return build_config


@pytest.fixture(scope='session')
def _userver_config_http_client(mockserver_info, mockserver_ssl_info):
    def patch_config(config, config_vars):
        http_client = config['components_manager']['components']['http-client']
        if http_client is None:
            http_client = {}
        http_client['testsuite-enabled'] = True
        http_client['testsuite-timeout'] = '10s'
        allowed_urls = [
            mockserver_info.base_url,
            'http://localhost:1180/echo',
            # requests to UNIX sockets do not specify ports in the URL
            'http://localhost/echo',
        ]
        if mockserver_ssl_info:
            allowed_urls.append(mockserver_ssl_info.base_url)
        http_client['testsuite-allowed-url-prefixes'] = allowed_urls
        config['components_manager']['components']['http-client'] = http_client

    return patch_config


@pytest.fixture(scope='session')
def _userver_config_testsuite_support(pytestconfig, userver_dumps_root):
    def _set_postgresql_options(testsuite_support: dict) -> None:
        testsuite_support['testsuite-pg-execute-timeout'] = '15s'
        testsuite_support['testsuite-pg-statement-timeout'] = '10s'
        testsuite_support['testsuite-pg-readonly-master-expected'] = True

    def _set_redis_timeout(testsuite_support: dict) -> None:
        testsuite_support['testsuite-redis-timeout-connect'] = '20s'
        testsuite_support['testsuite-redis-timeout-single'] = '10s'
        testsuite_support['testsuite-redis-timeout-all'] = '10s'

    def _disable_cache_periodic_update(testsuite_support: dict) -> None:
        testsuite_support['testsuite-periodic-update-enabled'] = False

    def _set_userver_dumps_root(config_vars: dict) -> None:
        config_vars['userver-dumps-root'] = str(userver_dumps_root)

    def patch_config(config, config_vars) -> None:
        config_vars['logger_level'] = (
            pytestconfig.option.service_log_level
        ) or config_vars.get('logger_level', 'debug')
        _set_userver_dumps_root(config_vars)
        components: dict = config['components_manager']['components']
        if 'testsuite-support' not in components:
            return
        testsuite_support = components['testsuite-support'] or {}
        _set_postgresql_options(testsuite_support)
        _set_redis_timeout(testsuite_support)
        if not pytestconfig.getoption('--service-runner-mode', False):
            _disable_cache_periodic_update(testsuite_support)
        components['testsuite-support'] = testsuite_support

    return patch_config


# 'dynamic-config' component caches config in a file.
# We need to clear it, otherwise the service will make first http requests
# using $mockserver url from previous test session
@pytest.fixture(scope='session')
def _userver_config_clear_fs_cache():
    def clear_caches(config, config_vars):
        cache_file_path = (
            config.get('components_manager', {})
            .get('components', {})
            .get('dynamic-config', {})
            .get('fs-cache-path', None)
        )
        if cache_file_path is not None:
            path = pathlib.Path(cache_file_path)
            if path.is_file():
                path.unlink()

    return clear_caches


@pytest.fixture(scope='session')
def _userver_config_testsuite_tasks(pytestconfig):
    def patch_config(config, config_vars) -> None:
        if (
                hasattr(pytestconfig.option, 'service_runner_mode')
                and pytestconfig.option.service_runner_mode
        ):
            config_vars['testsuite-tasks-enabled'] = False

    return patch_config


def _strip_trailing_separator(url: str) -> str:
    if url.endswith('/'):
        return url[:-1]
    return url
