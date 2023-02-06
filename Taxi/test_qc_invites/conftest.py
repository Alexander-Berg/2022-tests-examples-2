# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import json

import pytest

import qc_invites.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['qc_invites.generated.service.pytest_plugins']


class MockContext:
    def __init__(self):
        self.responses = {}

    def set_response(self, handler, content):
        self.responses[handler] = content


@pytest.fixture(name='fleet_vehicles')
def _fleet_vehicles(mockserver):
    context = MockContext()

    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/retrieve_by_number_with_normalization',
    )
    def _retrieve_handler(request):
        handler = 'retrieve_by_number_with_normalization'

        serialized_data = json.loads(request.get_data())
        car_numbers = serialized_data.get('numbers_in_set', [])
        if car_numbers:
            car_handler = '_'.join(
                ['retrieve_by_number_with_normalization', car_numbers[0]],
            )
            if car_handler in context.responses:
                handler = car_handler
        return mockserver.make_response(
            json.dumps(context.responses.get(handler, '')), 200,
        )

    return context


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver):
    context = MockContext()

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/'
        'drivers/retrieve_by_park_id_car_id',
    )
    def _retrieve_by_park_id_car_id_handler(request):
        return mockserver.make_response(
            json.dumps(
                context.responses.get('retrieve_by_park_id_car_id', {}),
            ),
            200,
        )

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def _retrieve_by_license_handler(request):
        return mockserver.make_response(
            json.dumps(
                context.responses.get('profiles_retrieve_by_license', {}),
            ),
            200,
        )

    return context


@pytest.fixture(autouse=True)
def _qc_exams_admin(mockserver):
    context = MockContext()

    @mockserver.json_handler('/qc-exams-admin/qc-admin/v1/call')
    def _state_post(request):
        return {}

    return context
