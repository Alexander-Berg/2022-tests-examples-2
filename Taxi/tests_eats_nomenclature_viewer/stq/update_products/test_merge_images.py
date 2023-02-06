import datetime as dt

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

    old_data = sql.load_all(models.Image)

    # save the same data
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data_repeated = sql.load_all(models.Image)
    assert old_data_repeated == old_data


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_insert(load_json, sql, nmn_data_utils):
    data_template = load_json('single_object_data_template.json')

    # initalize data
    initial_url = 'initial'
    initial_sort_order = 100
    data_template['products'][0].update(
        {'images': [{'url': initial_url, 'sort_order': initial_sort_order}]},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data = sql.load_all(models.Image)

    # insert new data (new image)
    new_url = initial_url + '_new'
    data_template['products'][0].update(
        {
            'images': [
                {'url': initial_url, 'sort_order': initial_sort_order},
                {'url': new_url, 'sort_order': initial_sort_order},
            ],
        },
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    url_to_data = {i.url: i for i in sql.load_all(models.Image)}
    assert len(url_to_data) == 2
    assert url_to_data[old_data[0].url].updated_at == old_data[0].updated_at
    assert url_to_data[new_url].updated_at >= old_data[0].updated_at
