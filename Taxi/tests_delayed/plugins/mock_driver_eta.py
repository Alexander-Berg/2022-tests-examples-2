import json

import pytest


@pytest.fixture(name='driver_eta')
def _driver_eta(mockserver):
    class DriverEtaContext:
        def __init__(self):
            self.drivers_by_order = {}
            self.requests = []

        def set_drivers_for_order(self, drivers_by_order):
            self.drivers_by_order = drivers_by_order

        def get_drivers_for_order(self):
            return self.drivers_by_order

    context = DriverEtaContext()

    @mockserver.handler('/driver-eta/eta')
    def _driver_eta(request):
        parsed_body = request.json
        context.requests.append(parsed_body)

        order_id = parsed_body['order_id']

        search_settings = {
            'limit': 10,
            'max_distance': 10000,
            'max_route_distance': 9000,
            'max_route_time': 1090,
        }

        universal_drivers = {
            'found': True,
            'estimated_time': 100,
            'estimated_distance': 1000,
            'search_settings': search_settings,
            'candidates': context.drivers_by_order[order_id],
        }

        response = {
            'classes': {
                'econom': universal_drivers,
                'comfort': universal_drivers,
            },
        }

        return mockserver.make_response(
            json.dumps(response),
            200,
            headers={'Content-Type': 'application/json'},
        )

    return context
