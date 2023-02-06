import pytest

from . import constants
from .... import models


@pytest.mark.yt(
    schemas=[
        'yt_categories_schema.yaml',
        'yt_categories_relations_schema.yaml',
    ],
    static_table_data=[
        'yt_categories_data_for_errors.yaml',
        'yt_categories_relations_data_for_errors.yaml',
    ],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_exceed_max_skipped_batches(
        add_common_data,
        assert_objects_lists,
        enable_periodic_in_config,
        get_categories_from_db,
        get_product_types_from_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
):
    @testpoint('categories-importer-finished')
    def categories_import_finished(param):
        pass

    @testpoint('categories-relations-importer-finished')
    def categories_relations_import_finished(param):  # pylint: disable=C0103
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

    assert_objects_lists(get_product_types_from_db(), [])
    assert_objects_lists(get_categories_from_db(), [])

    assert batch_read_table_failed.has_calls
    assert batch_read_table_retries.times_called == max_retries_count

    assert not categories_import_finished.has_calls
    assert not categories_relations_import_finished.has_calls
    assert not periodic_finished.has_calls


@pytest.mark.parametrize(
    'categories_path, categories_relations_path',
    [
        pytest.param(None, None, id='no_path'),
        pytest.param(
            '//nmn_yt/some_path',
            '//nmn_yt/some_path2',
            id='path_without_table',
        ),
    ],
)
@pytest.mark.yt(
    schemas=[
        'yt_categories_schema.yaml',
        'yt_categories_relations_schema.yaml',
    ],
    static_table_data=[
        'yt_categories_data_for_errors.yaml',
        'yt_categories_relations_data_for_errors.yaml',
    ],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_no_snapshot_tables(
        add_brand,
        assert_objects_lists,
        enable_periodic_in_config,
        get_categories_from_db,
        get_product_types_from_db,
        save_snapshot_tables_to_db,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
        # parametrize params
        categories_path,
        categories_relations_path,
):
    @testpoint('categories-importer-finished')
    def categories_import_finished(param):
        pass

    @testpoint('categories-relations-importer-finished')
    def categories_relations_import_finished(param):  # pylint: disable=C0103
        pass

    @testpoint(constants.PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(constants.PERIODIC_NAME)
    add_brand()

    if categories_path:
        save_snapshot_tables_to_db(
            [
                models.SnapshotTable(
                    table_id=constants.SNAPSHOT_CATEGORIES_TABLE_ID,
                    table_path=categories_path,
                ),
            ],
        )
    if categories_relations_path:
        save_snapshot_tables_to_db(
            [
                models.SnapshotTable(
                    table_id=constants.SNAPSHOT_CATEGORIES_RELATIONS_TABLE_ID,
                    table_path=categories_relations_path,
                ),
            ],
        )

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    assert_objects_lists(get_product_types_from_db(), [])
    assert_objects_lists(get_categories_from_db(), [])

    assert not categories_import_finished.has_calls
    assert not categories_relations_import_finished.has_calls
    assert not periodic_finished.has_calls
