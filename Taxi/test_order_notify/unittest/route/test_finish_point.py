import pytest

from order_notify.repositories.order_info import OrderData
from order_notify.repositories.route.route_info import get_finish_point


ORDER_INFO_WITHOUT_COMPLETE_POINTS = {
    'statistics': {
        'status_updates': [
            {'c': {'$date': 1638957444566}},
            {'p': {'taxi_status': 'pending'}},
        ],
    },
}

COMPLETE_POINT = {
    'taxi_status': 'complete',
    'geopoint': [37.597506, 55.768991],
}

ORDER_INFO_WITH_COMPLETE_POINTS = {
    'statistics': {
        'status_updates': [
            {'c': {'$date': 1638957444566}},
            {'p': {'taxi_status': 'pending'}},
            {'p': COMPLETE_POINT},
        ],
    },
}

ORDER_WITHOUT_DESTINATIONS: dict = {'request': {'destinations': []}}

ORDER_WITH_DESTINATIONS = {
    'request': {
        'destinations': [
            {'geopoint': [37.59749437328688, 55.77085916050152]},
            {'geopoint': [37.5349951418744, 55.75027739625019]},
        ],
    },
}


ORDER_WITH_DESTINATIONS_NEAR_COMPLETE_POINT = {
    'request': {
        'destinations': [
            {'geopoint': [37.5349951418744, 55.75027739625019]},
            {'geopoint': [37.59750437328688, 55.76885916050152]},
        ],
    },
}


@pytest.mark.parametrize(
    'order_data, expected_finish_point',
    [
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={
                    'order_info': {},
                    'order': ORDER_WITHOUT_DESTINATIONS,
                },
            ),
            None,
            id='empty_status_updates_no_destinations',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={
                    'order_info': ORDER_INFO_WITHOUT_COMPLETE_POINTS,
                    'order': ORDER_WITHOUT_DESTINATIONS,
                },
            ),
            None,
            id='no_complete_points_no_destinations',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={
                    'order_info': ORDER_INFO_WITHOUT_COMPLETE_POINTS,
                    'order': ORDER_WITH_DESTINATIONS,
                },
            ),
            ORDER_WITH_DESTINATIONS['request']['destinations'][-1],
            id='no_complete_points_exist_destinations',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={
                    'order_info': ORDER_INFO_WITH_COMPLETE_POINTS,
                    'order': ORDER_WITH_DESTINATIONS,
                },
            ),
            COMPLETE_POINT,
            id='complete_points_exist_not_near_destination',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={
                    'order_info': ORDER_INFO_WITH_COMPLETE_POINTS,
                    'order': ORDER_WITH_DESTINATIONS_NEAR_COMPLETE_POINT,
                },
            ),
            ORDER_WITH_DESTINATIONS_NEAR_COMPLETE_POINT['request'][
                'destinations'
            ][-1],
            id='complete_points_exist_near_destination',
        ),
    ],
)
def test_get_finish_point(order_data, expected_finish_point):
    finish_point = get_finish_point(order_data)
    assert finish_point == expected_finish_point
