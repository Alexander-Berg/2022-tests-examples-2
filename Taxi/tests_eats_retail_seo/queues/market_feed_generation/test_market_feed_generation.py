import datetime as dt
import decimal

import pytest
import pytz

from ... import constants
from ... import models


PREVIOUS_GENERATED_AT = '2020-01-01T10:00:00+03:00'
MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)
BRAND_1_ID = '771'
BRAND_2_ID = '772'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'
MARKET_FEED_SETTINGS_KEY = 'market_feed'


@pytest.mark.now(MOCK_NOW.isoformat())
async def test_market_feed_generation(
        load,
        load_expected_market_feed,
        load_result_market_feed,
        normalize_market_feed_xml,
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        stq_runner,
        update_taxi_config,
):
    _set_configs(update_taxi_config)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [
        products,
        categories,
        generalized_places_products,
    ] = _generate_products_and_categories(brands)
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(generalized_places_products)

    await stq_runner.eats_retail_seo_market_feed_generation.call(
        task_id=BRAND_1_ID,
        args=[],
        kwargs={'brand_id': BRAND_1_ID},
        expect_fail=False,
    )

    result_xml = load_result_market_feed(brands[BRAND_1_ID])
    expected_xml = load_expected_market_feed(
        load('expected_feed.xml'), MOCK_NOW,
    )

    assert normalize_market_feed_xml(result_xml) == normalize_market_feed_xml(
        expected_xml,
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize('already_generated', [True, False])
async def test_save_market_feed_to_db(
        assert_objects_lists,
        generate_feed_s3_path,
        get_brands_market_feeds_from_db,
        save_brands_to_db,
        save_brands_feeds_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        stq_runner,
        to_utc_datetime,
        update_taxi_config,
        # parametrize params
        already_generated,
):
    _set_configs(update_taxi_config)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [
        products,
        categories,
        generalized_places_products,
    ] = _generate_products_and_categories(brands)
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(generalized_places_products)

    brand_1 = brands[BRAND_1_ID]
    brand_market_feed_1 = models.BrandMarketFeed(
        brand=brand_1,
        s3_path=generate_feed_s3_path(
            constants.S3_DIRS[constants.MARKET_FEED_TYPE], brand_1,
        ),
        last_generated_at=to_utc_datetime(PREVIOUS_GENERATED_AT),
    )
    if already_generated:
        save_brands_feeds_to_db([brand_market_feed_1])

    await stq_runner.eats_retail_seo_market_feed_generation.call(
        task_id=BRAND_1_ID,
        args=[],
        kwargs={'brand_id': BRAND_1_ID},
        expect_fail=False,
    )

    brand_market_feed_1.last_generated_at = to_utc_datetime(MOCK_NOW)
    assert_objects_lists(
        get_brands_market_feeds_from_db(), [brand_market_feed_1],
    )


@pytest.mark.now(MOCK_NOW.isoformat())
async def test_empty_feed(
        mds_s3_storage, save_brands_to_db, stq_runner, update_taxi_config,
):
    _set_configs(update_taxi_config)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    await stq_runner.eats_retail_seo_market_feed_generation.call(
        task_id=BRAND_1_ID,
        args=[],
        kwargs={'brand_id': BRAND_1_ID},
        expect_fail=False,
    )

    assert not mds_s3_storage.storage


async def test_dsa_title(
        get_first_offer_exact_field,
        load_result_market_feed,
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        set_feeds_settings_dsa_title,
        stq_runner,
):
    set_feeds_settings_dsa_title(MARKET_FEED_SETTINGS_KEY)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [
        products,
        categories,
        generalized_places_products,
    ] = _generate_product_and_category_minimal(brands)
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(generalized_places_products)

    await stq_runner.eats_retail_seo_market_feed_generation.call(
        task_id=BRAND_1_ID,
        args=[],
        kwargs={'brand_id': BRAND_1_ID},
        expect_fail=False,
    )

    result_xml = load_result_market_feed(brands[BRAND_1_ID])
    assert (
        get_first_offer_exact_field(result_xml, field_name='dsa_title')
        == 'DSA_TITLE'
    )


def _set_configs(update_taxi_config):
    update_taxi_config(
        'EATS_NOMENCLATURE_MASTER_TREE',
        {
            'master_tree_settings': {
                BRAND_1_ID: {'assortment_name': 'default_assortment'},
            },
        },
    )
    update_taxi_config(
        'EATS_RETAIL_SEO_FEEDS_SETTINGS',
        {
            MARKET_FEED_SETTINGS_KEY: {
                'allowed_countries': ['Австралия', 'РОССИЯ'],
                'feed_expiration_threshold_in_hours': 336,
                'fallback_picture': {
                    'domain': 'eda.yandex.ru',
                    'relative_url': '/fallback-picture/orig',
                },
            },
        },
    )


def _generate_brands():
    brand_1 = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand_1.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand_1.brand_id,
        ),
        PLACE_2_ID: models.Place(
            place_id=PLACE_2_ID, slug='place1002', brand_id=brand_1.brand_id,
        ),
    }

    return {brand.brand_id: brand for brand in [brand_1]}


