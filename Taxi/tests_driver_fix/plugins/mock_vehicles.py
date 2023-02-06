import pytest


@pytest.fixture(name='vehicles')
def _mock_vehicles(mockserver):
    class DriverProfilesContext:
        def __init__(self):
            self.vehicle_bindings = None
            self.cars_list = None

            self.vehicle_bindings_response = {}
            self.cars_list_response = {}

        def set_vehicle_bindings_response(self, response):
            self.vehicle_bindings_response = response

        def set_cars_list_response(self, response):
            self.cars_list_response = response

    context = DriverProfilesContext()

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id',
    )
    def _vehicle_bindings(request):
        return context.vehicle_bindings_response

    @mockserver.json_handler('/parks/cars/list')
    def _cars_list(request):
        response = context.cars_list_response
        return response

    context.vehicle_bindings = _vehicle_bindings
    context.cars_list = _cars_list

    return context
