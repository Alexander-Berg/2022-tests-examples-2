import datetime as dt
import decimal

import pytest
import pytz

from . import models

PERIODIC_NAME = 'db-cleanup-periodic'
BRAND_1_ID = '771'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'
MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)
DEFAULT_THRESHOLD = 100
CATEGORIES_RELATIONS_THRESHOLD = 1
CATEGORIES_PRODUCT_TYPES_THRESHOLD = 2
CATEGORIES_PRODUCTS_THRESHOLD = 3
PLACES_PRODUCTS_THRESHOLD = 4
PRODUCTS_BARCODES_THRESHOLD = 5
PRODUCTS_PICTURES_THRESHOLD = 6
PRODUCTS_TYPES_PRODUCT_BRANDS_THRESHOLD = 7
TAGS_THRESHOLD = 8
CATEGORIES_TAGS_THRESHOLD = 9


@pytest.mark.now(MOCK_NOW.isoformat())
async def test_db_cleanup(
        assert_objects_lists,
        get_categories_from_db,
        get_products_from_db,
        get_product_types_from_db,
        save_barcodes_to_db,
        save_brands_to_db,
        save_tags_to_db,
        get_tags_from_db,
        save_categories_to_db,
        save_pictures_to_db,
        save_product_types_to_db,
        save_products_to_db,
        save_product_brands_to_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
):
    _set_configs(update_taxi_config)

    brand = _generate_brand()
    save_brands_to_db([brand])

    [
        product_brands,
        product_types,
        barcodes,
        pictures,
        products,
        tags,
        categories,
    ] = _generate_data(brand)
    save_product_types_to_db(product_types)
    save_product_brands_to_db(product_brands)
    save_barcodes_to_db(barcodes)
    save_pictures_to_db(pictures)
    save_products_to_db(products)
    save_tags_to_db(tags)
    save_categories_to_db(categories)

    @testpoint('db-cleanup-periodic-finished')
    def task_testpoint(param):
        pass

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    [product_brand_1, _] = product_brands
    [product_type_1, product_type_2] = product_types
    [barcode_1, _] = barcodes
    [picture_1, _] = pictures
    [product_1, product_2] = products
    [tag_1, tag_2, tag_3, tag_4] = tags[:4]
    [category_1, category_2, category_3, category_4, category_5] = categories

    product_type_1.set_type_brands(
        [
            models.ProductTypeProductBrand(
                product_brand_1, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    product_1.set_product_barcodes(
        [models.ProductBarcode(barcode_1, last_referenced_at=MOCK_NOW)],
    )
    product_1.set_product_pictures(
        [models.ProductPicture(picture_1, last_referenced_at=MOCK_NOW)],
    )
    product_1.set_product_in_places(
        [
            models.ProductInPlace(
                place=brand.places[PLACE_1_ID],
                price=decimal.Decimal('50.97'),
                stocks=500,
                is_available=True,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    category_1.set_category_product_types(
        [
            models.CategoryProductType(
                product_type_1, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    category_1.set_category_products(
        [models.CategoryProduct(product_1, last_referenced_at=MOCK_NOW)],
    )
    category_3.set_child_categories_relations(
        [models.CategoryRelation(category_1, last_referenced_at=MOCK_NOW)],
    )
    category_5.set_category_tags([])

    assert_objects_lists(
        get_product_types_from_db(), [product_type_1, product_type_2],
    )
    assert_objects_lists(get_products_from_db(), [product_1, product_2])
    assert_objects_lists(get_tags_from_db(), [tag_1, tag_2, tag_3, tag_4])
    assert_objects_lists(
        get_categories_from_db(),
        [category_1, category_2, category_3, category_4, category_5],
    )

    assert task_testpoint.times_called == 1


async def test_periodic_metrics(
        save_brands_to_db, update_taxi_config, verify_periodic_metrics,
):
    _set_configs(update_taxi_config)

    brand = _generate_brand()
    save_brands_to_db([brand])

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _set_configs(update_taxi_config):
    update_taxi_config(
        'EATS_RETAIL_SEO_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 10800}},
    )
    update_taxi_config(
        'EATS_RETAIL_SEO_DB_CLEANUP_SETTINGS',
        {
            '__default__': {
                'last_referenced_threshold_in_hours': DEFAULT_THRESHOLD,
            },
            'categories_relations': {
                'last_referenced_threshold_in_hours': (
                    CATEGORIES_RELATIONS_THRESHOLD
                ),
            },
            'categories_product_types': {
                'last_referenced_threshold_in_hours': (
                    CATEGORIES_PRODUCT_TYPES_THRESHOLD
                ),
            },
            'categories_products': {
                'last_referenced_threshold_in_hours': (
                    CATEGORIES_PRODUCTS_THRESHOLD
                ),
            },
            'places_products': {
                'last_referenced_threshold_in_hours': (
                    PLACES_PRODUCTS_THRESHOLD
                ),
            },
            'products_barcodes': {
                'last_referenced_threshold_in_hours': (
                    PRODUCTS_BARCODES_THRESHOLD
                ),
            },
            'products_pictures': {
                'last_referenced_threshold_in_hours': (
                    PRODUCTS_PICTURES_THRESHOLD
                ),
            },
            'product_types_product_brands': {
                'last_referenced_threshold_in_hours': (
                    PRODUCTS_TYPES_PRODUCT_BRANDS_THRESHOLD
                ),
            },
            'tags': {'last_referenced_threshold_in_hours': TAGS_THRESHOLD},
            'categories_tags': {
                'last_referenced_threshold_in_hours': (
                    CATEGORIES_TAGS_THRESHOLD
                ),
            },
        },
    )


def _get_time_in_past(hours):
    return MOCK_NOW - dt.timedelta(hours=hours)


def _generate_brand():
    brand = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand.brand_id,
        ),
        PLACE_2_ID: models.Place(
            place_id=PLACE_2_ID, slug='place1002', brand_id=brand.brand_id,
        ),
    }
    return brand


def _generate_data(brand):
    product_brand_1 = models.ProductBrand('Мираторг')
    product_brand_2 = models.ProductBrand('Агуша')
    product_brands = [product_brand_1, product_brand_2]

    product_type_1 = models.ProductType('product_type_1')
    product_type_1.set_type_brands(
        [
            models.ProductTypeProductBrand(
                product_brand_1, last_referenced_at=MOCK_NOW,
            ),
            models.ProductTypeProductBrand(
                product_brand_2,
                last_referenced_at=_get_time_in_past(
                    2 * PRODUCTS_TYPES_PRODUCT_BRANDS_THRESHOLD,
                ),
            ),
        ],
    )
    product_type_2 = models.ProductType('product_type_2')
    product_types = [product_type_1, product_type_2]

    barcode_1 = models.Barcode('10205800000')
    barcode_2 = models.Barcode('10205800001')
    barcodes = [barcode_1, barcode_2]

    picture_1 = models.Picture('product_url_1')
    picture_2 = models.Picture('product_url_2')
    pictures = [picture_1, picture_2]

    product_1 = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко',
        brand=brand,
        origin_id='item-origin-id-1',
        description='Товар 1<p>Описание</p> <b>Молоко</b>',
        vendor_name='Поставщик&nbsp;1',
        vendor_country='Австралия',
        measure_in_milliliters=2000,
        delivery_flag=False,
        pick_flag=True,
    )
    product_1.set_product_barcodes(
        [
            models.ProductBarcode(barcode_1, last_referenced_at=MOCK_NOW),
            models.ProductBarcode(
                barcode_2,
                last_referenced_at=_get_time_in_past(
                    2 * PRODUCTS_BARCODES_THRESHOLD,
                ),
            ),
        ],
    )
    product_1.set_product_pictures(
        [
            models.ProductPicture(picture_1, last_referenced_at=MOCK_NOW),
            models.ProductPicture(
                picture_2,
                last_referenced_at=_get_time_in_past(
                    2 * PRODUCTS_PICTURES_THRESHOLD,
                ),
            ),
        ],
    )
    product_1.set_product_in_places(
        [
            models.ProductInPlace(
                place=brand.places[PLACE_1_ID],
                price=decimal.Decimal('50.97'),
                stocks=500,
                is_available=True,
                last_referenced_at=MOCK_NOW,
            ),
            models.ProductInPlace(
                place=brand.places[PLACE_2_ID],
                price=decimal.Decimal('55.55'),
                stocks=700,
                is_available=True,
                last_referenced_at=_get_time_in_past(
                    2 * PLACES_PRODUCTS_THRESHOLD,
                ),
            ),
        ],
    )
    product_2 = models.Product(
        nomenclature_id='45631b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко сухое',
        brand=brand,
        origin_id='item-origin-id-2',
        description='Товар 2<p>Описание</p> <b>Молоко</b>',
        vendor_name='Поставщик&nbsp;1',
        vendor_country='Австралия',
        measure_in_milliliters=2000,
        delivery_flag=False,
        pick_flag=True,
    )
    products = [product_1, product_2]

    not_referenced_old_tag = models.Tag(
        'Тег молоко', last_referenced_at=_get_time_in_past(2 * TAGS_THRESHOLD),
    )
    not_referenced_new_tag = models.Tag(
        'Тег сливки', last_referenced_at=MOCK_NOW,
    )

    referenced_lately_old_tag = models.Tag(
        'Тег сметана',
        last_referenced_at=_get_time_in_past(2 * TAGS_THRESHOLD),
    )
    referenced_lately_new_tag = models.Tag(
        'Тег кефир и сметана', last_referenced_at=MOCK_NOW,
    )

    referenced_long_time_ago_old_tag = models.Tag(  # pylint: disable=C0103
        'Тег йогурт', last_referenced_at=_get_time_in_past(2 * TAGS_THRESHOLD),
    )
    referenced_long_time_ago_new_tag = models.Tag(  # pylint: disable=C0103
        'Тег творог и йогурт', last_referenced_at=MOCK_NOW,
    )

    tags = [
        not_referenced_new_tag,
        referenced_lately_old_tag,
        referenced_lately_new_tag,
        referenced_long_time_ago_new_tag,
        not_referenced_old_tag,
        referenced_long_time_ago_old_tag,
    ]

    category_1 = models.Category(
        category_id='123', name='Молоко', image_url='cat_url_1234',
    )
    category_1.set_category_product_types(
        [
            models.CategoryProductType(
                product_type_1, last_referenced_at=MOCK_NOW,
            ),
            models.CategoryProductType(
                product_type_2,
                last_referenced_at=_get_time_in_past(
                    2 * CATEGORIES_PRODUCT_TYPES_THRESHOLD,
                ),
            ),
        ],
    )
    category_1.set_category_products(
        [
            models.CategoryProduct(product_1, last_referenced_at=MOCK_NOW),
            models.CategoryProduct(
                product_2,
                last_referenced_at=_get_time_in_past(
                    2 * CATEGORIES_PRODUCTS_THRESHOLD,
                ),
            ),
        ],
    )
    category_2 = models.Category(
        category_id='456', name='Cыр', image_url='cat_url_123',
    )
    category_3 = models.Category(category_id='789', name='Молоко & сыр')
    category_3.set_child_categories_relations(
        [
            models.CategoryRelation(category_1, last_referenced_at=MOCK_NOW),
            models.CategoryRelation(
                category_2,
                last_referenced_at=_get_time_in_past(
                    2 * CATEGORIES_RELATIONS_THRESHOLD,
                ),
            ),
        ],
    )
    category_4 = models.Category(category_id='111', name='Сметана')
    category_4.set_category_tags(
        [
            models.CategoryTag(
                tag=referenced_lately_old_tag, last_referenced_at=MOCK_NOW,
            ),
            models.CategoryTag(
                tag=referenced_lately_new_tag, last_referenced_at=MOCK_NOW,
            ),
        ],
    )

    category_5 = models.Category(category_id='222', name='Йогурт')
    category_5.set_category_tags(
        [
            models.CategoryTag(
                tag=referenced_long_time_ago_old_tag,
                last_referenced_at=_get_time_in_past(
                    2 * CATEGORIES_TAGS_THRESHOLD,
                ),
            ),
            models.CategoryTag(
                tag=referenced_long_time_ago_new_tag,
                last_referenced_at=_get_time_in_past(
                    2 * CATEGORIES_TAGS_THRESHOLD,
                ),
            ),
        ],
    )

    categories = [category_1, category_2, category_3, category_4, category_5]

    return [
        product_brands,
        product_types,
        barcodes,
        pictures,
        products,
        tags,
        categories,
    ]
