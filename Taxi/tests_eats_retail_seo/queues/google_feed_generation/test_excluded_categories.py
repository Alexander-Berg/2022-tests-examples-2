import decimal

from ... import models


BRAND_1_ID = '771'
PLACE_1_ID = '1001'
SOME_PARENT_CATEGORY_EXCLUDED_BY_ID = '123'
SOME_CHILD_CATEGORY_EXCLUDED_BY_ID = '456'
SOME_PARENT_CATEGORY_EXCLUDED_BY_TAG = '321'
SOME_CHILD_CATEGORY_EXCLUDED_BY_TAG = '654'
TAG_TO_EXCLUDE_BY = 'Тег 1'
GOOGLE_FEED_SETTINGS_KEY = 'google_feed'


async def test_excluded_categories(
        load,
        load_result_google_feed,
        normalize_google_feed_xml,
        save_brands_to_db,
        save_tags_to_db,
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
        tag_to_exclude_by,
    ] = _generate_products_and_categories(brands)
    save_products_to_db(products)
    save_tags_to_db([tag_to_exclude_by])
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(generalized_places_products)

    await stq_runner.eats_retail_seo_google_feed_generation.call(
        task_id=BRAND_1_ID,
        args=[],
        kwargs={'brand_id': BRAND_1_ID},
        expect_fail=False,
    )

    result_xml = load_result_google_feed(brands[BRAND_1_ID])
    expected_xml = load('expected_feed.xml')

    assert normalize_google_feed_xml(result_xml) == normalize_google_feed_xml(
        expected_xml,
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
            GOOGLE_FEED_SETTINGS_KEY: {
                'allowed_countries': [],
                'feed_expiration_threshold_in_hours': 336,
                'categories_ids_to_exclude': [
                    SOME_PARENT_CATEGORY_EXCLUDED_BY_ID,
                    SOME_CHILD_CATEGORY_EXCLUDED_BY_ID,
                ],
                'categories_tags_to_exclude': [TAG_TO_EXCLUDE_BY],
            },
        },
    )


def _generate_brands():
    brand_1 = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand_1.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand_1.brand_id,
        ),
    }

    return {brand.brand_id: brand for brand in [brand_1]}


