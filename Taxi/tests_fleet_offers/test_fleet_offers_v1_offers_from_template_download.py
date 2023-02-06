import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/from-template/download'


def build_params(kind):
    return {'kind': kind}


OK_PARAMS = ['offer', 'labor_contract', 'rent']


@pytest.mark.parametrize('kind', OK_PARAMS)
async def test_ok(
        taxi_fleet_offers,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        mock_balance_replica,
        mockserver,
        kind,
):
    @mockserver.handler(f'/service/templates/{kind}/0')
    def mock_mds(request):
        return mockserver.make_response('file_string_data', 200)

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(kind=kind),
    )

    assert response.status_code == 200, response.text

    assert mock_mds.times_called == 1


async def test_not_found_in_s3(taxi_fleet_offers, mockserver):
    @mockserver.handler(f'/service/templates/offer/0')
    def mock_mds(request):
        return mockserver.make_response('Not found', 404)

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(kind='offer'),
    )

    assert mock_mds.times_called == 1

    assert response.status_code == 500, response.text
