import pytest

from . import catalog_wms_config


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['stocks.sql', 'mark_depots_as_wms.sql', 'refresh_wms_views.sql'],
)
async def test_happy_path_wms(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-stocks.json', 'gdepots-zones-stocks.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog/availableforsale/90213',
    )

    assert response.status_code == 200
    for org in response.json()['data']['organizations']:
        for stock in org['stocks']:
            if stock['productId'] == '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3':
                assert stock['avialableForSale'] == 322.0


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        '1c_menu_data.sql',
        '1c_stocks.sql',
        'stocks.sql',
        'refresh_wms_views.sql',
    ],
)
async def test_happy_path(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-stocks.json', 'gdepots-zones-stocks.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog/availableforsale/90213',
    )

    assert response.status_code == 200
    for org in response.json()['data']['organizations']:
        for stock in org['stocks']:
            if stock['productId'] == '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3':
                assert stock['avialableForSale'] == 322.0


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['stocks.sql', 'mark_depots_as_wms.sql', 'refresh_wms_views.sql'],
)
async def test_not_found_wms(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-stocks.json', 'gdepots-zones-stocks.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog/availableforsale/90214',
    )
    assert response.status_code == 404


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['stocks.sql', 'mark_depots_as_wms.sql', 'refresh_wms_views.sql'],
)
async def test_not_found(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-stocks.json', 'gdepots-zones-stocks.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog/availableforsale/90214',
    )
    assert response.status_code == 404


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'stocks.sql',
        'mark_depots_as_wms.sql',
        'negative_good_quantity.sql',
        'refresh_wms_views.sql',
    ],
)
async def test_negative_stocks_wms(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-stocks.json', 'gdepots-zones-stocks.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog/availableforsale/90213',
    )
    assert response.status_code == 200
    for org in response.json()['data']['organizations']:
        for stock in org['stocks']:
            if stock['productId'] == '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3':
                assert stock['avialableForSale'] == 0.0
