import pytest


@pytest.fixture(name='taxi_tariffs', autouse=True)
def _mock_taxi_tariffs(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _mock_tariff_zones(request):
        assert request.query['city_ids'] in ('CITY_ID2', 'CITY_ID1')
        if request.query['city_ids'] == 'CITY_ID2':
            return {
                'zones': [
                    {'name': 'Moscow', 'time_zone': 'UTC', 'country': 'RUS'},
                    {'name': 'Piter', 'time_zone': 'UTC', 'country': 'RUS'},
                ],
            }
        return {'zones': []}
