import copy

from psycopg2 import extras
import pytest


# root conftest for service eats-retail-seo
pytest_plugins = ['eats_retail_seo_plugins.pytest_plugins']


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_retail_seo'].cursor()


@pytest.fixture
def pg_realdict_cursor(pgsql):
    return pgsql['eats_retail_seo'].cursor(
        cursor_factory=extras.RealDictCursor,
    )


@pytest.fixture
def component_config(testsuite_build_dir, load_yaml):
    class ComponentConfig:
        @staticmethod
        def get(component_name, var_path):
            config_path = testsuite_build_dir.joinpath('configs/service.yaml')
            config = load_yaml(config_path)
            config_vars = load_yaml(config['config_vars'])
            component_section = config['components_manager']['components'][
                component_name
            ]
            cur_path = component_section
            for var in var_path:
                cur_path = cur_path[var]

            return config_vars[cur_path[1:]]

    return ComponentConfig()


@pytest.fixture
def update_taxi_config(taxi_config):
    """
    Updates only specified keys in the config, without touching other keys.
    E.g. if original config is `{ a: 1, b: 2}`, then value `{ b: 3, c: 4}`
    will set the config to `{ a: 1, b: 3, c: 4}`.
    """

    def impl(config_name, config_value):
        updated_config = copy.deepcopy(taxi_config.get(config_name))
        updated_config.update(config_value)
        taxi_config.set(**{config_name: updated_config})

    return impl
