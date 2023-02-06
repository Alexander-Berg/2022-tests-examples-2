import pytest

from tests_dispatch_airport_partner_protocol import common


@pytest.mark.parametrize('status_code', [200, 404, 500])
async def test_svo_cancel(
        taxi_dispatch_airport_partner_protocol, mockserver, status_code,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/stop')
    def _relocate_stop(request):
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        return {}

    response = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/cancel',
        {'order_id': 'rep:order_id_1'},
        headers={'Ya-Taxi-Token': 'cd5a4c6f-529b-4ea9-9633-dc2cd560ad76'},
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == {}


async def test_negative(taxi_dispatch_airport_partner_protocol):
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/cancel',
        {'order_id': 'rep:order_id_1'},
        headers={'Ya-Taxi-Token': 'not_existing_api_key'},
    )
    assert resp.status_code == 403
    assert resp.json()['code'] == 'INVALID_API_KEY'

    # bad request, no Api-Key header
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/cancel', {'order_id': 'rep:order_id_1'}, headers={},
    )
    assert resp.status_code == 400

    # bad request, order is not reposition
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/cancel',
        {'order_id': 'not_rep_order_id'},
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert resp.status_code == 400
    assert resp.json()['code'] == 'NOT_REPOSITION'
