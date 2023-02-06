import pytest


@pytest.fixture(name='mock_fleet_vehicles')
def _mock_fleet_vehicles(mockserver):
    class Context:
        def __init__(self):
            self.vehicle_id = '12345'
            self.park_id = '123'
            self.is_vehicle_found = True
            self.projection = ['data.car_id']

        def set_data(
                self,
                park_id=None,
                vehicle_id=None,
                projection=None,
                is_vehicle_found=None,
        ):
            if park_id is not None:
                self.park_id = park_id
            if vehicle_id is not None:
                self.vehicle_id = vehicle_id
            if is_vehicle_found is not None:
                self.is_vehicle_found = is_vehicle_found
            if projection is not None:
                self.projection = projection

        def make_fleet_vehicles_request(self):
            return {
                'id_in_set': [f'{self.park_id}_{self.vehicle_id}'],
                'projection': self.projection,
            }

        def make_fleet_vehicles_responce(self):
            return [
                {
                    'data': {'car_id': self.vehicle_id},
                    'park_id_car_id': f'{self.park_id}_{self.vehicle_id}',
                },
            ]

        @property
        def has_mock_parks_calls(self):
            return fleet_mock_parks.has_calls

    context = Context()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def fleet_mock_parks(request):
        assert request.method == 'POST'
        assert request.json == context.make_fleet_vehicles_request()
        vehicles = (
            []
            if not context.is_vehicle_found
            else context.make_fleet_vehicles_responce()
        )
        return {'vehicles': vehicles}

    return context
