import pytest


@pytest.fixture(name='fleet_parks_dispatch_requirements')
def _mock_fleet_parks(mockserver):
    @mockserver.json_handler(
        '/fleet-parks/internal/v1/dispatch-requirements/retrieve-by-park',
    )
    def _mock(request):
        assert request.json['park_id'] == 'park_id'
        return {
            'park_id': 'park_id',
            'label_id': 'label_id',
            'dispatch_requirement': 'only_source_park',
        }

    return _mock


@pytest.fixture(name='personal_phones_store')
def _mock_personal_phones_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock(request):
        assert request.json['value']
        return {
            'id': 'id_' + request.json['value'],
            'value': request.json['value'],
        }

    return _mock


@pytest.fixture(name='v1_profile')
def _mock_v1_profile(mockserver):
    @mockserver.json_handler('/integration-api/v1/profile')
    def _mock(request):
        assert request.json['user']['personal_phone_id']
        return {
            'user_id': 'user_id_' + request.json['user']['personal_phone_id'],
        }

    return _mock


@pytest.fixture(name='fleet_parks_list')
def _mock_fleet_parks_lis(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock(request):
        return {
            'parks': [
                {
                    'id': 'another_park',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'de',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'another park name',
                    'org_name': 'some park org name',
                    'geodata': {'lat': 45, 'lon': 6, 'zoom': 9},
                },
            ],
        }

    return _mock
