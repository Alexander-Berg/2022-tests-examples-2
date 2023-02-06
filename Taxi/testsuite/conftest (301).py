# pylint: disable=too-many-lines
import copy

from psycopg2 import extras
import pytest


# root conftest for service eats-retail-products-autodisable
pytest_plugins = ['eats_retail_products_autodisable_plugins.pytest_plugins']


@pytest.fixture
def pg_realdict_cursor(pgsql):
    return pgsql['eats_retail_products_autodisable'].cursor(
        cursor_factory=extras.RealDictCursor,
    )


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_retail_products_autodisable'].cursor()


@pytest.fixture
def update_taxi_config(taxi_config):
    """
    Updates only specified keys in the config, without touching other keys.
    E.g. if original config is `{ a: 1, b: 2}`, then value `{ b: 3, c: 4}`
    will set the config to `{ a: 1, b: 3, c: 4}`.
    """

    def _impl(config_name, config_value):
        updated_config = copy.deepcopy(taxi_config.get(config_name))
        updated_config.update(config_value)
        taxi_config.set(**{config_name: updated_config})

    return _impl