def _generate_products_and_categories(brands):
    product_brand_1 = models.ProductBrand('Мираторг')
    product_brand_2 = models.ProductBrand('Агуша&nbsp;')

    barcode_1 = models.Barcode('10205800000')
    barcode_2 = models.Barcode('10205800001')
    barcode_3 = models.Barcode('10205800002')
    barcode_4 = models.Barcode('78905800000')

    picture_1 = models.Picture('product_url_1')
    picture_2 = models.Picture('product_url_2')
    picture_3 = models.Picture('product_url_3')

    product_1 = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-1',
        description='Товар 1<p>Описание</p> <b>Молоко</b>',
        product_brand=product_brand_2,
        vendor_name='Поставщик&nbsp;1',
        vendor_country='Австралия',
        measure_in_milliliters=2000,
        delivery_flag=False,
        pick_flag=True,
    )
    product_1.set_pictures([picture_1])
    product_1.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                price=decimal.Decimal('8'),
                vat=10,
                stocks=100,
                is_available=True,
            ),
        ],
    )
    product_2 = models.Product(
        nomenclature_id='45631b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Конфеты&nbsp;M&m\'s',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-2',
        description='Конфеты&npsp;M&M\'s;<p>шоколадные конфеты</p>',
        vendor_name='Поставщик&nbsp;2',
        vendor_country='Невалидная страна',
        measure_in_grams=100,
        delivery_flag=True,
        pick_flag=False,
    )
    product_2.set_barcodes([barcode_1, barcode_2, barcode_3])
    product_2.set_pictures([picture_2])
    product_2.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                price=decimal.Decimal('99'),
                old_price=decimal.Decimal('95.3'),
                vat=20,
                stocks=0,
                is_available=True,
            ),
        ],
    )
    product_3 = models.Product(
        nomenclature_id='78931b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Колбаса',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-3',
        is_adult=True,
        description='Товар&nbsp;3<BR/>Описание 1<p><B>Описание 2</B>test</p>',
        product_brand=product_brand_1,
        delivery_flag=True,
        pick_flag=True,
    )
    product_3.set_barcodes([barcode_4])
    product_3.set_pictures([picture_2])
    product_3.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                price=decimal.Decimal('50.97'),
                stocks=500,
                is_available=True,
            ),
        ],
    )
    product_4_not_available = models.Product(
        nomenclature_id='89131b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Недоступный товар',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-4',
        is_adult=True,
        description='Товар 4',
        vendor_country='РОССИЯ',
        measure_in_grams=1600,
        delivery_flag=False,
        pick_flag=False,
    )
    product_4_not_available.set_pictures([picture_3])
    product_4_not_available.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                price=decimal.Decimal('20'),
                vat=0,
                stocks=80,
                is_available=False,
            ),
        ],
    )
    product_5_without_image = models.Product(
        nomenclature_id='jkl31b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Товар без картинок',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-5',
    )
    product_5_without_image.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                price=decimal.Decimal('100'),
                vat=20,
                stocks=100,
                is_available=True,
            ),
        ],
    )
    products = [
        product_1,
        product_2,
        product_3,
        product_4_not_available,
        product_5_without_image,
    ]

    category_1 = models.Category(
        category_id='1234', name='Молоко', image_url='cat_url_1234',
    )
    category_1.set_products([product_1])
    category_2 = models.Category(
        category_id='123', name='Молоко & сыр', image_url='cat_url_123',
    )
    category_2.set_child_categories([category_1])
    category_3 = models.Category(
        category_id='789', name='Колбасные&nbsp;изделия',
    )
    category_3.set_products([product_3, product_4_not_available])
    category_4 = models.Category(
        category_id='12', name='Молочные продукты', image_url='cat_url_12',
    )
    category_4.set_child_categories([category_2, category_3])

    category_5 = models.Category(
        category_id='456',
        name='Конфеты&nbsp;<b>шоколадные</b>',
        image_url='cat_url_456',
    )
    category_5.set_products([product_2, product_5_without_image])
    category_6 = models.Category(category_id='45', name='Конфеты')
    category_6.set_child_categories([category_5])

    category_7_without_products = models.Category(
        category_id='1012',
        name='Категория без товаров',
        image_url='cat_url_1012',
    )
    category_8_without_products = models.Category(
        category_id='101', name='Родительская категория без товаров',
    )
    category_8_without_products.set_child_categories(
        [category_7_without_products],
    )

    categories = [category_4, category_6, category_8_without_products]

    generalized_places_product_1 = models.GeneralizedPlacesProduct(
        product=product_1,
        category=category_1,
        price=decimal.Decimal('8'),
        vat=10,
    )
    generalized_places_product_2 = models.GeneralizedPlacesProduct(
        product=product_2,
        category=category_5,
        price=decimal.Decimal('99'),
        old_price=decimal.Decimal('95.3'),
        vat=20,
    )
    generalized_places_product_3 = models.GeneralizedPlacesProduct(
        product=product_3, category=category_3, price=decimal.Decimal('50.97'),
    )
    generalized_places_product_4 = models.GeneralizedPlacesProduct(
        product=product_4_not_available,
        category=category_3,
        price=decimal.Decimal('20'),
        vat=0,
    )
    generalized_places_product_5 = models.GeneralizedPlacesProduct(
        product=product_5_without_image,
        category=category_5,
        price=decimal.Decimal('100'),
        vat=20,
    )
    generalized_places_products = [
        generalized_places_product_1,
        generalized_places_product_2,
        generalized_places_product_3,
        generalized_places_product_4,
        generalized_places_product_5,
    ]

    return [products, categories, generalized_places_products]


def _generate_product_and_category_minimal(brands):
    picture_1 = models.Picture('product_url_1')

    product_1 = models.Product(
        nomenclature_id='00000000-0000-0000-0000-_public_id_1',
        name='Молоко',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-1',
        description='Описание 1',
    )
    product_1.set_pictures([picture_1])

    products = [product_1]

    category_1 = models.Category(
        category_id='1234', name='Молоко', image_url='cat_url_1234',
    )
    category_1.set_products([product_1])

    categories = [category_1]

    generalized_places_product_1 = models.GeneralizedPlacesProduct(
        product=product_1, category=category_1, price=decimal.Decimal('8'),
    )

    generalized_places_products = [generalized_places_product_1]

    return [products, categories, generalized_places_products]
