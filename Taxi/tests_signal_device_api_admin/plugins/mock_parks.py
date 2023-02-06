# encoding=utf-8
import copy

import pytest


@pytest.fixture(name='parks')
def _mock_parks(mockserver):
    class ParksContext:
        def __init__(self):
            self.driver_profiles_list = None
            self.cars_list = None
            self.driver_profiles_response = {}
            self.cars_list_response = {}
            self.cars_400_response = None
            self.driver_profiles_one_time_called = True
            self.expected_drivers_create_body = {}
            self.drivers_create_400_response = None

        def set_driver_profiles_response(self, response, one_time_called=True):
            self.driver_profiles_response = response
            self.driver_profiles_one_time_called = one_time_called

        def set_cars_list_response(self, response):
            self.cars_list_response = response

        def set_cars_400_response(self, response):
            self.cars_400_response = response

        def set_drivers_create_body(self, body):
            self.expected_drivers_create_body = body

        def set_drivers_create_400_response(self, response):
            self.drivers_create_400_response = response

        @staticmethod
        def make_driver_id(*, park_id, idempotency_token):
            """Only for testing purpose I create driver_id that way"""
            return park_id + idempotency_token

    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _get_driver_profiles_list(request):
        request.get_data()
        if isinstance(context.driver_profiles_response, list):
            return context.driver_profiles_response[
                context.driver_profiles_list.times_called
            ]
        if (
                not context.driver_profiles_one_time_called
                or context.driver_profiles_list.times_called == 0
        ):
            return context.driver_profiles_response
        raise ValueError('Only one call to driver_profiles_list expected')

    @mockserver.json_handler('/parks/cars/list')
    def _get_cars(request):
        request.get_data()
        return context.cars_list_response

    @mockserver.json_handler('/parks/cars')
    def _create_car(request):
        if context.cars_400_response is not None:
            return mockserver.make_response(
                json=context.cars_400_response, status=400,
            )

        assert request.query.get('park_id') is not None
        assert request.headers.get('X-Idempotency-Token') is not None
        assert request.headers.get('X-Ya-User-Ticket') is not None
        assert request.headers.get('X-Ya-User-Ticket-Provider') in {
            'yandex',
            'yandex_team',
        }

        request_json = request.json
        assert request_json['booster_count'] == 0
        assert request_json['mileage'] == 0
        assert not request_json['amenities']
        assert not request_json['categories']
        assert not request_json['categories_filter']

        response = request_json
        response['normalized_number'] = response['number']
        response.pop('categories_filter')

        response['park_id'] = request.query['park_id']

        response['id'] = context.make_driver_id(
            park_id=request.query['park_id'],
            idempotency_token=request.headers['X-Idempotency-Token'],
        )
        return response

    @mockserver.json_handler('/parks/internal/driver-profiles/create')
    def _create_driver(request):
        if context.drivers_create_400_response is not None:
            return mockserver.make_response(
                json=context.drivers_create_400_response, status=400,
            )

        assert request.query.get('park_id') is not None
        assert request.headers.get('X-Idempotency-Token') is not None

        request_json = request.json
        driver_license = request_json['driver_profile'].get('driver_license')

        if driver_license is not None:
            driver_license_number = driver_license['number']
            context.expected_drivers_create_body['driver_profile'][
                'driver_license'
            ] = (
                {
                    'number': driver_license_number,
                    'expiration_date': '2021-01-01',
                    'issue_date': '2021-01-01',
                }
            )
            birth_date = driver_license.get('birth_date')
            if birth_date is not None:
                context.expected_drivers_create_body['driver_profile'][
                    'driver_license'
                ]['birth_date'] = birth_date

        context.expected_drivers_create_body['accounts'] = [
            {'type': 'current', 'balance_limit': '0'},
        ]
        assert request_json == context.expected_drivers_create_body

        response = {
            'driver_profile': copy.deepcopy(request_json['driver_profile']),
        }

        response['driver_profile']['park_id'] = request.query['park_id']
        response['driver_profile']['work_status'] = 'not_working'

        if driver_license is not None:
            response['driver_profile']['driver_license'][
                'normalized_number'
            ] = driver_license['number']

        response['driver_profile']['id'] = context.make_driver_id(
            park_id=request.query['park_id'],
            idempotency_token=request.headers['X-Idempotency-Token'],
        )
        return response

    context.driver_profiles_list = _get_driver_profiles_list
    context.cars_list = _get_cars

    return context
