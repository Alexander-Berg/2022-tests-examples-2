# pylint: disable=redefined-outer-name
import pathlib

import pytest

from . import service
from . import support


def pytest_addoption(parser):
    group = parser.getgroup('yt')
    group.addoption('--yt-proxy', help='Yt local proxy, e.g: localhost:8000')


def pytest_service_register(register_service):
    register_service('yt', service.create_service)


def pytest_configure(config):
    config.addinivalue_line('markers', 'yt: per-test yt-local initialization')


@pytest.fixture
def yt_apply(_yt_init):
    _yt_init()


@pytest.fixture
def yt_apply_force(_yt_init):
    _yt_init(force=True)


@pytest.fixture(scope='session')
def yt_service_schemas():
    return []


@pytest.fixture(scope='session')
def yt_proxy(yt_conninfo):
    return yt_conninfo.connection_string


@pytest.fixture
def yt_client(yt_proxy, _yt_service):
    import yt.wrapper.client
    return yt.wrapper.client.Yt(
        config={
            'api_version': 'v3',
            'proxy': {'url': yt_proxy, 'connect_timeout': 1.0},
        },
    )


@pytest.fixture(scope='session')
def yt_conninfo(pytestconfig, _yt_service_settings):
    if pytestconfig.option.yt_proxy:
        return service.parse_connection_info(pytestconfig.option.yt_proxy)
    return _yt_service_settings.get_conninfo()


@pytest.fixture
def _yt_service(pytestconfig, ensure_service_started, _yt_service_settings):
    if not pytestconfig.option.yt_proxy:
        ensure_service_started('yt', settings=_yt_service_settings)
    return True


@pytest.fixture(scope='session')
def _yt_service_settings():
    return service.get_service_settings()


@pytest.fixture(scope='session')
def _yt_service_state(yt_service_schemas):
    return support.YTServiceState(service_schemas=yt_service_schemas)


@pytest.fixture
def _yt_init(
        _yt_state: support.YtState,
        _yt_service_state: support.YTServiceState,
        yt_client,
):
    def _init(force=False):
        if not force and not _yt_service_state.initialized:
            _yt_service_state.initialized = True
            force = True
        _yt_state.initialize(yt_client, force=force)

    return _init


@pytest.fixture
def _yt_state(
        request, _yt_data_loader, _yt_service_state: support.YTServiceState,
):
    markers = list(request.node.iter_markers('yt'))
    table_schemas = []
    tables_dict = {}

    def _add_table(path, attributes):
        table = support.Table(path=path, attributes=attributes)
        if table.path in tables_dict:
            raise ValueError(
                f'Do not try to override table schema for {table.path!r}',
            )
        tables_dict[table.path] = table
        table_schemas.append(table)

    for schema_value in _yt_service_state.service_schemas:
        data = _yt_data_loader(schema_value, skip_check_prefix=True)
        for table_data in data:
            _add_table(**table_data)
    for marker in markers:
        for schema_value in marker.kwargs.get('schemas', ()):
            data = _yt_data_loader(schema_value)
            for table_data in data:
                _add_table(
                    path=table_data['path'],
                    attributes=table_data['attributes'],
                )

        for table_values, is_dyn_table in [
                (marker.kwargs.get('dyn_table_data', ()), True),
                (marker.kwargs.get('static_table_data', ()), False),
        ]:
            for table_value in table_values:
                tables_data = _yt_data_loader(table_value)
                for table_data in tables_data:
                    path = table_data['path']
                    if path not in tables_dict:
                        raise ValueError(
                            f'YT path is not initialized in "schemas": {path}',
                        )
                    if is_dyn_table and not tables_dict[path].dynamic:
                        raise ValueError(
                            f'YT table: {path} is not dynamic '
                            f'(set attributes->dynamic: true)',
                        )
                    elif not is_dyn_table and tables_dict[path].dynamic:
                        raise ValueError(
                            f'YT table: {path} is dynamic, '
                            f'but used static_table parameter',
                        )
                    tables_dict[path].initial_data.extend(table_data['values'])

    return support.YtState(support.Schema(table_schemas))


@pytest.fixture
def _yt_data_loader(load_yaml, load_json):
    def _loader(value, *, skip_check_prefix=False):
        if isinstance(value, (str, pathlib.Path)):
            value = str(value)
            if value.endswith('.yaml'):
                data = load_yaml(value)
            else:
                raise TypeError(f'Unsupported yt file extension: {value}')
            if not skip_check_prefix and not value.startswith('yt'):
                raise TypeError(
                    f'YT path should starts with "yt" prefix: {value}',
                )
        else:
            data = value
        if not isinstance(data, list):
            data = [data]
        return data

    return _loader
