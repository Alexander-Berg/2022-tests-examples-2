import datetime as dt

import pytest
import pytz

from . import constants
from .... import models


MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_products_schema.yaml'],
    static_table_data=['yt_products_data_for_many_brands.yaml'],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE={
        'master_tree_settings': {
            constants.BRAND_1_ID: {'assortment_name': 'default_assortment'},
            constants.BRAND_2_ID: {'assortment_name': 'Дерево'},
        },
    },
)
async def test_many_brands(
        add_snapshot_table,
        assert_objects_lists,
        enable_periodic_in_config,
        get_products_from_db,
        save_brands_to_db,
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
    add_snapshot_table()

    brand_1 = models.Brand(
        brand_id=constants.BRAND_1_ID, slug='magnit', name='Магнит',
    )
    brand_2 = models.Brand(
        brand_id=constants.BRAND_2_ID, slug='ashan', name='АШАН',
    )
    save_brands_to_db([brand_1, brand_2])

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    product_1_first_brand = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко Простоквашино',
        brand=brand_1,
        origin_id='350462',
        last_referenced_at=MOCK_NOW,
    )
    product_2_second_brand = models.Product(
        nomenclature_id='559cffb0-9723-4377-b354-25419eef427b',
        name='Сервелат Российский',
        brand=brand_2,
        origin_id='488759',
        last_referenced_at=MOCK_NOW,
    )
    assert_objects_lists(
        get_products_from_db(),
        [product_1_first_brand, product_2_second_brand],
    )

    assert products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1
