import pytest


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.fixture(name='mock_routes')
def mock_routes(mockserver, load_binary):
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
        assert rll == context.geopoints
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    return context
