import pytest

FALLBACK_ROUTER = 'fallback_router'

# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


async def test_happy_path(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', 'seg6',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3', extra_time_min=10,
    )
    assert response.status_code == 200

    diff_response = await taxi_cargo_dispatch.post(
        '/v1/waybill/get-update-diff', json={'waybill_ref': 'my_waybill'},
    )
    assert diff_response.status_code == 200

    diff = diff_response.json()
    assert diff['revision'] == 1
    assert diff['extra_time_min'] == 10
    new_points = [point['point_id'] for point in diff['new_points']]
    assert new_points == ['seg6_A1_p1', 'seg6_B1_p2', 'seg6_C1_p3']


async def test_no_previous_waybill(
        taxi_cargo_dispatch, happy_path_state_performer_found, testpoint,
):
    @testpoint('no-previous-waybill-ref')
    def exception_point(data):
        return

    diff_response = await taxi_cargo_dispatch.post(
        '/v1/waybill/get-update-diff', json={'waybill_ref': 'waybill_fb_3'},
    )
    await exception_point.wait_call()

    assert diff_response.status_code == 500