def _generate_products_and_categories(brands):
    picture_1 = models.Picture('product_url_1')
    picture_2 = models.Picture('product_url_2')
    picture_3 = models.Picture('product_url_3')
    picture_4 = models.Picture('product_url_4')
    picture_5 = models.Picture('product_url_5')
    picture_6 = models.Picture('product_url_6')

    product_1 = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-1',
    )
    product_1.set_pictures([picture_1])
    product_2 = models.Product(
        nomenclature_id='45631b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Конфеты M&ms',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-2',
    )
    product_2.set_pictures([picture_2])
    product_3 = models.Product(
        nomenclature_id='78931b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Колбаса',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-3',
    )
    product_3.set_pictures([picture_2])
    product_4 = models.Product(
        nomenclature_id='89131b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Сервелат',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-4',
    )
    product_4.set_pictures([picture_3])
    product_5 = models.Product(
        nomenclature_id='jkl31b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Конфеты шоколадные',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-5',
    )

    product_6 = models.Product(
        nomenclature_id='11131b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко (для тегов)',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-6',
    )
    product_6.set_pictures([picture_4])
    product_7 = models.Product(
        nomenclature_id='22231b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Конфеты M&ms (для тегов)',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-7',
    )
    product_7.set_pictures([picture_5])
    product_8 = models.Product(
        nomenclature_id='33331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Колбаса (для тегов)',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-8',
    )
    product_8.set_pictures([picture_5])
    product_9 = models.Product(
        nomenclature_id='44431b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Сервелат (для тегов)',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-9',
    )
    product_9.set_pictures([picture_6])
    product_10 = models.Product(
        nomenclature_id='55531b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Конфеты шоколадные (для тегов)',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-10',
    )
    products = [
        product_1,
        product_2,
        product_3,
        product_4,
        product_5,
        product_6,
        product_7,
        product_8,
        product_9,
        product_10,
    ]

    category_1 = models.Category(
        category_id='1234', name='Молоко', image_url='cat_url_1234',
    )
    category_1.set_products([product_1])
    category_2_excluded = models.Category(
        category_id=SOME_PARENT_CATEGORY_EXCLUDED_BY_ID,
        name='Молоко & сыр',
        image_url='cat_url_123',
    )
    category_2_excluded.set_child_categories([category_1])
    category_3 = models.Category(
        category_id='789', name='Колбасные&nbsp;изделия',
    )
    category_3.set_products([product_3, product_4])
    category_4 = models.Category(
        category_id='12', name='Молочные продукты', image_url='cat_url_12',
    )
    category_4.set_child_categories([category_2_excluded, category_3])

    category_5_excluded = models.Category(
        category_id=SOME_CHILD_CATEGORY_EXCLUDED_BY_ID,
        name='Конфеты&nbsp;<b>шоколадные</b>',
        image_url='cat_url_456',
    )
    category_5_excluded.set_products([product_2, product_5])
    category_6 = models.Category(category_id='45', name='Конфеты')
    category_6.set_child_categories([category_5_excluded])

    tag_to_exclude_by = models.Tag(name=TAG_TO_EXCLUDE_BY)
    category_7 = models.Category(
        category_id='1111',
        name='Молоко (для тегов)',
        image_url='cat_url_1111',
    )
    category_7.set_products([product_6])
    category_8_excluded = models.Category(
        category_id=SOME_PARENT_CATEGORY_EXCLUDED_BY_TAG,
        name='Молоко & сыр (для тегов)',
        image_url='cat_url_321',
    )
    category_8_excluded.add_tag(tag_to_exclude_by)
    category_8_excluded.set_child_categories([category_7])
    category_9 = models.Category(
        category_id='2222', name='Колбасные&nbsp;изделия (для тегов)',
    )
    category_9.set_products([product_8, product_9])
    category_10 = models.Category(
        category_id='3333',
        name='Молочные продукты (для тегов)',
        image_url='cat_url_3333',
    )
    category_10.set_child_categories([category_8_excluded, category_9])

    category_11_excluded = models.Category(
        category_id=SOME_CHILD_CATEGORY_EXCLUDED_BY_TAG,
        name='Конфеты&nbsp;<b>шоколадные</b> (для тегов)',
        image_url='cat_url_654',
    )
    category_11_excluded.add_tag(tag_to_exclude_by)
    category_11_excluded.set_products([product_7, product_10])
    category_12 = models.Category(
        category_id='4444', name='Конфеты (для тегов)',
    )
    category_12.set_child_categories([category_11_excluded])

    categories = [category_4, category_6, category_10, category_12]

    generalized_places_product_1 = models.GeneralizedPlacesProduct(
        product=product_1, category=category_1, price=decimal.Decimal('100'),
    )
    generalized_places_product_2 = models.GeneralizedPlacesProduct(
        product=product_2,
        category=category_5_excluded,
        price=decimal.Decimal('100'),
    )
    generalized_places_product_3 = models.GeneralizedPlacesProduct(
        product=product_3, category=category_3, price=decimal.Decimal('100'),
    )
    generalized_places_product_4 = models.GeneralizedPlacesProduct(
        product=product_4, category=category_3, price=decimal.Decimal('100'),
    )
    generalized_places_product_5 = models.GeneralizedPlacesProduct(
        product=product_5,
        category=category_5_excluded,
        price=decimal.Decimal('100'),
    )

    generalized_places_product_6 = models.GeneralizedPlacesProduct(
        product=product_6, category=category_7, price=decimal.Decimal('100'),
    )
    generalized_places_product_7 = models.GeneralizedPlacesProduct(
        product=product_7,
        category=category_11_excluded,
        price=decimal.Decimal('100'),
    )
    generalized_places_product_8 = models.GeneralizedPlacesProduct(
        product=product_8, category=category_9, price=decimal.Decimal('100'),
    )
    generalized_places_product_9 = models.GeneralizedPlacesProduct(
        product=product_9, category=category_9, price=decimal.Decimal('100'),
    )
    generalized_places_product_10 = models.GeneralizedPlacesProduct(
        product=product_10,
        category=category_11_excluded,
        price=decimal.Decimal('100'),
    )

    generalized_places_products = [
        generalized_places_product_1,
        generalized_places_product_2,
        generalized_places_product_3,
        generalized_places_product_4,
        generalized_places_product_5,
        generalized_places_product_6,
        generalized_places_product_7,
        generalized_places_product_8,
        generalized_places_product_9,
        generalized_places_product_10,
    ]

    return [
        products,
        categories,
        generalized_places_products,
        tag_to_exclude_by,
    ]
