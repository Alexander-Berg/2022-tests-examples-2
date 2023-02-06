import datetime as dt

import pytest
import pytz

from . import constants
from .... import models


MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_products_schema.yaml'],
    static_table_data=['yt_products_data_for_retries.yaml'],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_retries(
        add_common_data,
        assert_objects_lists,
        enable_periodic_in_config,
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
    brand = add_common_data()

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

    product_3_new = models.Product(
        nomenclature_id='559cffb0-9723-4377-b354-25419eef427b',
        name='Сервелат Российский',
        brand=brand,
        origin_id='488759',
        last_referenced_at=MOCK_NOW,
    )
    assert_objects_lists(get_products_from_db(), [product_3_new])

    assert batch_read_table_failed.has_calls
    assert batch_read_table_retries.times_called == max_retries_count

    assert products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1
