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
        'yt_categories_data_for_filter_out.yaml',
        'yt_categories_relations_data_for_filter_out.yaml',
    ],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_filter_out(
        add_common_data,
        assert_objects_lists,
        enable_periodic_in_config,
        get_categories_from_db,
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
    add_common_data()

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    category_1_new = models.Category(
        category_id='801', name='Молоко и яйца', last_referenced_at=MOCK_NOW,
    )
    assert_objects_lists(get_categories_from_db(), [category_1_new])

    assert categories_import_finished.times_called == 1
    assert categories_relations_import_finished.times_called == 1
    assert periodic_finished.times_called == 1
