import pytest


class CandidatesContext:
    def __init__(self):
        self.profiles = {}
        self.profiles_by_zone = {}
        self.mock_profiles = {}

    def load_profiles(self, profiles):
        self.profiles = profiles

    def load_profiles_by_zone(self, profiles_by_zone):
        self.profiles_by_zone = profiles_by_zone


@pytest.fixture(name='candidates')
def mock_candidates(mockserver):
    context = CandidatesContext()

    @mockserver.json_handler('/candidates/profiles')
    def _mock_profiles(request):
        doc = request.json
        if 'payment_methods' in context.profiles:
            assert 'payment_methods' in doc['data_keys']
        if 'payment_type' in context.profiles:
            assert 'payment_methods' in doc['data_keys']

        if 'zone_id' in doc:
            return context.profiles_by_zone[doc['zone_id']]
        return context.profiles

    context.mock_profiles = _mock_profiles

    return context
