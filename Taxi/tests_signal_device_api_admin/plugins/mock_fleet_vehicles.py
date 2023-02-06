# encoding=utf-8
import pytest


@pytest.fixture(name='fleet_vehicles')
def _mock_fleet_vehicles(mockserver):
    class FleetVehiclesContext:
        def __init__(self):
            self.fleet_vehicles = None
            self.fleet_vehicles_response = {}
            self.fleet_vehicles_status = 200

        def set_fleet_vehicles_response(self, response):
            self.fleet_vehicles_response = response

        def set_fleet_vehicles_err_response(self, status):
            self.fleet_vehicles_status = status

    context = FleetVehiclesContext()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _get_fleet_vehicles(request):
        request.get_data()
        if context.fleet_vehicles_status != 200:
            return mockserver.make_response(
                json=context.fleet_vehicles_response,
                status=context.fleet_vehicles_status,
            )
        return context.fleet_vehicles_response

    context.fleet_vehicles = _get_fleet_vehicles

    return context
