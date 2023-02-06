import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.route.route_info import get_route_data
from order_notify.repositories.route.route_info import RouteData


@pytest.fixture(name='mock_functions')
def mock_get_maps_points(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_finish_point = Counter()
            self.get_track_points = Counter()

    counters = Counters()

    @patch('order_notify.repositories.route.route_info.get_finish_point')
    def _get_finish_point(order_data: OrderData) -> typing.Optional[dict]:
        counters.get_finish_point.call()
        if order_data.order_proc['_id'] == '1':
            return {'geopoint': [37.534, 55.750]}
        if order_data.order_proc['_id'] == '2':
            return {'geopoint': [2.340111, 48.855311]}
        return None

    @patch('order_notify.repositories.route.route_info.get_track_points')
    async def _get_track_points(
            context: stq_context.Context, order_data: OrderData,
    ) -> typing.List[typing.List[float]]:
        counters.get_track_points.call()
        return [[37.534, 55.750]]

    return counters


@pytest.mark.parametrize(
    '_id, order_request, '
    'expected_source, expected_destinations, expected_final_destination',
    [
        pytest.param(
            '0',
            {
                'destinations': [],
                'source': {'geopoint': [37.597506, 55.768991]},
            },
            {'geopoint': [37.597506, 55.768991]},
            [],
            None,
            id='no_destinations_no_finish_point',
        ),
        pytest.param(
            '1',
            {
                'destinations': [{'geopoint': [37.534, 55.750]}],
                'source': {'geopoint': [55.768991, 37.597506]},
            },
            {'geopoint': [55.768991, 37.597506]},
            [],
            {'geopoint': [37.534, 55.750]},
            id='no_destinations_exist_finish_point',
        ),
        pytest.param(
            '2',
            {
                'destinations': [
                    {'geopoint': [57.534, 15.750]},
                    {'geopoint': [2.340111, 48.855311]},
                ],
                'source': {'geopoint': [45.758991, 28.597506]},
            },
            {'geopoint': [45.758991, 28.597506]},
            [{'geopoint': [57.534, 15.750]}],
            {'geopoint': [2.340111, 48.855311]},
            id='two_destinations_exist_finish_point',
        ),
    ],
)
async def test_get_route_data(
        stq3_context: stq_context.Context,
        mock_functions,
        _id,
        order_request,
        expected_source,
        expected_destinations,
        expected_final_destination,
):
    expected_route_data = RouteData(
        source=expected_source,
        destinations=expected_destinations,
        final_destination=expected_final_destination,
        track_points=[[37.534, 55.750]],
    )
    route_data = await get_route_data(
        context=stq3_context,
        order_data=OrderData(
            brand='',
            country='',
            order={},
            order_proc={'_id': _id, 'order': {'request': order_request}},
        ),
    )
    assert route_data == expected_route_data
    assert mock_functions.get_finish_point.times_called == 1
    assert mock_functions.get_track_points.times_called == 1


@pytest.mark.parametrize(
    'destinations, final_destination, expected_geopoints',
    [
        pytest.param([], None, [], id='no_destinations_no_finish_point'),
        pytest.param(
            [],
            {'geopoint': [37.534, 55.750]},
            [[37.534, 55.750]],
            id='no_destinations_exist_finish_point',
        ),
        pytest.param(
            [{'geopoint': [57.534, 15.750]}, {'geopoint': [2.340, 48.855]}],
            {'geopoint': [45.758991, 28.597506]},
            [[2.340, 48.855], [57.534, 15.750], [45.758991, 28.597506]],
            id='two_destinations_exist_finish_point',
        ),
    ],
)
def test_get_all_geopoints(
        destinations, final_destination, expected_geopoints,
):
    route_data = RouteData(
        source={'geopoint': [37.597506, 55.768991]},
        destinations=destinations,
        final_destination=final_destination,
        track_points=[[57.534, 15.750]],
    )
    expected_geopoints = typing.cast(
        typing.List[typing.List[float]],
        (
            [route_data.source['geopoint']]
            + route_data.track_points
            + expected_geopoints
        ),
    )
    assert route_data.get_all_geopoints().sort() == expected_geopoints.sort()
