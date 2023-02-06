import copy
import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer import models

S3_PRODUCTS_FILE = '/some_path_to_products.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_invalid_s3_path(stq_runner, load, mds_s3_storage, sql):
    invalid_path = f'/invalid_path/{S3_PRODUCTS_FILE}'

    mds_s3_storage.put_object(
        S3_PRODUCTS_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_products.call(
        task_id='1',
        kwargs={
            's3_path': invalid_path,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    assert not sql.load_all(models.Product)


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_dir_in_s3path(stq_runner, load_json, mds_s3_storage, sql):
    s3dir = '/dir/'

    file_count = 3
    product_in_file_count = 2

    data_template = load_json('single_object_data_template.json')
    product_template = copy.deepcopy(data_template['products'][0])
    data_template['products'].clear()

    expected_product_ids = set()
    for file_idx in range(0, file_count):
        file_data = copy.deepcopy(data_template)
        for _ in range(0, product_in_file_count):
            current_product_idx = len(expected_product_ids)
            product_data = copy.deepcopy(product_template)
            product_data[
                'id'
            ] = f'00000000-0000-0000-0000-00000000000{current_product_idx}'
            product_data['origin_id'] = str(current_product_idx)

            file_data['products'].append(product_data)
            expected_product_ids.add(product_data['id'])

        mds_s3_storage.put_object(
            f'{s3dir}/{file_idx}.json', json.dumps(file_data).encode('utf-8'),
        )

    await stq_runner.eats_nomenclature_viewer_update_products.call(
        task_id='1',
        kwargs={'s3_path': s3dir, 'file_datetime': DEFAULT_TIME.isoformat()},
    )

    product_ids = {i.nmn_id for i in sql.load_all(models.Product)}
    assert product_ids == expected_product_ids


async def test_stq_error_limit(
        mds_s3_storage, load, stq_runner, testpoint, update_taxi_config,
):
    max_retries_on_error = 2
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_PROCESSING_V2',
        {'__default__': {'max_retries_on_error': max_retries_on_error}},
    )

    @testpoint(
        'eats-nomenclature-viewer_stq_update_products::failure-injector',
    )
    def task_testpoint(param):
        return {'inject': True}

    mds_s3_storage.put_object(
        S3_PRODUCTS_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )

    for i in range(max_retries_on_error):
        await stq_runner.eats_nomenclature_viewer_update_products.call(
            task_id='1',
            kwargs={
                's3_path': S3_PRODUCTS_FILE,
                'file_datetime': DEFAULT_TIME.isoformat(),
            },
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_nomenclature_viewer_update_products.call(
        task_id='1',
        kwargs={
            's3_path': S3_PRODUCTS_FILE,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls
