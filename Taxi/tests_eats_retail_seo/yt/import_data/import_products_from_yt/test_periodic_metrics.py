import pytest

from . import constants


@pytest.mark.yt(
    schemas=['yt_products_schema.yaml'],
    static_table_data=['yt_products_data_for_periodic_metrics.yaml'],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_periodic_metrics(
        add_common_data,
        enable_periodic_in_config,
        verify_periodic_metrics,
        yt_apply,
):
    enable_periodic_in_config(constants.PERIODIC_NAME)
    add_common_data()

    await verify_periodic_metrics(constants.PERIODIC_NAME, is_distlock=True)
