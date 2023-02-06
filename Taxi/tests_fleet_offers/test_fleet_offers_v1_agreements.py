from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/agreements'


async def test_ok(
        taxi_fleet_offers,
        mock_fleet_parks,
        mock_document_templator,
        load_json,
):
    response = await taxi_fleet_offers.get(
        ENDPOINT, headers=utils.build_fleet_headers(park_id='park1'),
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json('response.json')
