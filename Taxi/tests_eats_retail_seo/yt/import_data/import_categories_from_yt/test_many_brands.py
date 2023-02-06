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
        'yt_categories_data_for_many_brands.yaml',
        'yt_categories_relations_data_for_many_brands.yaml',
    ],
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
        get_categories_from_db,
        save_brands_to_db,
        taxi_eats_retail_seo,
        testpoint,
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

    enable_periodic_in_config(constants.PERIODIC_NAME)
    add_snapshot_table()

    brand_1 = models.Brand(
        brand_id=constants.BRAND_1_ID, slug='magnit', name='Магнит',
    )
    brand_1.places = {
        constants.PLACE_1_ID: models.Place(
            place_id=constants.PLACE_1_ID,
            slug='place1001',
            brand_id=brand_1.brand_id,
        ),
    }
    brand_2 = models.Brand(
        brand_id=constants.BRAND_2_ID, slug='ashan', name='АШАН',
    )
    brand_2.places = {
        constants.PLACE_2_ID: models.Place(
            place_id=constants.PLACE_2_ID,
            slug='place1002',
            brand_id=brand_2.brand_id,
        ),
    }
    save_brands_to_db([brand_1, brand_2])

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    category_1_first_brand = models.Category(
        category_id='801', name='Молоко и яйца', last_referenced_at=MOCK_NOW,
    )
    category_2_first_brand = models.Category(
        category_id='802', name='Молоко', last_referenced_at=MOCK_NOW,
    )

    category_3_second_brand = models.Category(
        category_id='803', name='Яйца', last_referenced_at=MOCK_NOW,
    )

    # category tree is taken from all brands
    category_1_first_brand.set_child_categories(
        [category_2_first_brand, category_3_second_brand],
        last_referenced_at=MOCK_NOW,
    )

    assert_objects_lists(
        get_categories_from_db(),
        [
            category_1_first_brand,
            category_2_first_brand,
            category_3_second_brand,
        ],
    )

    assert categories_import_finished.times_called == 1
    assert categories_relations_import_finished.times_called == 1
    assert periodic_finished.times_called == 1
