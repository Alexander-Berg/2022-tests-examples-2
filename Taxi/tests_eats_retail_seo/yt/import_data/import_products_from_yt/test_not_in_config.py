import pytest

from . import constants


@pytest.mark.yt(
    schemas=['yt_products_schema.yaml'],
    static_table_data=['yt_products_data_for_not_in_config.yaml'],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE={
        'master_tree_settings': {
            '999': {'assortment_name': 'some_assortment'},
        },
    },
)
async def test_brand_not_in_config(
        add_common_data,
        assert_objects_lists,
        enable_periodic_in_config,
        get_barcodes_from_db,
        get_pictures_from_db,
        get_product_types_from_db,
        get_product_brands_from_db,
        get_products_from_db,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
):
    @testpoint('products-importer-finished')
    def products_import_finished(param):
        pass

    @testpoint(constants.PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(constants.PERIODIC_NAME)
    add_common_data()

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    assert_objects_lists(get_barcodes_from_db(), [])
    assert_objects_lists(get_pictures_from_db(), [])
    assert_objects_lists(get_product_types_from_db(), [])
    assert_objects_lists(get_product_brands_from_db(), [])
    assert_objects_lists(get_products_from_db(), [])

    assert products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1
