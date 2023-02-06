import pytest


class _Context:
    def __init__(self):
        self.udid_to_profiles = {}

    def set_udid_to_profiles(self, udid_to_profiles):
        self.udid_to_profiles = udid_to_profiles


@pytest.fixture(name='mock_unique_drivers')
def mock_unique_drivers(mockserver):
    ctx = _Context()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _retrieve_by_uniques(request):
        resp_profiles = []
        for udid in request.json['id_in_set']:
            data = []
            for profile in ctx.udid_to_profiles[udid]:
                dbid = profile['park_id']
                uuid = profile['driver_profile_id']
                data.append(
                    {
                        'park_id': dbid,
                        'driver_profile_id': uuid,
                        'park_driver_profile_id': dbid + '_' + uuid,
                    },
                )
            resp_profiles.append({'unique_driver_id': udid, 'data': data})
        return {'profiles': resp_profiles}

    return ctx
