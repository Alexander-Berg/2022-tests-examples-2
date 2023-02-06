import pytest


@pytest.fixture(name='tariffs')
def _mock_tariffs(mockserver, load_json):
    all_zones = load_json('tariff_zones.json')

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _mock_tariff_zones(request, *args, **kwargs):
        request_for_cities = request.query['city_ids']
        assert request_for_cities

        cities = request_for_cities.split(',')
        zones = [zone for zone in all_zones if zone['city_id'] in cities]
        return mockserver.make_response(json={'zones': zones})

    return _mock_tariff_zones


@pytest.fixture(name='make_admin_request')
def _make_admin_request(taxi_coupons):
    async def _request_maker(data, mode, url, headers):
        return await taxi_coupons.post(
            path=f'/admin/promocodes/{url}/{mode}/',
            json=data,
            headers=headers,
        )

    return _request_maker
