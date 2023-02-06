import copy

import pytest


async def test_parcels_update_timeslot(taxi_grocery_api, mockserver):
    """Provide data to tristero"""
    ref_order = 'some-ref-order'
    vendor = 'some-vendor'
    token = 'some-token'
    timeslot = {
        'start': '2021-12-15T17:09:00+03:00',
        'end': '2021-12-15T18:09:00+03:00',
    }
    utc_timeslot = {
        'start': '2021-12-15T14:09:00+00:00',
        'end': '2021-12-15T15:09:00+00:00',
    }

    json = {
        'ref_order': ref_order,
        'vendor': vendor,
        'token': token,
        'timeslot': timeslot,
    }

    expected_request = copy.deepcopy(json)
    expected_request['timeslot'] = utc_timeslot

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/update-timeslot',
    )
    def tristero_update_timeslot(request):
        assert request.json == expected_request
        return {}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/order/update-timeslot', json=json,
    )
    assert response.status_code == 200
    assert tristero_update_timeslot.times_called == 1


@pytest.mark.parametrize('error_code', [404, 409, 500])
async def test_parcels_update_timeslot_errors(
        taxi_grocery_api, mockserver, error_code,
):
    """Proxy errors from tristero"""
    json = {'ref_order': '', 'vendor': '', 'token': ''}

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/update-timeslot',
    )
    def tristero_update_timeslot(request):
        return mockserver.make_response(status=error_code)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/order/update-timeslot', json=json,
    )
    assert response.status_code == error_code
    assert tristero_update_timeslot.times_called == 1
