# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import copy
import dataclasses
import typing

import pytest

import corp_tariffs.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_tariffs.generated.service.pytest_plugins']


@pytest.fixture
def cache_shield(web_app):
    ctx = web_app['context']

    def get_caches():
        return {
            'tariffs': ctx.tariffs_cache._cache,
            'corp_tariffs': ctx.corp_tariffs_cache._cache,
            'tariff_plans': ctx.tariff_plans_cache._cache,
            'tariff_zones': ctx.tariff_zones_cache._cache,
        }

    caches = copy.deepcopy(get_caches())
    yield

    assert caches == get_caches()


@pytest.fixture(autouse=True)
def mock_tariff_zones(mockserver):
    class MockTariffZones:
        @dataclasses.dataclass
        class TariffZonesData:
            zones: typing.List[typing.List]

        data = TariffZonesData(zones=[])

        @staticmethod
        @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
        def _mock_tariffs_zones(request, **kwargs):
            return mockserver.make_response(
                json=MockTariffZones.data.zones, status=200,
            )

    return MockTariffZones()


@pytest.fixture(autouse=True)
def individual_tariffs_mockserver(mockserver, load_json):
    class IndividualTariffsHandlers:
        @dataclasses.dataclass
        class TariffsContext:
            def __init__(self):
                file_name = 'individual_tariffs_v1_tariff_list.json'
                self.list_response = load_json(file_name)
                self.tariff_response = {}
                self.status = 200

            def set_list_response(self, response):
                self.list_response = response

            def set_tariff_response(self, response):
                self.tariff_response = copy.deepcopy(response)

        tariffs_context = TariffsContext()

        @staticmethod
        @mockserver.json_handler(
            '/individual-tariffs/internal/v1/tariffs/list',
        )
        def list(_):
            handlers = IndividualTariffsHandlers
            if handlers.tariffs_context.status != 200:
                return mockserver.make_response(
                    status=handlers.tariffs_context.status,
                    json=handlers.tariffs_context.list_response,
                )
            return {'tariffs': (handlers.tariffs_context.list_response)}

        @staticmethod
        @mockserver.json_handler('/individual-tariffs/internal/v1/tariff')
        def tariff(_):
            return IndividualTariffsHandlers.tariffs_context.tariff_response

        @staticmethod
        @mockserver.json_handler(
            '/individual-tariffs/internal/v1/tariff-by-zone',
        )
        def tariff_by_zone(_):
            return IndividualTariffsHandlers.tariffs_context.tariff_response

    return IndividualTariffsHandlers()
