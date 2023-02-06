import json

import pytest


class ParksActivation:
    def __init__(self, marker):
        if marker:
            self.parks_activation = marker.args[0]
        else:
            self.parks_activation = []

    def get_parks(self, last_revision):
        return [
            activation
            for activation in self.parks_activation
            if activation['revision'] > last_revision
        ]


@pytest.fixture(autouse=True)
def parks_activation_request(request, mockserver):
    marker = request.node.get_marker('parks_activation')
    parks_activation = ParksActivation(marker)

    @mockserver.json_handler('/parks_activation/v1/parks/activation/updates')
    def _mock_updates(request):
        data = json.loads(request.get_data())
        revision = data['last_known_revision']
        parks = parks_activation.get_parks(revision)
        if parks:
            return {
                'last_revision': parks[-1]['revision'],
                'parks_activation': parks,
            }

        return {'last_revision': revision, 'parks_activation': []}


@pytest.fixture
def mock_uantifraud_payment_available(mockserver):
    def mock_service_handler(antifraud_status):
        class CallHolder:
            calls = []

            def check_calls(self, count, order_id):
                assert len(self.calls) == count
                if count:
                    for call in self.calls:
                        assert call == order_id

        call_holder = CallHolder()

        @mockserver.json_handler(
            '/uantifraud/v1/payment/type/change_available',
        )
        def mock_antifraud_events(request):
            call_holder.calls.append(request.args['order_id'])
            if antifraud_status:
                return {'status': antifraud_status}
            return mockserver.make_response({}, 500)

        return call_holder

    return mock_service_handler
