import pytest


@pytest.fixture(name='waybill_info_points_status')
def _waybill_info_points_status(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_points_status.json',
    )


@pytest.mark.config(
    CARGO_ORDERS_ENABLE_POINT_STATUS_BY_EXECUTION_IN_PRICING_REQUEST=[
        'visited',
        'skipped',
    ],
)
async def test_calc_request_waypoints_resolution_execution(
        calc_price,
        mock_cargo_pricing_calc,
        waybill_info_points_status,
        resolve_waybill,
):
    await calc_price(source_type='requestconfirm')
    assert mock_cargo_pricing_calc.mock.times_called == 1
    waypoints = mock_cargo_pricing_calc.request['waypoints']
    waypoint_resolution = [
        point['resolution_info']
        for point in waypoints
        if 'resolution_info' in point
    ]
    assert len(waypoint_resolution) == 6
    assert waypoint_resolution == [
        {
            'resolution': 'skipped',
            'resolved_at': '2021-03-23T10:15:52.346759+00:00',
        },
        {
            'resolution': 'delivered',
            'resolved_at': '2021-03-23T10:16:17.384156+00:00',
        },
        {
            'resolution': 'delivered',
            'resolved_at': '2021-03-23T10:20:17.384156+00:00',
        },
        {
            'resolution': 'skipped',
            'resolved_at': '2021-03-23T10:15:52.346759+00:00',
        },
        {
            'resolution': 'skipped',
            'resolved_at': '2021-03-23T10:15:52.346759+00:00',
        },
        {
            'resolution': 'skipped',
            'resolved_at': '2021-03-23T10:20:17.384156+00:00',
        },
    ]
