import datetime

import pytest


TEST_RESTORED = '2021-08-09T10:10:10+00:00'
TEST_DEPLETED = '2021-08-10T11:11:11+00:00'


@pytest.mark.now('2021-08-10T11:11:11+00:00')
async def test_internal_stocks_200(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    """ Check /internal/v1/catalog/v1/stocks
    return stocks in depot by product_id;
    also check that product missed in depot cache is not returned
    """
    depot = None
    products = []
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        mock_grocery_depots.add_depot(depot)
        products.append(
            category.add_product(
                product_id=1,
                in_stock=5,
                depleted=TEST_DEPLETED,
                restored=TEST_RESTORED,
            ),
        )
        products.append(
            category.add_product(
                product_id=2,
                in_stock=0,
                depleted=TEST_DEPLETED,
                restored=TEST_RESTORED,
            ),
        )
        products.append(
            category.add_product(
                product_id=3,
                in_stock=0,
                checkout_limit=5,
                depleted=TEST_DEPLETED,
                restored=TEST_RESTORED,
            ),
        )
        products.append(
            category.add_product(
                product_id=4,
                in_stock=10,
                checkout_limit=0,
                depleted=TEST_DEPLETED,
                restored=TEST_RESTORED,
            ),
        )
        products.append(
            category.add_product(
                product_id=5,
                in_stock=10,
                checkout_limit=5,
                depleted=TEST_DEPLETED,
                restored=TEST_RESTORED,
            ),
        )
        products.append(
            category.add_product(
                product_id=6,
                in_stock=5,
                checkout_limit=10,
                depleted=TEST_DEPLETED,
                restored=TEST_RESTORED,
            ),
        )

    # product missed in depot stocks: it must not appear in the response
    some_product_id = '88b4b661-aa33-11e9-b7ff-ac1f6b8569b3'

    product_ids = list(map(lambda item: item.id_wms, products))
    product_ids.append(some_product_id)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/stocks',
        json={'product_ids': product_ids, 'depot_id': depot.id_wms},
    )
    assert response.status_code == 200
    actual_products = []
    expected_products = list(map(lambda x: x.id_wms, products))
    for i, stock in enumerate(response.json()['stocks']):
        assert stock['in_stock'] == str(products[i].in_stock)
        assert stock['product_id'] == products[i].id_wms
        assert stock['restored'] == TEST_RESTORED
        assert stock['depleted'] == TEST_DEPLETED
        if (
                products[i].checkout_limit is None
                or products[i].checkout_limit < 1
        ):
            assert stock['quantity_limit'] == str(products[i].in_stock)
        else:
            assert stock['quantity_limit'] == str(
                min(products[i].in_stock, products[i].checkout_limit),
            )
        actual_products.append(stock['product_id'])
    assert expected_products == actual_products


@pytest.mark.now(f'{datetime.datetime(2020, 12, 1, 1, 1, 1)}Z')
@pytest.mark.parametrize(
    'depleted, can_show',
    [
        (datetime.datetime(2019, 12, 1, 1, 1, 1), False),
        (datetime.datetime(2021, 12, 1, 1, 1, 1), True),
    ],
)
async def test_internal_stock_can_show_flag(
        taxi_overlord_catalog,
        overlord_db,
        depleted,
        can_show,
        mock_grocery_depots,
):
    depot = None
    products = []
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        mock_grocery_depots.add_depot(depot)
        products.append(
            category.add_product(product_id=1, in_stock=0, depleted=depleted),
        )
        category.add_product(product_id=2, in_stock=1, depleted=depleted)

    product_ids = list(map(lambda item: item.id_wms, products))
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/stocks',
        json={'product_ids': product_ids, 'depot_id': depot.id_wms},
    )
    assert response.json()['stocks'][0]['can_be_shown'] == can_show


async def test_internal_stocks_404(taxi_overlord_catalog, overlord_db):
    """ Check /internal/v1/catalog/v1/stocks
    return 404 when depot not found
    """
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/stocks',
        json={'product_ids': ['123456'], 'depot_id': 'depot-not-found-id'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DEPOT_NOT_FOUND'


# Проверяем, что продукт без активной категории не попадает в выдачу
@pytest.mark.now('2021-08-10T11:11:11+00:00')
@pytest.mark.parametrize(
    'check_for_category_availability', [True, False, None],
)
async def test_internal_stocks_check_category_availability(
        taxi_overlord_catalog,
        overlord_db,
        mock_grocery_depots,
        check_for_category_availability,
):
    depot = None
    products = []
    expected_products = []
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category_1 = depot.add_category(category_id=1)
        category_2 = depot.add_category(
            category_id=2, timetable=['12:00', '13:00'],
        )
        mock_grocery_depots.add_depot(depot)
        available_product = category_1.add_product(
            product_id=1,
            in_stock=5,
            depleted=TEST_DEPLETED,
            restored=TEST_RESTORED,
        )
        products.append(available_product.id_wms)
        expected_products.append(available_product.id_wms)
        unavailable_product = category_2.add_product(
            product_id=7,
            in_stock=5,
            checkout_limit=10,
            depleted=TEST_DEPLETED,
            restored=TEST_RESTORED,
        )
        products.append(unavailable_product.id_wms)
        if (
                check_for_category_availability is None
                or not check_for_category_availability
        ):
            expected_products.append(unavailable_product.id_wms)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/stocks',
        json={
            'product_ids': products,
            'depot_id': depot.id_wms,
            'check_for_category_availability': check_for_category_availability,
        },
    )
    assert response.status_code == 200
    actual_products = []
    for stock in response.json()['stocks']:
        actual_products.append(stock['product_id'])
    assert expected_products == actual_products
