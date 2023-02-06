# noqa: E501 pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name, function-redefined
import pytest

import taxi_agglomerations.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_agglomerations.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def mock_geoareas_handler(mockserver, load_json):
    urls = [
        '/geoareas/geoareas/v1/tariff-areas',
        '/geoareas/geoareas/admin/v1/tariff-areas/',
    ]

    async def _mock(request):
        geoareas = load_json('db_geoareas.json')
        name = request.query.get('name')
        if name:
            geoareas = [
                geoarea for geoarea in geoareas if geoarea['name'] == name
            ]
        return {'geoareas': geoareas}

    for url in urls:
        mockserver.json_handler(url)(_mock)


@pytest.fixture(autouse=True)
def mock_tariffs_handler(mockserver, load_json):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones/archive')
    async def _mock(request):
        tariffs = load_json('db_tariffs.json')
        zones = [
            {
                'name': tariff['home_zone'],
                'time_zone': 'Europe/Moscow',
                'country': 'russia',
                'currency': 'RUB',
            }
            for tariff in tariffs
        ]
        return {'zones': zones}


@pytest.fixture
def client(taxi_agglomerations_web):
    return taxi_agglomerations_web
