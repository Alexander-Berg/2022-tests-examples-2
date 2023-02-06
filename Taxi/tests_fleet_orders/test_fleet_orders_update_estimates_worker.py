import pytest


ORDERS = ['order_id1', 'order_id3']


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.fixture(name='mock_routes')
def _mock_routes(mockserver, load_binary):
    class RoutesContext:
        def __init__(self):
            self.geopoints = []
            self.v2_route_use_count = 0

        def set_geopoints(self, geopoints):
            self.geopoints = geopoints

    context = RoutesContext()

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        context.v2_route_use_count += 1
        rll = _rll_to_array(request.args['rll'])
        assert rll in context.geopoints
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    return context


@pytest.mark.now('2022-01-01T00:00:00Z')
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_update_estimates_worker(
        testpoint, taxi_fleet_orders, mock_routes,
):
    @testpoint('update-estimates-task-finished')
    def handle_finished(arg):
        pass

    mock_routes.set_geopoints(
        [
            [[37.6, 50.6], [37.6, 51.6], [37.6, 52.6]],
            [[38.6, 50.6], [38.6, 51.6], [37.6, 52.6]],
        ],
    )

    await taxi_fleet_orders.run_distlock_task('update-estimates-task')

    result = handle_finished.next_call()
    assert result['arg'] == ORDERS
