import pytest

from tests_grocery_uber_gw import models

MENU_SYNC_SETTINGS = {'enabled': True, 'period_seconds': 60}
DEPOTS_MAPPING_SETTINGS = {'enabled': True, 'limit': 1}


@pytest.mark.config(GROCERY_UBER_GW_MENU_SYNC_SETTINGS=MENU_SYNC_SETTINGS)
@pytest.mark.suspend_periodic_tasks('menu-sync-periodic')
async def test_basic(taxi_grocery_uber_gw, grocery_uber_gw_db, testpoint):
    """ Menu sync should work if enabled by config """

    grocery_uber_gw_db.flush_distlocks()

    @testpoint('menu-sync-result')
    def menu_sync_testpoint(data):
        pass

    await taxi_grocery_uber_gw.run_periodic_task('menu-sync-periodic')

    assert menu_sync_testpoint.times_called == 1


@pytest.mark.experiments3(
    name='grocery_uber_gw_menu_sync',
    consumers=['grocery-uber-gw/periodic-tasks'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'sync_stocks': True},
        },
    ],
    is_config=True,
)
@pytest.mark.config(
    GROCERY_UBER_GW_DEPOTS_MAPPING_SETTINGS=DEPOTS_MAPPING_SETTINGS,
)
@pytest.mark.config(GROCERY_UBER_GW_MENU_SYNC_SETTINGS=MENU_SYNC_SETTINGS)
@pytest.mark.suspend_periodic_tasks('menu-sync-periodic')
@pytest.mark.now('2020-02-02T10:21:00+00:00')
async def test_sync_stocks(
        taxi_grocery_uber_gw,
        grocery_uber_gw_db,
        mock_uber_api,
        overlord_catalog,
        grocery_depots,
        mockserver,
):
    """ items availability syncs properly """

    uber_store_id = '01234567-89ab-cdef-0123-456789abcdef'
    grocery_depot_id = 'deli_id_1'

    grocery_depots.add_depot(
        depot_test_id=1,
        depot_id=grocery_depot_id,
        legacy_depot_id=grocery_depot_id,
    )

    products = [
        {
            'product_id': 'available-in_stock',
            'in_stock': '10',
            'suspend_until': None,
        },
        {
            'product_id': 'available-not_in_stock',
            'in_stock': '0',
            'suspend_until': None,
        },
        {
            'product_id': 'suspened-in_stock',
            'in_stock': '10',
            'suspend_until': 2212811432,
        },
        {
            'product_id': 'suspended-not_in_stock',
            'in_stock': '0',
            'suspend_until': 2212811432,
        },
    ]
    new_products_stocks = []
    uber_items = []
    for product in products:
        new_products_stocks.append(
            {
                'product_id': product['product_id'],
                'in_stock': product['in_stock'],
                'quantity_limit': product['in_stock'],
            },
        )
        uber_items.append(
            models.MenuItem(
                item_id=product['product_id'],
                suspend_until=product['suspend_until'],
                title={'en': product['product_id']},
            ),
        )

    overlord_catalog.add_products_stocks(
        depot_id=grocery_depot_id, new_products_stocks=new_products_stocks,
    )

    stores = [
        models.Store(
            store_id=uber_store_id, merchant_store_id=grocery_depot_id,
        ),
    ]
    menus = [models.Menu(store_id=uber_store_id, items=uber_items)]

    mock_uber_api_payload = {'stores': {}, 'menus': {}}
    for store in stores:
        mock_uber_api_payload['stores'][store.store_id] = store
    for menu in menus:
        mock_uber_api_payload['menus'][menu.store_id] = menu

    mock_uber_api.set_payload(mock_uber_api_payload)

    grocery_uber_gw_db.flush_distlocks()

    await taxi_grocery_uber_gw.invalidate_caches()

    @mockserver.json_handler(
        '/uber-api/v2/eats/stores/{}/menus/items'
        '/available-not_in_stock'.format(uber_store_id),
    )
    def _mock_suspend_item(request):
        assert 'Authorization' in request.headers
        assert (
            request.json['suspension_info']['suspension']['suspend_until'] > 0
        )
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/uber-api/v2/eats/stores/{}/menus/items/suspened-in_stock'.format(
            uber_store_id,
        ),
    )
    def _mock_make_item_available(request):
        assert 'Authorization' in request.headers
        assert (
            request.json['suspension_info']['suspension']['suspend_until'] == 0
        )
        return mockserver.make_response(status=204)

    await taxi_grocery_uber_gw.run_periodic_task('menu-sync-periodic')

    assert _mock_suspend_item.times_called == 1
    assert _mock_make_item_available.times_called == 1
