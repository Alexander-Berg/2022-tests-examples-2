import pytest


@pytest.fixture()
def driver_ui_profile_mocks(mockserver):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _v1_mode(request):
        assert request.query['park_id'] == 'park_id'
        assert request.query['driver_profile_id'] == 'driver_profile_id'
        assert request.query['concern'] == 'urgent'
        return {
            'display_mode': 'display_mode',
            'display_profile': 'display_profile',
        }


@pytest.fixture()
def unique_drivers_mocks(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        assert request.query['consumer'] == 'contractor-state'
        assert request.json['profile_id_in_set'] == [
            'park_id_driver_profile_id',
        ]
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park_id_driver_profile_id',
                    'data': {'unique_driver_id': 'unique_driver_id'},
                },
            ],
        }
