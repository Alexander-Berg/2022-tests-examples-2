# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from contractor_statistics_view_plugins import *  # noqa: F403 F401


@pytest.fixture(name='client_events')
def _client_events(mockserver):
    @mockserver.json_handler('/client-events/bulk-push')
    def _bulk_push(request_):
        return mockserver.make_response(
            status=context.status_code, json=context.response,
        )

    class FixtureContext:
        def __init__(self):
            self.bulk_push = _bulk_push
            self.status_code = None
            self.response = None

    context = FixtureContext()

    return context


@pytest.fixture(name='unique_drivers')
def _uniques(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        return context.retrieve_by_profiles_response

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _retrieve_by_uniques(request):
        return context.retrieve_by_uniques_response

    class FixtureContext:
        def __init__(self):
            self.retrieve_by_profiles = _retrieve_by_profiles
            self.retrieve_by_profiles_response = None
            self.retrieve_by_uniques = _retrieve_by_uniques
            self.retrieve_by_uniques_response = None

        def set_retrieve_by_uniques(
                self, unique_driver_id, driver_profile_id, park_id,
        ):
            self.retrieve_by_uniques_response = {
                'profiles': [
                    {
                        'unique_driver_id': (
                            unique_driver_id if unique_driver_id else 'udid'
                        ),
                        'data': [
                            {
                                'park_id': park_id if park_id else 'park_id',
                                'driver_profile_id': (
                                    driver_profile_id
                                    if driver_profile_id
                                    else 'driver_profile_id'
                                ),
                                'park_driver_profile_id': 'pdid',
                            },
                        ],
                    },
                ],
            }

        def set_retrieve_by_profiles(
                self, unique_driver_id, driver_profile_id, park_id,
        ):
            self.retrieve_by_profiles_response = {
                'uniques': [
                    {
                        'park_driver_profile_id': (
                            park_id + '_' + driver_profile_id
                        ),
                        'data': {'unique_driver_id': unique_driver_id},
                    },
                ],
            }

    context = FixtureContext()

    return context
