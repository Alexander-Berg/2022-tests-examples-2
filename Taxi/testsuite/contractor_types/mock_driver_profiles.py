import pytest

from . import utils


class DriverProfilesContext:
    def __init__(self):
        self.orders_provider = {}

    def set_orders_provider(
            self,
            park_id='park_id',
            contractor_profile_id='profile_id',
            orders_provider='taxi',
    ):
        profile_id = utils.make_profile_id(park_id, contractor_profile_id)
        self.orders_provider[profile_id] = {orders_provider: True}


@pytest.fixture(autouse=True)
def driver_profiles(mockserver, load_json):
    context = DriverProfilesContext()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def retrieve_profiles(request):
        profiles = []
        for profile_id in request.json['id_in_set']:
            profiles.append(
                {
                    'park_driver_profile_id': profile_id,
                    'data': {
                        'orders_provider': context.orders_provider.get(
                            profile_id, {'taxi': True},
                        ),
                    },
                },
            )
        response_body = {'profiles': profiles}
        return mockserver.make_response(status=200, json=response_body)

    setattr(context, 'retrieve_profiles', retrieve_profiles)
    return context
