import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer import models

S3_PRODUCTS_FILE = '/some_path_to_products.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_update(load_json, sql, nmn_data_utils):
    data_template = load_json('single_object_data_template.json')

    # initalize data
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data = sql.load_all(models.Attribute)

    # save the same data
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data_repeated = sql.load_all(models.Attribute)
    assert old_data_repeated == old_data


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_insert(load_json, sql, nmn_data_utils):
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

    old_data = sql.load_all(models.Attribute)

    # insert new data (new attribute)
    new_name = initial_name + '_new'
    data_template['products'][0].update(
        {'attributes': {initial_name: initial_value, new_name: initial_value}},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    name_to_data = {i.name: i for i in sql.load_all(models.Attribute)}
    assert len(name_to_data) == 2
    assert name_to_data[old_data[0].name].updated_at == old_data[0].updated_at
    assert name_to_data[new_name].updated_at >= old_data[0].updated_at
