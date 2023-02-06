import datetime as dt
import decimal

import pytest
import pytz

from . import models


MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)
PERIODIC_NAME = 'generate-top-products-feeds-periodic'
TOP_PRODUCTS_FEEDS_SETTINGS_KEY = 'generate-top-products-feeds-periodic'
TOP_PRODUCTS_FEEDS_S3_DIR = 'top_products'
FEED_NAMES = [
    'one_brand_one_category_feed',
    'one_brand_two_categories_feed',
    'two_brands_one_category_feed',
    'two_brands_two_categories_feed',
    'two_brands_two_categories_with_several_products_feed',
]
EMPTY_FEED_NAME = ['empty_feed']
BRAND_1_ID = '771'
BRAND_2_ID = '772'
PLACE_1_ID = '1001'
PLACE_2_ID = '2001'


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_top_products_schema.yaml'],
    static_table_data=['yt_top_products_data.yaml'],
)
async def test_generate_top_products_feeds(
        enable_periodic_in_config,
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        load,
        load_expected_market_feed,
        mds_s3_storage,
        normalize_market_feed_xml,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(PERIODIC_NAME)

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

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert periodic_finished.times_called == 1

    s3_dir = TOP_PRODUCTS_FEEDS_S3_DIR
    result_feeds_list = mds_s3_storage.storage[
        f'{s3_dir}/feeds_list.txt'
    ].data.decode('utf-8')
    assert set(result_feeds_list.split()) == {
        f'{s3_dir}/{feed_name}.xml' for feed_name in FEED_NAMES
    }

    for feed_name in FEED_NAMES[1:]:
        result_xml = mds_s3_storage.storage[
            f'{s3_dir}/{feed_name}.xml'
        ].data.decode('utf-8')
        expected_xml = load_expected_market_feed(
            load(f'{feed_name}.xml'), MOCK_NOW,
        )
        assert normalize_market_feed_xml(
            result_xml,
        ) == normalize_market_feed_xml(expected_xml)


@pytest.mark.yt(
    schemas=['yt_top_products_schema.yaml'],
    static_table_data=['yt_top_products_data_empty_feed.yaml'],
)
async def test_empty_top_products_feed(
        enable_periodic_in_config,
        mds_s3_storage,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(PERIODIC_NAME)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert periodic_finished.times_called == 0
    assert mds_s3_storage.storage == {}


@pytest.mark.yt(schemas=['yt_top_products_schema.yaml'])
async def test_empty_feeds_list(
        enable_periodic_in_config,
        mds_s3_storage,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply_force,
):
    # check that empty feeds list doesn't upload
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(PERIODIC_NAME)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert periodic_finished.times_called == 0
    assert mds_s3_storage.storage == {}


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_top_products_schema.yaml'],
    static_table_data=['yt_top_products_data_for_dsa_title.yaml'],
)
async def test_dsa_title(
        enable_periodic_in_config,
        get_first_offer_exact_field,
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        set_feeds_settings_dsa_title,
        mds_s3_storage,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(PERIODIC_NAME)
    set_feeds_settings_dsa_title(TOP_PRODUCTS_FEEDS_SETTINGS_KEY)

    brands = _generate_brands_minimal()
    save_brands_to_db(list(brands.values()))

    [
        products,
        categories,
        generalized_places_products,
    ] = _generate_products_and_categories_minimal(brands)
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(generalized_places_products)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert periodic_finished.times_called == 1

    s3_dir = TOP_PRODUCTS_FEEDS_S3_DIR

    result_xml = mds_s3_storage.storage[f'{s3_dir}/top_feed.xml'].data.decode(
        'utf-8',
    )

    assert (
        get_first_offer_exact_field(result_xml, field_name='dsa_title')
        == 'DSA_TITLE'
    )


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _generate_brands():
    brand_1 = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand_1.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand_1.brand_id,
        ),
    }
    brand_2 = models.Brand(brand_id=BRAND_2_ID, slug='lenta', name='Лента')
    brand_2.places = {
        PLACE_2_ID: models.Place(
            place_id=PLACE_2_ID, slug='place2001', brand_id=brand_2.brand_id,
        ),
    }

    return {brand.brand_id: brand for brand in [brand_1, brand_2]}


def _generate_brands_minimal():
    brand_1 = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand_1.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand_1.brand_id,
        ),
    }

    return {brand.brand_id: brand for brand in [brand_1]}


def _generate_products_and_categories(brands):
    picture_1 = models.Picture('product_url_1')

    product_1 = models.Product(
        nomenclature_id='00000000-0000-0000-0000-_public_id_1',
        name='Молоко',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-1',
        description='Описание 1',
    )
    product_1.set_pictures([picture_1])

    product_2 = models.Product(
        nomenclature_id='00000000-0000-0000-0000-_public_id_2',
        name='Молоко',
        brand=brands[BRAND_2_ID],
        origin_id='item-origin-id-2',
        description='Описание 2',
    )
    product_2.set_pictures([picture_1])

    product_3 = models.Product(
        nomenclature_id='00000000-0000-0000-0000-_public_id_3',
        name='Сыр Легкий',
        brand=brands[BRAND_2_ID],
        origin_id='item-origin-id-3',
        description='Описание 3',
    )
    product_3.set_pictures([picture_1])

    products = [product_1, product_2, product_3]

    category_1 = models.Category(
        category_id='1234', name='Молоко', image_url='cat_url_1234',
    )
    category_1.set_products([product_1, product_2])
    category_2 = models.Category(
        category_id='1235', name='Сыр', image_url='cat_url_1235',
    )
    category_2.set_products([product_3])
    category_3 = models.Category(
        category_id='123', name='Молоко & сыр', image_url='cat_url_123',
    )
    category_3.set_child_categories([category_1, category_2])

    categories = [category_3]

    generalized_places_product_1 = models.GeneralizedPlacesProduct(
        product=product_1, category=category_1, price=decimal.Decimal('8'),
    )
    generalized_places_product_2 = models.GeneralizedPlacesProduct(
        product=product_2, category=category_1, price=decimal.Decimal('99'),
    )
    generalized_places_product_3 = models.GeneralizedPlacesProduct(
        product=product_3, category=category_2, price=decimal.Decimal('50.97'),
    )

    generalized_places_products = [
        generalized_places_product_1,
        generalized_places_product_2,
        generalized_places_product_3,
    ]

    return [products, categories, generalized_places_products]


def _generate_products_and_categories_minimal(brands):
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
