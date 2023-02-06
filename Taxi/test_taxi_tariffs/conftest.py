# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

import copy
import typing

import pytest

from taxi.util import context_timings as ct

import taxi_tariffs.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_tariffs.generated.service.pytest_plugins']


@pytest.fixture
def cache_shield(web_app):
    ctx = web_app['context']

    def get_caches():
        return {
            'tariffs': ctx.tariffs_cache._cache,
            'tariff_settings': ctx.tariff_settings_cache._cache,
        }

    caches = copy.deepcopy(get_caches())
    yield

    assert caches == get_caches()


@pytest.fixture(autouse=True)
def _mock_time_storage():
    timestorage = ct.performance.TimeStorage('testsuite')
    ct.time_storage.set(timestorage)


@pytest.fixture(autouse=True)
def invalidate_memstorage_cache():
    from taxi import memstorage

    manager = memstorage._manager
    for key in list(manager._cache.keys()):
        manager._invalidate(key)


class TariffsContext:
    def __init__(self):
        self.tariffs = []
        self.status = 200
        self.error_response = {}

    def set_error(self, code, error_body):
        self.error_response = error_body
        self.status = code

    def set_tariffs(self, tariffs: typing.List[typing.Any]):
        self.tariffs = copy.deepcopy(tariffs)
        for tariff in self.tariffs:
            if 'categories_names' in tariff:
                tariff['categories'] = tariff['categories_names']
                tariff.pop('categories_names')

    def set_tariffs_list_response(self, expected_response):
        self.tariffs = copy.deepcopy(expected_response)


@pytest.fixture
def tariffs_context():
    return TariffsContext()


@pytest.fixture(autouse=True)
def individual_tariffs_mockserver(mockserver, tariffs_context):
    class IndividualTariffsHandlers:
        @staticmethod
        @mockserver.json_handler(
            '/individual-tariffs/internal/v1/tariff-by-zone',
        )
        @mockserver.json_handler('/individual-tariffs/internal/v1/tariff')
        @mockserver.json_handler('/individual-tariffs/v1/tariff/by_category')
        def tariff_handler(_):
            if tariffs_context.status != 200:
                return mockserver.make_response(
                    status=tariffs_context.status,
                    json=tariffs_context.error_response,
                )
            return tariffs_context.tariffs[0]

        @staticmethod
        @mockserver.json_handler(
            '/individual-tariffs/internal/v1/tariffs/summary',
        )
        def v1_tariffs_summary(_):
            response_list = copy.deepcopy(tariffs_context.tariffs)
            return {'tariffs': response_list}

    return IndividualTariffsHandlers()
