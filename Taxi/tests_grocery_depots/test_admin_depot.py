import pytest


@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_basic_depot(taxi_grocery_depots, load_json):

    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depot?depot_id=id-99999901',
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depot_404(taxi_grocery_depots, load_json):

    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depot?depot_id=id-9999991234',
    )
    assert response.status_code == 404
