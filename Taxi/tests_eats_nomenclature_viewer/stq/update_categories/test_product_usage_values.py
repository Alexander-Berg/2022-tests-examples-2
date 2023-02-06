import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_categories import constants

S3_CATEGORIES_FILE = '/some_path_to_categories.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_insert(nmn_test_utils, load_json, sql):
    old_product_id = sql.save(models.Product(brand_id=constants.BRAND_ID))
    old_product_usage = models.ProductUsage(
        product_nmn_id=old_product_id,
        last_referenced_at=OLD_TIME,
        created_at=OLD_TIME,
        updated_at=OLD_TIME,
    )
    sql.save(old_product_usage)

    new_product_id = sql.save(models.Product(brand_id=constants.BRAND_ID))

    data = load_json('single_object_data_template.json')
    data['categories'][0]['products'] = [
        {'id': new_product_id, 'sort_order': 1},
    ]
    await nmn_test_utils.store_data_and_call_stq_update_categories(
        data=data,
        path=S3_CATEGORIES_FILE,
        brand_id=constants.BRAND_ID,
        place_ids=[constants.PLACE_ID],
    )

    id_to_product_usage = {
        i.product_nmn_id: i for i in sql.load_all(models.ProductUsage)
    }
    assert len(id_to_product_usage) == 2
    db_old_product_usage = id_to_product_usage[old_product_id]
    db_new_product_usage = id_to_product_usage[new_product_id]

    assert db_old_product_usage == old_product_usage
    assert db_new_product_usage.updated_at > old_product_usage.updated_at
    assert (
        db_new_product_usage.last_referenced_at
        > old_product_usage.last_referenced_at
    )


@pytest.mark.parametrize(
    **utils.gen_bool_params('is_last_referenced_at_outdated'),
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_update(
        nmn_test_utils,
        load_json,
        sql,
        update_taxi_config,
        # parametrize
        is_last_referenced_at_outdated,
):
    last_referenced_at_treshold = dt.timedelta(minutes=5)
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_UPDATE_CATEGORIES',
        {
            'products_last_referenced_at_update_threshold_in_min': (
                last_referenced_at_treshold.seconds / 60
            ),
        },
    )

    now = utils.now_with_tz()
    if is_last_referenced_at_outdated:
        old_last_referenced_at = now - last_referenced_at_treshold * 2
    else:
        old_last_referenced_at = now - last_referenced_at_treshold / 2

    product_id = sql.save(models.Product(brand_id=constants.BRAND_ID))
    old_product_usage = models.ProductUsage(
        product_nmn_id=product_id,
        last_referenced_at=old_last_referenced_at,
        created_at=OLD_TIME,
        updated_at=OLD_TIME,
    )
    sql.save(old_product_usage)

    data = load_json('single_object_data_template.json')
    data['categories'][0]['products'] = [{'id': product_id, 'sort_order': 1}]
    await nmn_test_utils.store_data_and_call_stq_update_categories(
        data=data,
        path=S3_CATEGORIES_FILE,
        brand_id=constants.BRAND_ID,
        place_ids=[constants.PLACE_ID],
    )

    db_product_usages = sql.load_all(models.ProductUsage)
    assert len(db_product_usages) == 1
    db_product_usage = db_product_usages[0]

    if is_last_referenced_at_outdated:
        assert db_product_usage.updated_at > old_product_usage.updated_at
        assert (
            db_product_usage.last_referenced_at
            > old_product_usage.last_referenced_at
        )
    else:
        assert db_product_usage == old_product_usage
