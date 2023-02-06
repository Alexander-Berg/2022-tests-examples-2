import pytest

from tests_fleet_offers import utils

ENDPOINT = '/internal/v1/fleet-offers/v1/template/upload'

HEADERS = {
    **utils.SERVICE_HEADERS,
    'Content-Type': (
        'application/vnd.openxmlformats-'
        'officedocument.wordprocessingml.document'
    ),
}


def build_params(kind):
    return {'kind': kind}


@pytest.mark.parametrize('kind', ['offer', 'rent', 'labor_contract'])
async def test_ok(taxi_fleet_offers, load, mockserver, kind):
    @mockserver.handler(f'/service/templates/{kind}/0')
    def mock_mds(request):
        return mockserver.make_response('OK', 200)

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=HEADERS,
        params=build_params(kind=kind),
        data=utils.FILE_DATA,
    )

    assert response.status_code == 204, response.text
    assert mock_mds.times_called == 1
