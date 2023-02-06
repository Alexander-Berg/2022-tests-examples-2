import decimal

import pytest

from .. import models
from .. import utils


PERIODIC_NAME = 'fill-generalized-places-products-periodic'
BRAND_1_ID = '771'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'


@pytest.mark.parametrize(**utils.gen_bool_params('is_available'))
async def test_place_product_choice(
        assert_objects_lists,
        enable_periodic_in_config,
        get_generalized_places_products_from_db,
        save_brands_to_db,
        save_categories_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
        # parametrize params
        is_available,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(PERIODIC_NAME)

    brand = _generate_brand()
    save_brands_to_db([brand])

    [
        products,
        categories,
        expected_generalized_places_products,  # pylint: disable=C0103
    ] = _generate_data(brand, is_available)
    save_products_to_db(products)
    save_categories_to_db(categories)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert_objects_lists(
        get_generalized_places_products_from_db(),
        expected_generalized_places_products,
    )

    assert periodic_finished.times_called == 1


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


def _generate_data(brand, is_available):
    product_1 = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Товар 1',
        brand=brand,
        origin_id='item-origin-id-1',
    )
    product_1.set_product_in_places(
        [
            models.ProductInPlace(
                place=brand.places[PLACE_1_ID],
                price=decimal.Decimal('80'),
                vat=10,
                stocks=100,
                is_available=True,
            ),
            models.ProductInPlace(
                place=brand.places[PLACE_2_ID],
                # будут взяты данные из этого магазина,
                # независимо от доступности товара,
                # т.к. в этом магазине цена у товара максимальная
                price=decimal.Decimal('99'),
                old_price=decimal.Decimal('95.3'),
                vat=20,
                stocks=50,
                is_available=is_available,
            ),
        ],
    )
    products = [product_1]

    category_1 = models.Category(category_id='123', name='Молоко')
    category_1.set_products([product_1])
    categories = [category_1]

    generalized_places_product_1 = (  # pylint: disable=C0103
        models.GeneralizedPlacesProduct(
            product=product_1,
            category=category_1,
            price=decimal.Decimal('99'),
            old_price=decimal.Decimal('95.3'),
            vat=20,
        )
    )
    expected_generalized_places_products = [  # pylint: disable=C0103
        generalized_places_product_1,
    ]

    return [products, categories, expected_generalized_places_products]
