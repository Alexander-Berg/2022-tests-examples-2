import pytest


@pytest.mark.pgsql(
    'overlord_catalog', files=['default_wms.sql', 'refresh_wms_views.sql'],
)
@pytest.mark.config(OVERLORD_CATALOG_NOMENCLATURE_SYNC_PERIOD_SECONDS=600)
async def test_feeds_raw(
        taxi_overlord_catalog, load_json, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-default_wms.json', 'gdepots-zones-default_wms.json',
    )
    response = await taxi_overlord_catalog.get('/feeds/raw_items_data')
    assert response.status_code == 200
    assert response.json() == load_json('feeds_raw.json')

    response = await taxi_overlord_catalog.get(
        '/feeds/raw_items_data?region_id=1',
    )
    assert response.status_code == 200
    assert response.json() == load_json('feeds_raw.json')
