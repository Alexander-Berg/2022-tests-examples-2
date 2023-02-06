import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_retail_products_autodisable_plugins import *  # noqa: F403 F401

from tests_eats_retail_products_autodisable.yt_autodisable import consts


# pylint: disable=W0102
@pytest.fixture(name='set_periodic_config')
def _set_periodic_config(taxi_config):
    def do_set_periodic_config(
            enabled_place_ids=[consts.PLACE_ID_1],
            enabled_algorithms=[consts.ALGORITHM_NAME_THRESHOLD],
            nomenclature_update_info_batch_size=None,
    ):
        yt_disable_settings_value = {
            'enabled_place_ids': enabled_place_ids,
            'yt_path_prefix': '//nomenclature_hide_info/',
            'enabled_algorithms': enabled_algorithms,
        }
        if nomenclature_update_info_batch_size is not None:
            yt_disable_settings_value[
                'nomenclature_update_info_batch_size'
            ] = nomenclature_update_info_batch_size

        taxi_config.set_values(
            {
                'EATS_RETAIL_PRODUCTS_AUTODISABLE_YT_AUTODISABLE_PRODUCTS_SETTINGS': (  # noqa: E501 pylint: disable=line-too-long
                    yt_disable_settings_value
                ),
                'EATS_RETAIL_PRODUCTS_AUTODISABLE_PERIODICS': {
                    '__default__': {'is_enabled': True, 'period_in_sec': 60},
                },
            },
        )

    return do_set_periodic_config
