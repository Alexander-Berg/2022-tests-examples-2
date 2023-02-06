import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils

S3_PRODUCTS_FILE = '/some_path_to_products.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['minimal_schema_data.sql'],
)
async def test_minimal_schema(stq_runner, load, mds_s3_storage, sql):
    expected_product = models.Product(
        name='name_1',
        origin_id='origin_id_1',
        nmn_id='00000000-0000-0000-0000-000000000001',
        brand_id=1,
        measure_unit='г',
        measure_value=100.2,
    )

    mds_s3_storage.put_object(
        S3_PRODUCTS_FILE, load('minimal_schema_data.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_products.call(
        task_id='1',
        kwargs={
            's3_path': S3_PRODUCTS_FILE,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    products = sql.load_all(models.Product)
    # replace updated_at for equality check to work
    for i in products + [expected_product]:
        i.reset_field_recursive('updated_at')
    assert products == [expected_product]


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['full_schema_data.sql'])
async def test_full_schema(stq_runner, load, mds_s3_storage, sql):
    expected_product_images = [
        models.ProductImage(models.Image(url='1'), sort_order=10),
        models.ProductImage(models.Image(url='2'), sort_order=20),
    ]
    expected_product_attributes = [
        models.ProductAttribute(
            models.Attribute(name='attribute_1'),
            attribute_value={'value': 'value_1'},
        ),
        models.ProductAttribute(
            models.Attribute(name='attribute_2'),
            attribute_value={'value': 'value_2'},
        ),
    ]
    expected_products = [
        models.Product(
            name='name_1',
            origin_id='origin_id_1',
            nmn_id='00000000-0000-0000-0000-000000000001',
            brand_id=1,
            sku_id='00000000-0000-0000-0000-000000000001',
            quantum=1,
            measure_unit='г',
            measure_value=100.2,
            product_images=expected_product_images,
            product_attributes=expected_product_attributes,
        ),
        models.Product(
            name='name_2',
            origin_id='origin_id_2',
            nmn_id='00000000-0000-0000-0000-000000000002',
            brand_id=1,
            sku_id='00000000-0000-0000-0000-000000000001',
            quantum=1,
            measure_unit='г',
            measure_value=100.2,
            product_images=expected_product_images,
            product_attributes=expected_product_attributes,
        ),
    ]

    mds_s3_storage.put_object(
        S3_PRODUCTS_FILE, load('full_schema_data.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_products.call(
        task_id='1',
        kwargs={
            's3_path': S3_PRODUCTS_FILE,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    products = sql.load_all(models.Product)
    # replace updated_at for equality check to work
    for i in products + expected_products:
        i.reset_field_recursive('updated_at')
    assert sorted(products) == sorted(expected_products)


@pytest.mark.parametrize(
    'product_params,expected_fields',
    [
        pytest.param({'measure/unit': 'GRM'}, {'measure_unit': 'г'}, id='GRM'),
        pytest.param(
            {'measure/unit': 'KGRM'}, {'measure_unit': 'кг'}, id='KGRM',
        ),
        pytest.param(
            {'measure/unit': 'MLT'}, {'measure_unit': 'мл'}, id='MLT',
        ),
        pytest.param({'measure/unit': 'LT'}, {'measure_unit': 'л'}, id='LT'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_fields(
        load_json,
        sql,
        nmn_data_utils,
        # parametrize
        product_params,
        expected_fields,
):
    data_template = load_json('single_object_data_template.json')
    utils.update_dict_by_paths(data_template['products'][0], product_params)

    await nmn_data_utils.store_data_and_call_stq_update_products(
        S3_PRODUCTS_FILE, data_template,
    )

    products = sql.load_all(models.Product)
    assert len(products) == 1
    for key, expected_value in expected_fields.items():
        assert getattr(products[0], key) == expected_value
