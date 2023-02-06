# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
import pytest

from eats_surge_resolver_plugins import *  # noqa: F403 F401


@pytest.fixture(name='pipeline_config', autouse=True)
def add_pipeline_experiment(experiments3):
    experiments3.add_config(
        name='eats_surge_resolver_pipeline',
        consumers=['eats-surge-resolver/main'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'pipeline_name': 'calc_surge_eats_2100m'},
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )
