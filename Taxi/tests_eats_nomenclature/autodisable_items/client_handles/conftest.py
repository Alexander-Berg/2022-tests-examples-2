import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
from eats_nomenclature_plugins import *  # noqa: F403 F401


@pytest.fixture(name='enable_get_disable_info_via_service')
def _enable_get_disable_info_via_service(update_taxi_config):
    def do_work():
        update_taxi_config(
            'EATS_NOMENCLATURE_PRODUCTS_AUTODISABLE_SETTINGS',
            {'should_get_data_from_erpa': True},
        )

    return do_work
