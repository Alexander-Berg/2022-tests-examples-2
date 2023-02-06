# encoding=utf-8
import pytest


@pytest.fixture(name='fleet_vehicles')
def _mock_fleet_vehicles(mockserver):
    class FleetVehiclesContext:
        def __init__(self):
            self.fleet_vehicles = None
            self.fleet_vehicles_response = {}

        def set_fleet_vehicles_response(self, response):
            self.fleet_vehicles_response = response

    context = FleetVehiclesContext()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _get_fleet_vehicles(request):
        request.get_data()
        return context.fleet_vehicles_response

    context.fleet_vehicles = _get_fleet_vehicles

    return context
