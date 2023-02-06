import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/by-id/download'


def build_params(offer_id, offer_rev):
    return {'id': offer_id, 'rev': offer_rev}


OK_PARAMS = [
    ('00000000-0000-0000-0000-000000000001', 0),
    ('00000000-0000-0000-0000-000000000001', 1),
]


@pytest.mark.parametrize('offer_id, offer_rev', OK_PARAMS)
async def test_create(taxi_fleet_offers, mockserver, offer_id, offer_rev):
    @mockserver.handler(f'/park1/{offer_id}/{offer_rev}')
    def mock_mds(request):
        return mockserver.make_response('file_string_data', 200)

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(offer_id=offer_id, offer_rev=offer_rev),
    )

    assert response.status_code == 200, response.text

    assert mock_mds.times_called == 1


BAD_PARAMS = [
    ('00000000-0000-0000-0000-000000000001', 999),
    ('00000000-0000-0000-0000-100000000001', 0),
]


@pytest.mark.parametrize('offer_id, offer_rev', BAD_PARAMS)
async def test_not_found_in_db(taxi_fleet_offers, offer_id, offer_rev):
    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(offer_id=offer_id, offer_rev=offer_rev),
    )

    assert response.status_code == 404, response.text


async def test_not_found_in_s3(taxi_fleet_offers, mockserver):
    @mockserver.handler(f'/park1/00000000-0000-0000-0000-000000000001/0')
    def mock_mds(request):
        return mockserver.make_response('Not found', 404)

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(
            offer_id='00000000-0000-0000-0000-000000000001', offer_rev=0,
        ),
    )

    assert mock_mds.times_called == 1

    assert response.status_code == 404, response.text
