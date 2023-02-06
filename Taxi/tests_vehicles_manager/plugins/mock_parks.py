# pylint: disable=redefined-outer-name, import-only-modules
import json

import pytest


def is_valid_header(request_header, context_header):
    for key, value in context_header.items():
        assert request_header.get(key) == value, f'invalid header {key}'
    return True


@pytest.fixture(name='mock_parks_cars')
def _mock_parks_request(mockserver):
    class Context:
        def __init__(self):
            self.park_id = '123'
            self.vehicle_id = '12345'
            self.vehicle_specifications = {}
            self.vehicle_licenses = {}
            self.park_profile = {}
            self.cargo = {}
            self.child_safety = {}
            self.result_caregories = []
            self.categories_filter = []
            self.fleet_api_client_id = None
            self.fleet_api_key_id = None
            self.real_ip = None
            self.idempotency_token = None
            self.status_code = None
            self.error_message = None
            self.error_code = None
            self.is_put_method = False

        def set_data(
                self,
                park_id=None,
                vehicle_id=None,
                vehicle_specifications=None,
                vehicle_licenses=None,
                park_profile=None,
                cargo=None,
                child_safety=None,
                result_caregories=None,
                categories_filter=None,
                fleet_api_client_id=None,
                fleet_api_key_id=None,
                real_ip=None,
                idempotency_token=None,
                status_code=None,
                error_message=None,
                error_code=None,
                is_put_method=None,
        ):
            if park_id is not None:
                self.park_id = park_id
            if vehicle_id is not None:
                self.vehicle_id = vehicle_id
            if vehicle_specifications is not None:
                self.vehicle_specifications = vehicle_specifications
            if vehicle_licenses is not None:
                self.vehicle_licenses = vehicle_licenses
            if park_profile is not None:
                self.park_profile = park_profile
            if cargo is not None:
                self.cargo = cargo
            if child_safety is not None:
                self.child_safety = child_safety
            if result_caregories is not None:
                self.result_caregories = result_caregories
            if categories_filter is not None:
                self.categories_filter = categories_filter
            if fleet_api_client_id is not None:
                self.fleet_api_client_id = fleet_api_client_id
            if fleet_api_key_id is not None:
                self.fleet_api_key_id = fleet_api_key_id
            if real_ip is not None:
                self.real_ip = real_ip
            if idempotency_token is not None:
                self.idempotency_token = idempotency_token
            if status_code is not None:
                self.status_code = status_code
            if error_message is not None:
                self.error_message = error_message
            if error_code is not None:
                self.error_code = error_code
            if is_put_method is not None:
                self.is_put_method = is_put_method

        def make_parks_request(self):
            request = {}

            request['model'] = self.vehicle_specifications['model']
            request['brand'] = self.vehicle_specifications['brand']
            request['year'] = self.vehicle_specifications['year']
            request['color'] = self.vehicle_specifications['color']
            request['transmission'] = self.vehicle_specifications[
                'transmission'
            ]
            if self.vehicle_specifications.get('body_number') is not None:
                request['body_number'] = self.vehicle_specifications[
                    'body_number'
                ]
            if self.vehicle_specifications.get('vin') is not None:
                request['vin'] = self.vehicle_specifications['vin']
            request['mileage'] = self.vehicle_specifications.get('mileage', 0)

            request['number'] = self.vehicle_licenses['licence_plate_number']
            if (
                    self.vehicle_licenses.get('registration_certificate')
                    is not None
            ):
                request['registration_cert'] = self.vehicle_licenses[
                    'registration_certificate'
                ]
            if self.vehicle_licenses.get('licence_number') is not None:
                request['permit_num'] = self.vehicle_licenses['licence_number']

            request['callsign'] = self.park_profile['callsign']
            request['status'] = self.park_profile['status']
            if self.park_profile.get('license_owner_id') is not None:
                request['carrier_permit_owner_id'] = self.park_profile[
                    'license_owner_id'
                ]
            if self.park_profile.get('is_park_property') is not None:
                request['rental'] = self.park_profile['is_park_property']
            if self.park_profile.get('ownership_type') is not None:
                request['rental_status'] = self.park_profile['ownership_type']
            if self.park_profile.get('leasing_conditions') is not None:
                request['leasing_company'] = self.park_profile[
                    'leasing_conditions'
                ]['company']
                request['leasing_start_date'] = self.park_profile[
                    'leasing_conditions'
                ]['start_date']
                request['leasing_term'] = self.park_profile[
                    'leasing_conditions'
                ]['term']
                request['leasing_monthly_payment'] = self.park_profile[
                    'leasing_conditions'
                ]['monthly_payment']
                request['leasing_interest_rate'] = float(
                    self.park_profile['leasing_conditions']['interest_rate'],
                )
            if self.park_profile.get('fuel_type') is not None:
                request['fuel_type'] = self.park_profile['fuel_type']
            request['amenities'] = self.park_profile.get('amenities', [])
            request['categories'] = sorted(
                self.result_caregories
                if self.result_caregories
                else self.park_profile.get('categories', []),
            )
            if self.categories_filter is not None:
                request['categories_filter'] = self.categories_filter
            if self.park_profile.get('tariffs') is not None:
                request['tariffs'] = self.park_profile['tariffs']
            if self.park_profile.get('comment') is not None:
                request['description'] = self.park_profile['comment']

            request['booster_count'] = self.child_safety.get(
                'booster_count', 0,
            )
            if self.child_safety.get('chairs') is not None:
                for cur_chair in self.child_safety['chairs']:
                    chair = {**cur_chair, 'brand': 'Other'}
                    request.setdefault('chairs', []).append(chair)

            if self.cargo.get('cargo_loaders') is not None:
                request['cargo_loaders'] = self.cargo['cargo_loaders']
            if self.cargo.get('carrying_capacity') is not None:
                request['carrying_capacity'] = self.cargo['carrying_capacity']
            if self.cargo.get('cargo_hold_dimensions') is not None:
                request['cargo_hold_dimensions'] = self.cargo[
                    'cargo_hold_dimensions'
                ]

            return request

        def make_parks_responce(self):
            return {
                'id': 'contractor_id',
                'park_id': '123',
                'brand': self.vehicle_specifications['brand'],
                'model': self.vehicle_specifications['model'],
                'color': self.vehicle_specifications['color'],
                'year': self.vehicle_specifications['year'],
                'mileage': self.vehicle_specifications.get('mileage', 0),
                'status': self.park_profile['status'],
                'number': self.vehicle_licenses['licence_plate_number'],
                'normalized_number': self.vehicle_licenses[
                    'licence_plate_number'
                ],
                'booster_count': self.child_safety.get('booster_count', 0),
                'callsign': self.park_profile['callsign'],
                'amenities': self.park_profile.get('amenities', []),
                'categories': self.park_profile.get('categories', []),
                'transmission': self.vehicle_specifications['transmission'],
            }

        @property
        def has_mock_parks_calls(self):
            return mock_parks.has_calls

        @property
        def gen_idempotency_token(self):
            return (
                f'fleet-api/{self.fleet_api_key_id}/{self.idempotency_token}'
            )

        def make_header(self):
            header = {
                'X-Fleet-API-Client-ID': self.fleet_api_client_id,
                'X-Fleet-API-Key-ID': self.fleet_api_key_id,
                'X-Real-IP': self.real_ip,
            }
            if not self.is_put_method:
                header['X-Idempotency-Token'] = self.gen_idempotency_token
            return header

    context = Context()

    @mockserver.json_handler('/parks/cars')
    def mock_parks(request):
        assert is_valid_header(request.headers, context.make_header())
        if request.method == 'PUT':
            assert request.query.get('id') == context.vehicle_id
        assert request.query.get('park_id') == context.park_id
        assert request.json == context.make_parks_request()
        if context.status_code is not None:
            return mockserver.make_response(
                json.dumps(
                    {
                        'error': {
                            'code': context.error_code,
                            'text': context.error_message,
                        },
                    },
                ),
                context.status_code,
            )
        return context.make_parks_responce()

    return context
