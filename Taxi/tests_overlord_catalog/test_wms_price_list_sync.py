import pytest


@pytest.mark.pgsql('overlord_catalog', files=[])
@pytest.mark.suspend_periodic_tasks('wms-price-lists-sync-periodic')
async def test_happy_path(taxi_overlord_catalog, pgsql, mockserver, load_json):
    price_lists = load_json('wms_price_list_response.json')
    price_list_items = load_json('wms_price_list_items_response.json')

    @mockserver.json_handler('/grocery-wms/api/external/price_lists/v1/list')
    def mock_price_lists(request):
        if request.json['cursor']:
            return load_json(
                'wms_price_list_response_{}.json'.format(
                    request.json['cursor'],
                ),
            )
        return price_lists

    @mockserver.json_handler(
        '/grocery-wms/api/external/price_lists/v1/products',
    )
    def mock_price_list_items(request):
        if request.json['cursor']:
            return load_json(
                'wms_price_list_items_response_{}.json'.format(
                    request.json['cursor'],
                ),
            )
        return price_list_items

    await taxi_overlord_catalog.run_periodic_task(
        'wms-price-lists-sync-periodic',
    )

    assert mock_price_lists.times_called == 2
    assert mock_price_list_items.times_called == 2

    db = pgsql['overlord_catalog']
    cursor = db.cursor()

    cursor.execute('SELECT count(*) from catalog_wms.price_lists')
    (count,) = cursor.fetchall()[0]
    assert count == len(price_lists['price_lists'])

    cursor.execute('SELECT count(*) from catalog_wms.price_list_items')
    (count,) = cursor.fetchall()[0]
    assert count == sum(
        [
            len(pli['prices'])
            for pli in price_list_items['price_list_products']
        ],
    )

    # check last cursors were saved
    cursor.execute(
        'SELECT cursor from catalog_wms.cursors '
        'WHERE name=\'/api/external/price_lists/v1/list\'',
    )
    (result,) = cursor.fetchall()[0]
    assert result == 'done'

    cursor.execute(
        'SELECT cursor from catalog_wms.cursors '
        'WHERE name=\'/api/external/price_lists/v1/products\'',
    )
    (result,) = cursor.fetchall()[0]
    assert result == 'done'


# We add a product with both shelf_types and make sure
# we dont delete both shelf_types when only one is removed
@pytest.mark.pgsql(
    'overlord_catalog', files=['store_and_markdown_price_list_item.sql'],
)
@pytest.mark.suspend_periodic_tasks('wms-price-lists-sync-periodic')
async def test_delete_price_for_shelf_type(
        taxi_overlord_catalog, pgsql, mockserver,
):
    @mockserver.json_handler('/grocery-wms/api/external/price_lists/v1/list')
    def _mock_price_lists(request):
        return {'code': 'OK', 'cursor': 'done', 'price_lists': []}

    @mockserver.json_handler(
        '/grocery-wms/api/external/price_lists/v1/products',
    )
    def _mock_price_list_items(request):
        if request.json['cursor']:
            return {'code': 'OK', 'cursor': 'done', 'price_list_products': []}

        return {
            'code': 'OK',
            'cursor': 'end',
            'price_list_products': [
                {
                    'pp_id': 'item_id_1',
                    'price': '89.00',
                    'price_list_id': 'price_list_id',
                    'prices': [{'price': '89.00', 'price_type': 'store'}],
                    'product_id': 'product_id',
                    'status': 'removed',
                },
            ],
        }

    db = pgsql['overlord_catalog']
    cursor = db.cursor()

    cursor.execute('SELECT shelf_type from catalog_wms.price_list_items')
    shelf_types = cursor.fetchall()
    assert len(shelf_types) == 2
    assert ('store',) in shelf_types
    assert ('markdown',) in shelf_types

    await taxi_overlord_catalog.run_periodic_task(
        'wms-price-lists-sync-periodic',
    )
    cursor.execute('SELECT shelf_type from catalog_wms.price_list_items')
    shelf_types = cursor.fetchall()

    assert shelf_types == [('markdown',)]


# LAVKABACKEND-572
# TODO empty sync
# TODO remove record
# TODO error sync
