import pytest


@pytest.fixture(name='unique_drivers')
def mock_unique_drivers(mockserver):
    class Context:
        def __init__(self):
            self.unique_driver_ids = {}
            self.mock_retrieve_by_profiles = {}

        def add_driver(self, park_id, driver_profile_id, unique_driver_id):
            self.unique_driver_ids[
                '{}_{}'.format(park_id, driver_profile_id)
            ] = unique_driver_id

    context = Context()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_retrieve_by_profiles(request):
        response_uniques = []
        profile_id_in_set = request.json.get('profile_id_in_set')
        for profile_id in profile_id_in_set:
            record = {'park_driver_profile_id': profile_id}
            if profile_id in context.unique_driver_ids:
                record['data'] = {
                    'unique_driver_id': context.unique_driver_ids[profile_id],
                }
            response_uniques.append(record)

        return {'uniques': response_uniques}

    context.mock_retrieve_by_profiles = _mock_retrieve_by_profiles

    return context
