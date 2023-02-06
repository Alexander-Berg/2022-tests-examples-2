import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer import models

S3_CATEGORIES_FILE = '/some_path_to_categories.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['minimal_schema_data.sql'],
)
async def test_minimal_schema(stq_runner, load, mds_s3_storage, sql):
    # s3 file does not provide any product fields except for product id,
    # but corresponding product must be present in PG
    dummy_product = models.Product(
        nmn_id='00000000-0000-0000-0000-000000000001',
        brand_id=1,
        name='name',
        origin_id='origin_id_1',
        measure_unit='г',
        measure_value=1.0,
    )

    expected_category_products = [
        models.CategoryProduct(product=dummy_product, sort_order=100),
    ]
    expected_category = models.Category(
        name='category_1',
        nmn_id=1,
        type=models.CategoryType.PARTNER,
        category_products=expected_category_products,
    )
    expected_category.category_relation.sort_order = 100

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE, load('minimal_schema_data.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': 'assortment',
            'brand_id': 1,
            'place_ids': [1],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    # replace dynamic fields for equality check to work
    categories = sql.load_all(models.Category)
    for i in categories + [expected_category]:
        i.reset_field_recursive('updated_at')
        i.reset_field_recursive('created_at')
        i.assortment.assortment_id = 1
    assert categories == [expected_category]

    place_categories = sql.load_all(models.PlaceCategory)
    for i in place_categories:
        assert i.place_id == 1
        assert not i.active_items_count

        i.reset_field_recursive('updated_at')
        i.reset_field_recursive('created_at')
        i.assortment.assortment_id = 1
    assert sorted([i.category for i in place_categories]) == [
        expected_category,
    ]


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['full_schema_data.sql'])
async def test_full_schema(stq_runner, load, mds_s3_storage, sql):
    # s3 file does not provide any product fields except for product id,
    # but corresponding product must be present in PG
    dummy_product_1 = models.Product(
        nmn_id='00000000-0000-0000-0000-000000000001',
        brand_id=1,
        name='name',
        origin_id='origin_id_1',
        measure_unit='г',
        measure_value=1.0,
    )
    dummy_product_2 = models.Product(
        nmn_id='00000000-0000-0000-0000-000000000002',
        brand_id=1,
        name='name',
        origin_id='origin_id_2',
        measure_unit='г',
        measure_value=1.0,
    )
    expected_category_products = [
        models.CategoryProduct(product=dummy_product_1, sort_order=1),
        models.CategoryProduct(product=dummy_product_2, sort_order=2),
    ]

    expected_category_images = [
        models.CategoryImage(models.Image(url='1_url'), sort_order=0),
        models.CategoryImage(models.Image(url='2_url'), sort_order=1),
    ]

    # 1
    category_1 = models.Category(
        name='category_1',
        nmn_id=1,
        origin_id='category_1_origin',
        type=models.CategoryType.PARTNER,
        category_images=expected_category_images,
    )
    category_1.category_relation.sort_order = 1

    # 2
    category_2 = models.Category(
        name='category_2',
        nmn_id=2,
        origin_id='category_2_origin',
        type=models.CategoryType.PARTNER,
        category_images=expected_category_images,
    )
    category_2.category_relation.sort_order = 2
    category_2.category_relation.parent_category = category_1

    # 3
    category_3 = models.Category(
        name='category_3',
        nmn_id=3,
        origin_id='category_3_origin',
        type=models.CategoryType.PARTNER,
        category_images=expected_category_images,
        category_products=expected_category_products,
    )
    category_3.category_relation.sort_order = 3
    category_3.category_relation.parent_category = category_2

    # 4
    category_4 = models.Category(
        name='category_4',
        nmn_id=4,
        origin_id='category_4_origin',
        type=models.CategoryType.PARTNER,
        category_images=expected_category_images,
        category_products=expected_category_products,
    )
    category_4.category_relation.sort_order = 4
    category_4.category_relation.parent_category = category_2

    expected_categories = [category_1, category_2, category_3, category_4]

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE, load('full_schema_data.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': 'assortment',
            'brand_id': 1,
            'place_ids': [1],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    # replace dynamic fields for equality check to work
    categories = sql.load_all(models.Category)
    for i in categories + expected_categories:
        i.reset_field_recursive('updated_at')
        i.reset_field_recursive('created_at')
        i.assortment.assortment_id = 1
    assert sorted(categories) == sorted(expected_categories)

    place_categories = sql.load_all(models.PlaceCategory)
    for i in place_categories:
        assert i.place_id == 1
        assert not i.active_items_count

        i.reset_field_recursive('updated_at')
        i.reset_field_recursive('created_at')
        i.assortment.assortment_id = 1
    assert sorted([i.category for i in place_categories]) == sorted(
        expected_categories,
    )


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
@pytest.mark.parametrize(
    'expected_category_type',
    [
        pytest.param(models.CategoryType.PARTNER, id='partner'),
        pytest.param(models.CategoryType.CUSTOM_BASE, id='custom base'),
        pytest.param(models.CategoryType.CUSTOM_PROMO, id='custom promo'),
        pytest.param(
            models.CategoryType.CUSTOM_RESTAURANT, id='custom restaurant',
        ),
    ],
)
async def test_category_values(
        stq_runner,
        load_json,
        mds_s3_storage,
        sql,
        # parametrize
        expected_category_type,
):
    sql.save(
        models.Product(
            nmn_id='00000000-0000-0000-0000-000000000001', brand_id=1,
        ),
    )

    s3_data = load_json('single_object_data_template.json')
    s3_data['categories'][0]['type'] = expected_category_type.value
    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE, json.dumps(s3_data).encode('utf-8'),
    )

    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': 'assortment',
            'brand_id': 1,
            'place_ids': [1],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    categories = sql.load_all(models.Category)
    assert len(categories) == 1
    assert categories[0].type == expected_category_type
