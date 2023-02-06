import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer.stq.update_categories import constants

S3_CATEGORIES_FILE = '/some_path_to_categories.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_missing_category_products(load, nmn_test_utils, sql):
    # product for category `1_1_1_w_products`
    sql.save(
        models.Product(
            brand_id=constants.BRAND_ID,
            nmn_id='00000000-0000-0000-0000-000000000001',
        ),
    )
    sql.save(
        models.Product(
            brand_id=constants.BRAND_ID,
            nmn_id='00000000-0000-0000-0000-000000000002',
        ),
    )

    await nmn_test_utils.store_data_and_call_stq_update_categories(
        data=load('missing_category_products.json').encode('utf-8'),
        path=S3_CATEGORIES_FILE,
        brand_id=constants.BRAND_ID,
        place_ids=[constants.PLACE_ID],
    )

    id_to_category = {i.name: i for i in sql.load_all(models.Category)}
    assert len(id_to_category) == 3
    assert id_to_category.keys() == {'1', '1_1', '1_1_1_w_products'}
    assert id_to_category['1_1_1_w_products'].category_products


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_products_with_mismatched_brand(
        load, nmn_test_utils, sql, update_taxi_config,
):
    _config_disable_product_limit(update_taxi_config)

    # product for category `1_1_1_w_valid_products`
    sql.save(
        models.Product(
            brand_id=constants.BRAND_ID,
            nmn_id='00000000-0000-0000-0000-000000000001',
        ),
    )
    sql.save(
        models.Product(
            brand_id=constants.BRAND_ID,
            nmn_id='00000000-0000-0000-0000-000000000002',
        ),
    )

    # product for category `1_2_1_1_w_wrong_brand_products`
    wrong_brand_id = sql.save(models.Brand(brand_id=999))
    sql.save(
        models.Product(
            brand_id=wrong_brand_id,
            nmn_id='00000000-0000-0000-0000-000000000003',
        ),
    )
    sql.save(
        models.Product(
            brand_id=wrong_brand_id,
            nmn_id='00000000-0000-0000-0000-000000000004',
        ),
    )

    await nmn_test_utils.store_data_and_call_stq_update_categories(
        data=load('products_with_mismatched_brand.json').encode('utf-8'),
        path=S3_CATEGORIES_FILE,
        brand_id=constants.BRAND_ID,
        place_ids=[constants.PLACE_ID],
    )

    id_to_category = {i.name: i for i in sql.load_all(models.Category)}
    assert len(id_to_category) == 3
    assert id_to_category.keys() == {'1', '1_1', '1_1_1_w_valid_products'}
    assert id_to_category['1_1_1_w_valid_products'].category_products


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_unknown_products(load, nmn_test_utils, sql, update_taxi_config):
    _config_disable_product_limit(update_taxi_config)

    # product for category `1_1_1_w_valid_products`
    sql.save(
        models.Product(
            brand_id=constants.BRAND_ID,
            nmn_id='00000000-0000-0000-0000-000000000001',
        ),
    )
    sql.save(
        models.Product(
            brand_id=constants.BRAND_ID,
            nmn_id='00000000-0000-0000-0000-000000000002',
        ),
    )

    await nmn_test_utils.store_data_and_call_stq_update_categories(
        data=load('unknown_products.json').encode('utf-8'),
        path=S3_CATEGORIES_FILE,
        brand_id=constants.BRAND_ID,
        place_ids=[constants.PLACE_ID],
    )

    id_to_category = {i.name: i for i in sql.load_all(models.Category)}
    assert len(id_to_category) == 3
    assert id_to_category.keys() == {'1', '1_1', '1_1_1_w_valid_products'}
    assert id_to_category['1_1_1_w_valid_products'].category_products


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_orphaned_categories(load, nmn_test_utils, sql):
    # product for category `1_1_1` and orphaned categories
    sql.save(
        models.Product(
            brand_id=constants.BRAND_ID,
            nmn_id='00000000-0000-0000-0000-000000000001',
        ),
    )

    await nmn_test_utils.store_data_and_call_stq_update_categories(
        data=load('orphaned_categories.json').encode('utf-8'),
        path=S3_CATEGORIES_FILE,
        brand_id=constants.BRAND_ID,
        place_ids=[constants.PLACE_ID],
    )

    id_to_category = {i.name: i for i in sql.load_all(models.Category)}
    assert len(id_to_category) == 3
    assert id_to_category.keys() == {'1', '1_1', '1_1_1'}


def _config_disable_product_limit(update_taxi_config):
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_UPDATE_CATEGORIES',
        {'missing_product_limit_in_percent': 100},
    )
