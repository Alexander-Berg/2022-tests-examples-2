from datetime import datetime

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.route.route_info import get_track_points


ORDER_INFO = {
    'statistics': {
        'status_updates': [
            {
                'p': {'taxi_status': 'transporting'},
                'c': datetime.fromtimestamp(1639051969),
            },
            {
                'p': {
                    'taxi_status': 'complete',
                    'geopoint': [37.597506, 55.768991],
                },
                'c': datetime.fromtimestamp(163905218),
            },
        ],
    },
}


@pytest.fixture(name='mock_driver_trackstory')
def mock_driver_trackstory_fixture(mockserver, load_json):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    async def handler(request):
        query = request.query
        if query['driver_id'] == '6a' and query['db_id'] == 'e0':
            return {
                'track': [
                    {
                        'point': [45.758991, 28.597506],
                        'timestamp': 1638957581,
                        'bearing': 0.0,
                        'speed': 0.0,
                    },
                    {
                        'point': [2.35434, 45.75890],
                        'timestamp': 1638957581,
                        'bearing': 0.0,
                        'speed': 0.0,
                    },
                ],
            }
        return {'track': []}

    return handler


@pytest.mark.parametrize(
    'order_data, expected_track_points',
    [
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={
                    'order': {'performer': {'db_id': 'e0'}},
                    'order_info': {},
                    'performer': {'driver_id': '1_6a'},
                },
            ),
            [],
            id='no_start_and_end_time',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={
                    'order': {'performer': {'db_id': 'e0'}},
                    'order_info': ORDER_INFO,
                    'performer': {'driver_id': '1_6a'},
                },
            ),
            [[45.758991, 28.597506], [2.35434, 45.75890]],
            id='exist_track',
        ),
    ],
)
async def test_get_track_points(
        stq3_context: stq_context.Context,
        mock_driver_trackstory,
        order_data,
        expected_track_points,
):
    track_points = await get_track_points(
        context=stq3_context, order_data=order_data,
    )
    assert track_points == expected_track_points
