import datetime as dt

import pytest
import pytz

from . import constants
from .... import models


MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=[
        'yt_categories_schema.yaml',
        'yt_categories_relations_schema.yaml',
    ],
    static_table_data=[
        'yt_categories_data_for_retries.yaml',
        'yt_categories_relations_data_for_retries.yaml',
    ],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_retries(
        add_common_data,
        assert_objects_lists,
        enable_periodic_in_config,
        get_categories_from_db,
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

    # первый батч будет пропущен из-за ошибки,
    # будет обработан только второй
    max_retries_count = 2
    update_taxi_config(
        'EATS_RETAIL_SEO_YT_SETTINGS',
        {
            constants.PERIODIC_NAME: {
                'lookup_batch_size': 2,
                'batch_max_retries_count': max_retries_count,
                'batch_delay_between_retries': 100,
                'max_skipped_batches_count': 10,
                'max_total_batches_count': 20,
            },
        },
    )

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    category_3_new = models.Category(
        category_id='803', name='Категория 3', last_referenced_at=MOCK_NOW,
    )
    assert_objects_lists(get_categories_from_db(), [category_3_new])

    assert batch_read_table_failed.has_calls
    # first retries for categories,
    # second retries for categories_relations
    assert batch_read_table_retries.times_called == max_retries_count * 2

    assert categories_import_finished.times_called == 1
    assert categories_relations_import_finished.times_called == 1
    assert periodic_finished.times_called == 1
