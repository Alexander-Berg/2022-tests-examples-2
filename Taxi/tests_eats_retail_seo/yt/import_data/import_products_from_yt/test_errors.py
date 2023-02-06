import pytest

from . import constants
from .... import models


@pytest.mark.yt(
    schemas=['yt_products_schema.yaml'],
    static_table_data=['yt_products_data_for_errors.yaml'],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_exceed_max_skipped_batches(
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
        update_taxi_config,
        yt_apply,
):
    @testpoint('products-importer-finished')
    def products_import_finished(param):
        pass

    @testpoint(constants.PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    @testpoint('BatchReadTable::fail')
    def batch_read_table_failed(param):
        return {'inject_failure': True, 'failure_at_row': 0}

    @testpoint('ProcessWithRetries::retry')
    def batch_read_table_retries(param):
        pass

    enable_periodic_in_config(constants.PERIODIC_NAME)
    add_common_data()

    max_retries_count = 2
    max_skipped_batches_count = 0
    update_taxi_config(
        'EATS_RETAIL_SEO_YT_SETTINGS',
        {
            constants.PERIODIC_NAME: {
                'lookup_batch_size': 2,
                'batch_max_retries_count': max_retries_count,
                'batch_delay_between_retries': 100,
                'max_skipped_batches_count': max_skipped_batches_count,
                'max_total_batches_count': 20,
            },
        },
    )

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    assert_objects_lists(get_barcodes_from_db(), [])
    assert_objects_lists(get_pictures_from_db(), [])
    assert_objects_lists(get_product_types_from_db(), [])
    assert_objects_lists(get_product_brands_from_db(), [])
    assert_objects_lists(get_products_from_db(), [])

    assert batch_read_table_failed.has_calls
    assert batch_read_table_retries.times_called == max_retries_count

    assert not products_import_finished.has_calls
    assert not periodic_finished.has_calls


@pytest.mark.parametrize(
    'products_path',
    [
        pytest.param(None, id='no_path'),
        pytest.param('//nmn_yt/some_path', id='path_without_table'),
    ],
)
@pytest.mark.yt(
    schemas=['yt_products_schema.yaml'],
    static_table_data=['yt_products_data_for_errors.yaml'],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_no_snapshot_tables(
        add_brand,
        assert_objects_lists,
        enable_periodic_in_config,
        get_barcodes_from_db,
        get_pictures_from_db,
        get_product_types_from_db,
        get_product_brands_from_db,
        get_products_from_db,
        save_snapshot_tables_to_db,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
        # parametrize params
        products_path,
):
    @testpoint('products-importer-finished')
    def products_import_finished(param):
        pass

    @testpoint(constants.PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(constants.PERIODIC_NAME)
    add_brand()

    if products_path:
        snapshot_table = models.SnapshotTable(
            table_id=constants.SNAPSHOT_PRODUCTS_TABLE_ID,
            table_path=products_path,
        )
        save_snapshot_tables_to_db([snapshot_table])

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    assert_objects_lists(get_barcodes_from_db(), [])
    assert_objects_lists(get_pictures_from_db(), [])
    assert_objects_lists(get_product_types_from_db(), [])
    assert_objects_lists(get_product_brands_from_db(), [])
    assert_objects_lists(get_products_from_db(), [])

    assert not products_import_finished.has_calls
    assert not periodic_finished.has_calls
