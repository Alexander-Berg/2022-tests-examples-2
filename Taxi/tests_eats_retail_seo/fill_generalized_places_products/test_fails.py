import decimal

from .. import models


PERIODIC_NAME = 'fill-generalized-places-products-periodic'
BRAND_1_ID = '771'
BRAND_2_ID = '772'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'
PLACE_3_ID = '1003'


async def test_brand_fails(
        assert_objects_lists,
        enable_periodic_in_config,
        get_generalized_places_products_from_db,
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    @testpoint('fill-generalized-places-products-for-brand::fail')
    def brand_failed(param):
        return {'inject_failure': True, 'brand_id': BRAND_1_ID}

    enable_periodic_in_config(PERIODIC_NAME)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [
        products,
        categories,
        initial_generalized_places_products,  # pylint: disable=C0103
        expected_generalized_places_products,  # pylint: disable=C0103
    ] = _generate_data(brands)
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(initial_generalized_places_products)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert_objects_lists(
        get_generalized_places_products_from_db(),
        expected_generalized_places_products,
    )

    assert brand_failed.has_calls
    assert not periodic_finished.has_calls


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

    brand_2 = models.Brand(
        brand_id=BRAND_2_ID,
        slug='auchan_gipermarket',
        name='Ашан Гипермаркет',
    )
    brand_2.places = {
        PLACE_3_ID: models.Place(
            place_id=PLACE_3_ID, slug='place1003', brand_id=brand_2.brand_id,
        ),
    }

    return {brand.brand_id: brand for brand in [brand_1, brand_2]}


def _generate_data(brands):
    product_1 = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Товар 1',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-1',
    )
    product_1.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                price=decimal.Decimal('40.5'),
                old_price=decimal.Decimal('50.6'),
                vat=20,
                stocks=100,
                is_available=True,
            ),
        ],
    )
    product_2 = models.Product(
        nomenclature_id='45631b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Товар 2',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-2',
    )
    product_2.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                price=decimal.Decimal('40.5'),
                old_price=decimal.Decimal('50.6'),
                vat=20,
                stocks=50,
                is_available=True,
            ),
        ],
    )
    product_3_second_brand = models.Product(
        nomenclature_id='78931b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Товар 3',
        brand=brands[BRAND_2_ID],
        origin_id='item-origin-id-3',
    )
    product_3_second_brand.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_2_ID].places[PLACE_3_ID],
                price=decimal.Decimal('123.4'),
                vat=20,
                stocks=10,
                is_available=True,
            ),
        ],
    )
    products = [product_1, product_2, product_3_second_brand]

    category_1 = models.Category(category_id='123', name='Молоко')
    category_1.set_products([product_1])
    category_2 = models.Category(category_id='456', name='Колбасные изделия')
    category_2.set_products([product_2, product_3_second_brand])
    categories = [category_1, category_2]

    generalized_places_product_1_change_skipped = (  # pylint: disable=C0103
        models.GeneralizedPlacesProduct(
            product=product_1,
            category=category_1,
            price=decimal.Decimal('100'),
            vat=10,
        )
    )
    initial_generalized_places_products = [  # pylint: disable=C0103
        generalized_places_product_1_change_skipped,
    ]

    generalized_places_product_3_new = (  # pylint: disable=C0103
        models.GeneralizedPlacesProduct(
            product=product_3_second_brand,
            category=category_2,
            price=decimal.Decimal('123.4'),
            vat=20,
        )
    )
    expected_generalized_places_products = [  # pylint: disable=C0103
        generalized_places_product_1_change_skipped,
        # generalized_place_product_2_new_skipped,
        generalized_places_product_3_new,
    ]

    return [
        products,
        categories,
        initial_generalized_places_products,
        expected_generalized_places_products,
    ]
