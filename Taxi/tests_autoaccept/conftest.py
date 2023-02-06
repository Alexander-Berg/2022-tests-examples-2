# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from autoaccept_plugins import *  # noqa: F403 F401


@pytest.fixture(name='driver-tags', autouse=True)
def _driver_tags(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
        def get_tags(request):
            data = {'tags': ['driver_fix']}
            return mockserver.make_response(200, json=data)

    return Context()


@pytest.fixture(name='driver-metrics', autouse=True)
def _driver_metrics(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/driver-metrics/v1/order/match_properties')
        def match_order_properies(request):
            data = {'dispatch_distance_type': 'dispatch_long'}
            return mockserver.make_response(200, json=data)

    return Context()


@pytest.fixture(name='passenger-profiles', autouse=True)
def _passenger_profile(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler(
            '/passenger-profile/passenger-profile/v1/profile',
        )
        def profile(request):
            data = {'first_name': 'First name', 'rating': '4.5'}
            return mockserver.make_response(200, json=data)

    return Context()


@pytest.fixture(name='driver_app_profile', autouse=True)
def _default_mocks(mockserver):
    data = {
        'taximeter_version': '9.88',
        'taximeter_platform': 'android',
        'taximeter_version_type': 'yango',
    }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_app_profiles(request):
        return {
            'profiles': [
                {'park_driver_profile_id': 'park_id_uuid0', 'data': data},
            ],
        }

    def _store(**kwargs):
        data.update(kwargs)

    return _store
