import pytest


@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_basic_depots_by_ids(taxi_grocery_depots, load_json):

    depot_ids = ['id-99999901', '99999902', 'id-5', 'id-not-found', '6']

    response = await taxi_grocery_depots.post(
        '/admin/depots/v1/depots-by-ids', json={'depot_ids': depot_ids},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
