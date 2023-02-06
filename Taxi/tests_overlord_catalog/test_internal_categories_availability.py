# pylint: disable=import-error
from grocery_mocks import grocery_menu as mock_grocery_menu
import pytest


async def test_internal_categories_availability_status(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    """ Check /internal/v1/catalog/v1/categories-availability
    check categories availability by status
    Category is available only if it is active
    """
    depot = None
    categories = []
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        categories.append(depot.add_category(category_id=1, status='active'))
        categories[-1].add_product(product_id=1)
        categories.append(depot.add_category(category_id=2, status='disabled'))
        categories[-1].add_product(product_id=2)
        categories.append(depot.add_category(category_id=3, status='removed'))
        categories[-1].add_product(product_id=3)
        mock_grocery_depots.add_depot(depot)

    category_ids = list(map(lambda item: item.id_wms, categories))

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/categories-availability',
        json={'category_ids': category_ids, 'depot_id': depot.id_wms},
    )
    assert response.status_code == 200
    for i, category in enumerate(response.json()['categories']):
        assert category['category_id'] == categories[i].id_wms
        assert category['available'] == (categories[i].status == 'active')


@pytest.mark.parametrize(
    'request_time,available_categories',
    [
        (None, {0, 1}),
        ('2020-08-19T09:00:00.00+03:00', {0, 1, 2}),
        ('2020-08-19T12:00:00.00+03:00', {0, 1}),
        ('2020-08-19T17:00:00.00+03:00', {0}),
    ],
)
@pytest.mark.now('2020-08-19T12:00:00.00+03:00')
async def test_internal_categories_availability_timetable(
        taxi_overlord_catalog,
        overlord_db,
        request_time,
        available_categories,
        mock_grocery_depots,
):
    """ Check /internal/v1/catalog/v1/categories-availability
    check categories availability by timetable
    Category is available only if request_time is inside timetable
    If no request_time in request - falling back to current server time
    """
    depot = None
    categories = []
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        categories.append(depot.add_category(category_id=1, timetable=None))
        categories[-1].add_product(product_id=1)

        categories.append(
            depot.add_category(category_id=2, timetable=['08:00', '15:00']),
        )
        categories[-1].add_product(product_id=2)

        categories.append(
            depot.add_category(
                category_id=3, status='active', timetable=['08:00', '10:00'],
            ),
        )
        categories[-1].add_product(product_id=3)
        mock_grocery_depots.add_depot(depot)

    category_ids = list(map(lambda item: item.id_wms, categories))

    request_json = {'category_ids': category_ids, 'depot_id': depot.id_wms}
    if request_time is not None:
        request_json['request_time'] = request_time

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/categories-availability', json=request_json,
    )
    assert response.status_code == 200
    for i, category in enumerate(response.json()['categories']):
        assert category['category_id'] == categories[i].id_wms
        assert category['available'] == (i in available_categories)


@pytest.mark.now('2020-08-19T12:00:00.00+03:00')
@pytest.mark.config(OVERLORD_CATALOG_SHOW_SOLDOUT_SUBCATEGORIES=True)
async def test_internal_categories_availability_stocks(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    """ Check /internal/v1/catalog/v1/categories-availability
    check categories availability by products stocks
    Category is available only if there is at least one product
    with stocks or with can_be_shown=true
    """
    depot = None
    categories = []
    available_categories = set()
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        categories.append(depot.add_category(category_id=1))
        categories[-1].add_product(product_id=1)
        available_categories.add(categories[-1].id_wms)

        categories.append(depot.add_category(category_id=2))
        categories[-1].add_product(product_id=2, in_stock=0)

        categories.append(depot.add_category(category_id=3))
        mock_grocery_depots.add_depot(depot)

        categories.append(depot.add_category(category_id=5))
        categories[-1].add_product(
            product_id=4, in_stock=0, depleted='2020-08-19T12:00:00.00+03:00',
        )
        available_categories.add(categories[-1].id_wms)

        categories.append(depot.add_category(category_id=6))
        categories[-1].add_product(
            product_id=5, in_stock=0, depleted='2020-08-10T12:00:00.00+03:00',
        )

    category_ids = list(map(lambda item: item.id_wms, categories))

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/categories-availability',
        json={'category_ids': category_ids, 'depot_id': depot.id_wms},
    )
    assert response.status_code == 200
    for i, category in enumerate(response.json()['categories']):
        assert category['category_id'] == categories[i].id_wms
        assert category['available'] == (
            category['category_id'] in available_categories
        )


# категория является доступной если в ней есть хотя бы один комбо товар
async def test_internal_categories_availability_with_combo_product(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots, grocery_menu,
):
    depot = None
    product = None
    category_1 = None
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        mock_grocery_depots.add_depot(depot)
        category_1 = depot.add_category(category_id=1)
        product = category_1.add_product(
            product_id=2, price=0, in_stock=None, set_default_stock=False,
        )
        category_2 = depot.add_category(category_id=2)
        category_2.add_product(product_id=3)

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'COMBO_ID', [product.id_wms], [], 'combo_revision',
        ),
    )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/categories-availability',
        json={'category_ids': [category_1.id_wms], 'depot_id': depot.id_wms},
    )
    assert response.status_code == 200
    response_category = response.json()['categories'][0]
    assert response_category['category_id'] == category_1.id_wms
    assert response_category['available']
