import pytest


class _Context:
    def __init__(self):
        self.dbiduuid_to_data = {}

    def set_dbiduuid_to_data(self, dbiduuid_to_data):
        self.dbiduuid_to_data = dbiduuid_to_data


@pytest.fixture(name='mock_driver_profiles')
def mock_driver_profiles(mockserver):
    ctx = _Context()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _retrieve_by_uniques(request):
        profiles = []
        for dbiduuid in request.json['id_in_set']:
            itm = {'park_driver_profile_id': dbiduuid}

            if dbiduuid in ctx.dbiduuid_to_data:
                data = ctx.dbiduuid_to_data[dbiduuid]
                if 'projection' in request.json:
                    data = {
                        key: data[key] for key in request.json['projection']
                    }
                itm['data'] = data

            profiles.append(itm)

        return {'profiles': profiles}

    return ctx
