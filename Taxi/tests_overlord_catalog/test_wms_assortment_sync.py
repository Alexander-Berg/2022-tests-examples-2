import pytest


@pytest.mark.pgsql('overlord_catalog', files=[])
@pytest.mark.suspend_periodic_tasks('wms-assortment-sync-periodic')
async def test_happy_path(taxi_overlord_catalog, pgsql, mockserver, load_json):
    assortments = load_json('wms_assortment_response.json')
    assortment_items = load_json('wms_assortment_items_response.json')

    @mockserver.json_handler('/grocery-wms/api/external/assortments/v1/list')
    def mock_assortment(request):
        if request.json['cursor']:
            return load_json(
                'wms_assortment_response_{}.json'.format(
                    request.json['cursor'],
                ),
            )
        return assortments

    @mockserver.json_handler(
        '/grocery-wms/api/external/assortments/v1/products',
    )
    def mock_assortment_items(request):
        if request.json['cursor']:
            return load_json(
                'wms_assortment_items_response_{}.json'.format(
                    request.json['cursor'],
                ),
            )
        return assortment_items

    await taxi_overlord_catalog.run_periodic_task(
        'wms-assortment-sync-periodic',
    )
    assert mock_assortment.times_called == 2
    assert mock_assortment_items.times_called == 2

    db = pgsql['overlord_catalog']
    cursor = db.cursor()
    cursor.execute('SELECT count(*) from catalog_wms.assortments')
    (result,) = cursor.fetchall()[0]
    assert result == len(assortments['assortments'])

    cursor.execute('SELECT count(*) from catalog_wms.assortment_items')
    (result,) = cursor.fetchall()[0]
    assert result == len(
        [
            x
            for x in assortment_items['assortment_products']
            if x['status'] == 'active'
        ],
    )  # one of the items is marked removed

    # check last cursors were saved
    cursor.execute(
        'SELECT cursor from catalog_wms.cursors '
        'WHERE name=\'/api/external/assortments/v1/list\'',
    )
    (result,) = cursor.fetchall()[0]
    assert result == 'done'

    cursor.execute(
        'SELECT cursor from catalog_wms.cursors '
        'WHERE name=\'/api/external/assortments/v1/products\'',
    )
    (result,) = cursor.fetchall()[0]
    assert result == 'done'


# LAVKABACKEND-572
# TODO empty sync
# TODO remove record
# TODO error sync
