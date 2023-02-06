# encoding=utf-8
import pytest


@pytest.fixture(name='fleet_parks', autouse=True)
def _mock_fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_v1_parks_list(request):
        return {
            'parks': [
                {
                    'city_id': 'CITY_ID1',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p2',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'specifications': ['taxi', 'signalq'],
                    'provider_config': {'type': 'none', 'clid': 'clid2'},
                },
                {
                    'city_id': 'CITY_ID2',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p3',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'specifications': ['taxi', 'signalq'],
                    'provider_config': {'type': 'none', 'clid': 'clid2'},
                },
                {
                    'city_id': 'CITY_ID4',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p4',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'specifications': ['taxi', 'signalq'],
                    'provider_config': {'type': 'none', 'clid': 'clid3'},
                },
                {
                    'city_id': 'CITY_ID5',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p5',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'specifications': ['taxi', 'signalq'],
                    'provider_config': {'type': 'none', 'clid': 'clid3'},
                },
                {
                    'city_id': 'CITY_ID6',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p6',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'specifications': ['taxi'],
                    'provider_config': {'type': 'none', 'clid': 'clid3'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/cities/retrieve_by_name')
    def _mock_v1_cities(request):
        assert request.json['name_in_set'] == ['CITY_ID1']
        return {
            'cities_by_name': [
                {
                    'name': 'some_name',
                    'cities': [
                        {
                            'id': 'CITY_ID1',
                            'data': {'lat': 12.0002, 'lon': 23.1102},
                        },
                    ],
                },
            ],
        }
