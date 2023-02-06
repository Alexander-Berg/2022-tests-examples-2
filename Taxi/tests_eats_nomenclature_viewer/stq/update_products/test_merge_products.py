import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer.stq.update_products import constants
from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils

BRAND_ID = constants.BRAND_ID
DEFAULT_PRODUCT_VALUES = constants.DEFAULT_PRODUCT_VALUES

S3_PRODUCTS_FILE = '/some_path_to_products.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_update_unchanged(load_json, sql, nmn_data_utils):
    old_product = models.Product(updated_at=OLD_TIME, **DEFAULT_PRODUCT_VALUES)
    sql.save(old_product)

    # save the same data
    data_template = load_json('single_object_data_template.json')
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    db_products = sql.load_all(models.Product)
    assert db_products == [old_product]


@pytest.mark.parametrize(
    'old_db_value, new_json_value, expected_db_value',
    [
        pytest.param(
            {'sku_id': 'old'},
            {'sku_id': 'new'},
            {'sku_id': 'new'},
            id='sku_id',
        ),
        pytest.param(
            {'name': 'old'}, {'name': 'new'}, {'name': 'new'}, id='name',
        ),
        pytest.param(
            {'quantum': None},
            {'quantum': 1.0},
            {'quantum': 1.0},
            id='quantum',
        ),
        pytest.param(
            {'measure_unit': 'кг'},
            {'measure/unit': 'MLT'},
            {'measure_unit': 'мл'},
            id='measure_unit',
        ),
        pytest.param(
            {'measure_value': 5.0},
            {'measure/value': '1'},
            {'measure_value': 1},
            id='measure_value',
        ),
        pytest.param(
            {'brand_id': 1}, {'brand_id': 2}, {'brand_id': 2}, id='brand_id',
        ),
    ],
)
@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_update_changed(
        load_json,
        sql,
        nmn_data_utils,
        # parametrize
        old_db_value,
        new_json_value,
        expected_db_value,
):
    if 'brand_id' in new_json_value:
        sql.save(models.Brand(brand_id=new_json_value['brand_id']))

    product = models.Product(updated_at=OLD_TIME, **DEFAULT_PRODUCT_VALUES)
    product.update(old_db_value)
    sql.save(product)

    # change value
    expected_product = product.clone()
    expected_product.updated_at = None
    expected_product.update(expected_db_value)

    data_template = load_json('single_object_data_template.json')
    utils.update_dict_by_paths(data_template['products'][0], new_json_value)
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    db_products = sql.load_all(models.Product)
    assert len(db_products) == 1
    db_product = db_products[0]

    assert db_product.updated_at > product.updated_at
    db_product.updated_at = None
    assert db_product == expected_product


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_insert(load_json, sql, nmn_data_utils):
    old_product = models.Product(updated_at=OLD_TIME, **DEFAULT_PRODUCT_VALUES)
    old_product.nmn_id = '00000000-0000-0000-0000-000000000001'
    sql.save(old_product)

    # insert new product
    expected_product = models.Product(**DEFAULT_PRODUCT_VALUES)
    expected_product.nmn_id = '00000000-0000-0000-0000-000000000002'
    expected_product.origin_id = expected_product.nmn_id

    data_template = load_json('single_object_data_template.json')
    data_template['products'][0].update(
        {
            'id': expected_product.nmn_id,
            'origin_id': expected_product.origin_id,
        },
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    id_to_data = {i.nmn_id: i for i in sql.load_all(models.Product)}
    assert len(id_to_data) == 2
    db_old_product = id_to_data[old_product.nmn_id]
    db_new_product = id_to_data[expected_product.nmn_id]

    assert db_old_product == old_product
    assert db_new_product.updated_at > old_product.updated_at
    db_new_product.updated_at = None
    assert db_new_product == expected_product
