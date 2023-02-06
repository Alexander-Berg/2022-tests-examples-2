# pylint: disable=redefined-outer-name
import pytest

import taxi_driver_photos.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_driver_photos.generated.service.pytest_plugins']


@pytest.fixture
def mock_unique_drivers(mockserver):
    def set_unique_id(unique_driver_id):
        @mockserver.json_handler(
            '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
        )
        def _unique_driver_id_handler(request):
            data = {
                'park_driver_profile_id': request.json['profile_id_in_set'][0],
            }
            if unique_driver_id is None:
                return {'uniques': [{**data}]}
            return {
                'uniques': [
                    {'data': {'unique_driver_id': unique_driver_id}, **data},
                ],
            }

    return set_unique_id


@pytest.fixture
def mock_driver_profiles(mockserver):
    def _mock_driver_profiles(car_id=None, is_internal_error=False):
        @mockserver.json_handler(
            '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id',
        )
        def _handler(request):
            if is_internal_error:
                return mockserver.make_response(
                    'Internal server error', json={}, status=500,
                )
            if car_id is None:
                return {'profiles': []}
            profiles_ids = request.json['id_in_set']
            assert len(profiles_ids) == 1
            profile_id = profiles_ids[0]
            return {
                'profiles': [
                    {
                        'park_driver_profile_id': profile_id,
                        'data': {'car_id': car_id},
                    },
                ],
            }

    return _mock_driver_profiles


@pytest.fixture
def mock_driver_categories(mockserver):
    def _mock_driver_categories(is_premium=None, is_internal_error=False):
        @mockserver.json_handler(
            '/driver-categories-api/internal/v2/allowed_driver_categories',
        )
        def _handler(request):
            if is_internal_error:
                return mockserver.make_response(
                    'Internal server error', json={}, status=500,
                )
            if is_premium is None:
                return []
            if is_premium:
                return {'categories': ['vip']}
            return {'categories': ['econome']}

    return _mock_driver_categories
