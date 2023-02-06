import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer.stq.update_categories import constants

S3_CATEGORIES_FILE = '/some_path_to_categories.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


async def test_unknown_place(stq_runner, load, mds_s3_storage, sql):
    brand_id = sql.save(models.Brand())
    unknown_place = models.Place(brand_id=brand_id)
    assortment_name = models.AssortmentName()

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': assortment_name.name,
            'brand_id': brand_id,
            'place_ids': [unknown_place.place_id],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    assert not sql.load_all(models.PlaceAssortment)


async def test_place_brand_mismatch(stq_runner, load, mds_s3_storage, sql):
    task_brand_id = sql.save(models.Brand())
    place_brand_id = sql.save(models.Brand())
    place_id = sql.save(models.Place(brand_id=place_brand_id))
    assortment_name = models.AssortmentName()

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': assortment_name.name,
            'brand_id': task_brand_id,
            'place_ids': [place_id],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    assert not sql.load_all(models.PlaceAssortment)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_retry_on_missing_products(
        stq_runner, stq, load_json, mds_s3_storage, sql, update_taxi_config,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_UPDATE_CATEGORIES',
        {'missing_product_limit_in_percent': 50},
    )

    product_1 = models.Product(brand_id=constants.BRAND_ID)
    product_2 = models.Product(brand_id=constants.BRAND_ID)
    product_3 = models.Product(brand_id=constants.BRAND_ID)
    assortment_name = models.AssortmentName()

    data = load_json('single_object_data_template.json')
    data['categories'][0]['products'] = [
        {'id': product_1.nmn_id, 'sort_order': 1},
        {'id': product_2.nmn_id, 'sort_order': 1},
        {'id': product_3.nmn_id, 'sort_order': 1},
    ]
    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE, json.dumps(data).encode('utf-8'),
    )

    async def _call_stq():
        await stq_runner.eats_nomenclature_viewer_update_categories.call(
            task_id='1',
            kwargs={
                's3_path': S3_CATEGORIES_FILE,
                'assortment_name': assortment_name.name,
                'brand_id': constants.BRAND_ID,
                'place_ids': [constants.PLACE_ID],
                'file_datetime': DEFAULT_TIME.isoformat(),
            },
        )

    # save only only one product, which is below allowed limit
    sql.save(product_1)
    await _call_stq()

    assert stq.eats_nomenclature_viewer_update_categories.has_calls
    assert not sql.load_all(models.Category)

    stq.eats_nomenclature_viewer_update_categories.next_call()

    # save another product, which should make it above the limit
    sql.save(product_2)
    await _call_stq()

    assert not stq.eats_nomenclature_viewer_update_categories.has_calls
    product_ids = set()
    for category in sql.load_all(models.Category):
        product_ids.update({i.nmn_id for i in category.products})
    assert product_ids == {product_1.nmn_id, product_2.nmn_id}


async def test_stq_error_limit(
        sql, stq_runner, testpoint, update_taxi_config, mds_s3_storage, load,
):
    max_retries_on_error = 2
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_PROCESSING_V2',
        {'__default__': {'max_retries_on_error': max_retries_on_error}},
    )

    brand_id = sql.save(models.Brand())
    place_id = sql.save(models.Place(brand_id=brand_id))
    assortment_name = models.AssortmentName()

    @testpoint(
        'eats-nomenclature-viewer_stq_update_categories::failure-injector',
    )
    def task_testpoint(param):
        return {'inject': True}

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )

    for i in range(max_retries_on_error):
        await stq_runner.eats_nomenclature_viewer_update_categories.call(
            task_id='1',
            kwargs={
                's3_path': S3_CATEGORIES_FILE,
                'assortment_name': assortment_name.name,
                'brand_id': brand_id,
                'place_ids': [place_id],
                'file_datetime': DEFAULT_TIME.isoformat(),
            },
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': assortment_name.name,
            'brand_id': brand_id,
            'place_ids': [place_id],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls
