import pytest
from taxi_linters import taxi_yamlfmt

from dashboards.internal.grafana.merger import config_merger
from dashboards.internal.models import configs as configs_models
from dashboards.internal.models import layouts as layouts_models


@pytest.fixture(name='make_file_name')
def _make_file_name():
    def _wrapper(name, folder=None):
        name = f'{name}.yaml'
        if folder:
            name = f'{folder}/{name}'
        return name

    return _wrapper


@pytest.fixture(name='load_raw_yaml_config')
def _load_raw_yaml_config(load, make_file_name):
    def _wrapper(name, folder=None):
        return load(make_file_name(name, folder))

    return _wrapper


@pytest.fixture(name='load_yaml_config')
def _load_yaml_config(load_raw_yaml_config):
    def _wrapper(name, folder=None):
        return taxi_yamlfmt.load(load_raw_yaml_config(name, folder))

    return _wrapper


@pytest.fixture(name='check_merge_configs')
def _check_merge_configs(load_yaml_config, load_raw_yaml_config):
    def _wrapper(
            *,
            current='current',
            remote='remote',
            expected='expected',
            previous_config=None,
            folder=None,
    ):
        current_data = load_yaml_config(current, folder)
        remote_data = load_yaml_config(remote, folder)
        expected_raw = load_raw_yaml_config(expected, folder)
        merger = config_merger.ConfigMerger(
            current_data, remote_data, previous_config,
        )
        merged_data = merger.merge()
        assert taxi_yamlfmt.dump(merged_data) == expected_raw

    return _wrapper


def test_layouts_merge_equal_configs(check_merge_configs):
    check_merge_configs(
        current='default_config',
        remote='default_config',
        expected='default_config',
    )


def test_add_layouts_merge(check_merge_configs):
    check_merge_configs(expected='current', folder='add_layouts')


def test_remote_layouts_merge(check_merge_configs):
    check_merge_configs(
        current='remote',
        remote='current',
        expected='current',
        folder='add_layouts',
    )


def test_layouts_parameters_merge(check_merge_configs):
    check_merge_configs(folder='parameters_merge')


def test_custom_geobus(check_merge_configs):
    check_merge_configs(folder='custom_geobus')


def test_add_new_key_from_yaml(check_merge_configs):
    check_merge_configs(folder='add_new_key_from_yaml')


def test_remove_layout(check_merge_configs):
    config = configs_models.BareConfig(
        dashboard_name='test_dashboard',
        dorblu_custom=None,
        handlers=[],
        layouts=[
            layouts_models.Layout('system', {}),
            layouts_models.Layout('rps_share', {}),
            layouts_models.Layout('http', {}),
            layouts_models.Layout('stq', {'queues': ['test_queue_1']}),
            layouts_models.Layout(
                'include',
                {
                    'variables': [],
                    'path': 'some_include_3',
                    'title': 'some_include_3',
                },
            ),
            layouts_models.Layout(
                'include',
                {
                    'variables': [],
                    'path': 'some_include_2',
                    'title': 'some_include_2',
                },
            ),
            layouts_models.Layout(
                'include',
                {
                    'variables': [],
                    'path': 'some_include_6',
                    'title': 'some_include_6',
                },
            ),
            layouts_models.Layout(
                'include',
                {
                    'variables': [],
                    'path': 'some_include_1',
                    'title': 'some_include_1',
                },
            ),
        ],
    )
    check_merge_configs(previous_config=config, folder='remove_layout')
