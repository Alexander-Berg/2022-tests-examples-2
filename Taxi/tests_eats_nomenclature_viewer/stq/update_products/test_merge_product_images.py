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
    initial_url = 'initial'
    initial_sort_order = 100
    data_template['products'][0].update(
        {'images': [{'url': initial_url, 'sort_order': initial_sort_order}]},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data = sql.load_all(models.ProductImage)

    # save the same data
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data_repeated = sql.load_all(models.ProductImage)
    assert old_data_repeated == old_data

    # change value
    data_template['products'][0].update(
        {
            'images': [
                {'url': initial_url, 'sort_order': initial_sort_order + 100},
            ],
        },
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    changed_data = sql.load_all(models.ProductImage)
    assert len(changed_data) == 1
    assert changed_data[0].updated_at >= old_data[0].updated_at
    assert changed_data[0].sort_order != old_data[0].sort_order


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_insert_image(load_json, sql, nmn_data_utils):
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

    old_data = sql.load_all(models.ProductImage)

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

    url_to_data = {i.image.url: i for i in sql.load_all(models.ProductImage)}
    assert len(url_to_data) == 2
    assert (
        url_to_data[old_data[0].image.url].updated_at == old_data[0].updated_at
    )
    assert url_to_data[new_url].updated_at >= old_data[0].updated_at


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_insert_product(load_json, sql, nmn_data_utils):
    data_template = load_json('single_object_data_template.json')

    # initalize data
    initial_url = 'initial'
    initial_sort_order = 100
    initial_nmn_id = '00000000-0000-0000-0000-000000000001'
    data_template['products'][0].update(
        {
            'id': initial_nmn_id,
            'origin_id': initial_nmn_id,
            'images': [{'url': initial_url, 'sort_order': initial_sort_order}],
        },
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    old_data = sql.load_all(models.ProductImage)

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
        nmn_id_to_product[initial_nmn_id].product_images[0].updated_at
        == old_data[0].updated_at
    )
    assert (
        nmn_id_to_product[new_nmn_id].product_images[0].updated_at
        > nmn_id_to_product[initial_nmn_id].product_images[0].updated_at
    )
    assert (
        nmn_id_to_product[new_nmn_id].product_images[0].image
        == nmn_id_to_product[initial_nmn_id].product_images[0].image
    )


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_merge_delete(load_json, sql, nmn_data_utils):
    data_template = load_json('single_object_data_template.json')

    # initalize data
    initial_url = 'initial'
    new_url = initial_url + '_new'
    initial_sort_order = 100
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

    old_url_to_data = {
        i.image.url: i for i in sql.load_all(models.ProductImage)
    }

    # insert data with a single image
    data_template['products'][0].update(
        {'images': [{'url': initial_url, 'sort_order': initial_sort_order}]},
    )
    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    new_data = sql.load_all(models.ProductImage)
    assert len(new_data) == 1
    assert new_data[0] == old_url_to_data[initial_url]
