import pytest


@pytest.fixture(name='tariffs')
def _mock_tariffs(mockserver, load_json):
    all_zones = load_json('tariff_settings.json')
    for zone in all_zones:
        zone['name'] = zone.pop('home_zone')
        zone['time_zone'] = zone.pop('timezone')

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _mock_tariff_zones(request, *args, **kwargs):
        request_for_cities = request.query['city_ids']
        assert request_for_cities

        cities = request_for_cities.split(',')
        zones = [zone for zone in all_zones if zone['city_id'] in cities]
        return mockserver.make_response(json={'zones': zones})

    return _mock_tariff_zones
