# pylint: disable=redefined-outer-name, import-only-modules
import pytest


PROJECTION = [
    'data.created_date',
    'data.amenities',
    'data.body_number',
    'data.boosters',
    'data.brand',
    'data.callsign',
    'data.cargo_hold_dimensions',
    'data.cargo_loaders',
    'data.carrier_permit_owner_id',
    'data.carrying_capacity',
    'data.categories',
    'data.chairs',
    'data.color',
    'data.description',
    'data.mileage',
    'data.model',
    'data.number',
    'data.permit_num',
    'data.permit_series',
    'data.permit_doc',
    'data.registration_cert',
    'data.rental',
    'data.rental_status',
    'data.leasing_company',
    'data.leasing_start_date',
    'data.leasing_term',
    'data.leasing_monthly_payment',
    'data.leasing_interest_rate',
    'data.fuel_type',
    'data.status',
    'data.tariffs',
    'data.transmission',
    'data.vin',
    'data.year',
]


@pytest.fixture(name='mock_fleet_vehicles')
def _mock_fleet_vehicles(mockserver):
    class Context:
        def __init__(self):
            self.response = {
                'vehicles': [
                    {'park_id_car_id': 'park-id_vehicle-id', 'data': {}},
                ],
            }
            self.park_id = '123'
            self.vehicle_id = '12345'
            self.vehicle_not_foud = False

        def set_data(
                self,
                response=None,
                park_id=None,
                vehicle_id=None,
                vehicle_not_foud=None,
        ):
            if response is not None:
                self.response = response
            if park_id is not None:
                self.park_id = park_id
            if vehicle_id is not None:
                self.vehicle_id = vehicle_id
            if vehicle_not_foud is not None:
                self.vehicle_not_foud = vehicle_not_foud

        def make_fleet_vehicles_request(self):
            return {
                'id_in_set': [f'{self.park_id}_{self.vehicle_id}'],
                'projection': PROJECTION,
            }

        def make_fleet_vehicles_responce(self):
            if self.vehicle_not_foud:
                return {'vehicles': [{'park_id_car_id': 'park-id_vehicle-id'}]}
            return self.response

        @property
        def has_mock_calls(self):
            return mock_fleet_vehicles.has_calls

    context = Context()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def mock_fleet_vehicles(request):
        assert request.json == context.make_fleet_vehicles_request()
        return context.make_fleet_vehicles_responce()

    return context
