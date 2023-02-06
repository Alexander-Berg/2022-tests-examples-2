import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer.stq.update_products import constants
from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer.sql_adaptor import (
    SqlAdaptor,
)  # noqa: F401 # pylint: disable=C5521

S3_PRODUCTS_FILE = '/some_path_to_products.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_update_unchanged(
        load_json, sql: SqlAdaptor, nmn_data_utils,
):
    attribute_name = 'name'
    attribute_value = {'value': '1'}
    product_attribute = models.ProductAttribute(
        attribute=models.Attribute(name=attribute_name, updated_at=OLD_TIME),
        attribute_value=attribute_value,
        updated_at=OLD_TIME,
    )
    sql.save(
        models.Product(
            updated_at=OLD_TIME,
            product_attributes=[product_attribute],
            **constants.DEFAULT_PRODUCT_VALUES,  # type: ignore
        ),
    )

    # save the same data
    data_template = load_json('single_object_data_template.json')
    data_template['products'][0]['attributes'] = {
        attribute_name: json.dumps(attribute_value),
    }

    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    db_attributes = sql.load_all(models.ProductAttribute)
    assert db_attributes == [product_attribute]


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_update_unchanged_json_invariant(
        load_json, sql: SqlAdaptor, nmn_data_utils,
):  # pylint: disable=C0103
    # C++ and PG have different serialize outputs,
    # this test verifies that these differences do not affect merger

    attribute_name = 'name'
    attribute_value = {'value1': '1', 'value2': '2', 'value3': '3'}
    # extra whitespace and unordered
    attribute_value_json = (
        '{   "value2"  :  "2"  , "value3"  :  "3" , "value1"  :  "1"    }'
    )
    product_attribute = models.ProductAttribute(
        attribute=models.Attribute(name=attribute_name, updated_at=OLD_TIME),
        attribute_value=attribute_value,
        updated_at=OLD_TIME,
    )
    sql.save(
        models.Product(
            updated_at=OLD_TIME,
            product_attributes=[product_attribute],
            **constants.DEFAULT_PRODUCT_VALUES,  # type: ignore
        ),
    )

    # save the same data
    data_template = load_json('single_object_data_template.json')
    data_template['products'][0]['attributes'] = {
        attribute_name: attribute_value_json,
    }

    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    db_attributes = sql.load_all(models.ProductAttribute)
    assert db_attributes == [product_attribute]


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_update(load_json, sql: SqlAdaptor, nmn_data_utils):
    attribute_name = 'name'
    attribute_value = {'value': '1'}
    old_product_attribute = models.ProductAttribute(
        attribute=models.Attribute(name=attribute_name, updated_at=OLD_TIME),
        attribute_value=attribute_value,
        updated_at=OLD_TIME,
    )
    sql.save(
        models.Product(
            updated_at=OLD_TIME,
            product_attributes=[old_product_attribute],
            **constants.DEFAULT_PRODUCT_VALUES,  # type: ignore
        ),
    )

    # change value
    expected_product_attribute = old_product_attribute.clone()
    expected_product_attribute.updated_at = None
    expected_product_attribute.attribute_value = {'value': '2'}

    data_template = load_json('single_object_data_template.json')
    data_template['products'][0]['attributes'] = {
        expected_product_attribute.attribute.name: json.dumps(
            expected_product_attribute.attribute_value,
        ),
    }

    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    db_attributes = sql.load_all(models.ProductAttribute)
    assert len(db_attributes) == 1
    db_attribute = db_attributes[0]

    assert (
        db_attribute.updated_at > old_product_attribute.updated_at  # type: ignore # noqa: E501
    )
    db_attribute.updated_at = None
    assert db_attribute == expected_product_attribute


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_insert_attribute(load_json, sql, nmn_data_utils):
    data_template = load_json('single_object_data_template.json')

    # initalize data
    initial_name = 'initial'
    initial_value = json.dumps({'value': 1})
    data_template['products'][0].update(
        {'attributes': {initial_name: initial_value}},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data = sql.load_all(models.ProductAttribute)

    # insert new data (new attribute)
    new_name = initial_name + '_new'
    data_template['products'][0].update(
        {'attributes': {initial_name: initial_value, new_name: initial_value}},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    name_to_data = {
        i.attribute.name: i for i in sql.load_all(models.ProductAttribute)
    }
    assert len(name_to_data) == 2
    assert (
        name_to_data[old_data[0].attribute.name].updated_at
        == old_data[0].updated_at
    )
    assert name_to_data[new_name].updated_at >= old_data[0].updated_at


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_insert_product(load_json, sql, nmn_data_utils):
    data_template = load_json('single_object_data_template.json')

    # initalize data
    initial_name = 'initial'
    initial_value = json.dumps({'value': 1})
    initial_nmn_id = '00000000-0000-0000-0000-000000000001'
    data_template['products'][0].update(
        {
            'id': initial_nmn_id,
            'origin_id': initial_nmn_id,
            'attributes': {initial_name: initial_value},
        },
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data = sql.load_all(models.ProductAttribute)

    # insert new data (new product)
    data_template['products'].append(data_template['products'][0])
    new_nmn_id = '00000000-0000-0000-0000-000000000002'
    data_template['products'][1].update(
        {'id': new_nmn_id, 'origin_id': new_nmn_id},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    nmn_id_to_product = {i.nmn_id: i for i in sql.load_all(models.Product)}
    assert len(nmn_id_to_product) == 2
    assert (
        nmn_id_to_product[initial_nmn_id].product_attributes[0].updated_at
        == old_data[0].updated_at
    )
    assert (
        nmn_id_to_product[new_nmn_id].product_attributes[0].updated_at
        > nmn_id_to_product[initial_nmn_id].product_attributes[0].updated_at
    )
    assert (
        nmn_id_to_product[new_nmn_id].product_attributes[0].attribute
        == nmn_id_to_product[initial_nmn_id].product_attributes[0].attribute
    )


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_delete(load_json, sql, nmn_data_utils):
    data_template = load_json('single_object_data_template.json')

    # initalize data
    initial_name = 'initial'
    new_name = initial_name + '_new'
    initial_value = json.dumps({'value': 1})
    data_template['products'][0].update(
        {'attributes': {initial_name: initial_value, new_name: initial_value}},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_name_to_data = {
        i.attribute.name: i for i in sql.load_all(models.ProductAttribute)
    }

    # insert data with a single attribute
    data_template['products'][0].update(
        {'attributes': {initial_name: initial_value}},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    new_data = sql.load_all(models.ProductAttribute)
    assert len(new_data) == 1
    assert new_data[0] == old_name_to_data[initial_name]
