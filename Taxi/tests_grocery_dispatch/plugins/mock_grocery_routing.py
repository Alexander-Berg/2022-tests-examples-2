import pytest


@pytest.fixture(autouse=True, name='grocery_routing')
def mock_grocery_routing(mockserver):
    class Context:
        def __init__(self):
            self.pedestrian_eta = 0
            self.bicycle_eta = 0
            self.distance = 1

        def times_called(self):
            return _mock_route.times_called

        def set_response(
                self, pedestrian_eta: int, bicycle_eta: int, distance: int,
        ):
            self.pedestrian_eta = pedestrian_eta
            self.bicycle_eta = bicycle_eta
            self.distance = distance

    context = Context()

    @mockserver.json_handler(
        '/grocery-routing/internal/grocery-routing/v1/route',
    )
    def _mock_route(request):
        if request.json['transport_type'] == 'pedestrian':
            return {
                'distance': context.distance,
                'eta': context.pedestrian_eta,
            }
        if request.json['transport_type'] == 'bicycle':
            return {'distance': context.distance, 'eta': context.bicycle_eta}
        return {'distance': context.distance, 'eta': 0}

    return context
