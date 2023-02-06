import pytest


@pytest.fixture(autouse=True)
def taxi_territories(mockserver, db):
    @mockserver.json_handler('/territories/v1/countries/list')
    def mock_countries_taxi(request):
        countries_cursor = db.countries.find()
        countries = []
        for country in countries_cursor:
            countries.append(country)
        return {'countries': countries}
