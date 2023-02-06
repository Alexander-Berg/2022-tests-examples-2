# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from contractor_order_setcar_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True, name='driver_app_profiles')
def _driver_app_profile(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': request.json['id_in_set'][0],
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': 'android',
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    return _mock_get_driver_app
