# pylint: disable=redefined-outer-name, import-only-modules
import pytest


@pytest.fixture(name='mock_fleet_parks')
def _mock_fleet_parks(mockserver):
    class Context:
        def __init__(self):
            self.park_id = '123'
            self.country = 'ua'
            self.is_park_found = True

        def set_data(self, park_id=None, country=None, is_park_found=None):
            if park_id is not None:
                self.park_id = park_id
            if country is not None:
                self.country = country
            if is_park_found is not None:
                self.is_park_found = is_park_found

        def make_fleet_parks_request(self):
            return {'query': {'park': {'ids': [self.park_id]}}}

        def make_fleet_parks_responce(self):
            return [
                {
                    'id': self.park_id,
                    'login': 'test',
                    'name': 'test',
                    'is_active': True,
                    'city_id': '44',
                    'locale': 'test',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': True,
                    'country_id': self.country,
                    'specifications': ['eda', 'selfdriving'],
                    'geodata': {'lat': 5, 'lon': 0, 'zoom': 1},
                },
            ]

        @property
        def has_mock_parks_calls(self):
            return fleet_mock_parks.has_calls

    context = Context()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def fleet_mock_parks(request):
        assert request.json == context.make_fleet_parks_request()
        parks = (
            []
            if not context.is_park_found
            else context.make_fleet_parks_responce()
        )
        return {'parks': parks}

    return context
