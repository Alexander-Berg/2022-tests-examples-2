# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy

import pytest

from cargo_pricing_plugins import *  # noqa: F403 F401

from tests_cargo_pricing.next_day_delivery import utils


@pytest.fixture(name='mock_ndd_tariff_composer')
def _mock_ndd_tariff_composer(mockserver):
    class Context:
        request = None
        response = utils.get_default_tariff_composition()
        response_status_code = 200

    ctx = Context()

    @mockserver.json_handler(
        '/cargo-tariffs/tariffs/v1/ndd-client/v1/composer',
    )
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        if ctx.response_status_code == 200:
            return ctx.response
        return mockserver.make_response(
            json={}, status=ctx.response_status_code,
        )

    return ctx


@pytest.fixture(name='mock_ndd_tariff_composer_retrieve')
def _mock_ndd_tariff_composer_retrieve(mockserver):
    class Context:
        requested_id = None
        response = utils.get_default_tariff_composition()

    ctx = Context()

    @mockserver.json_handler(
        '/cargo-tariffs/tariffs/v1/ndd-client/v1/composer/retrieve',
    )
    def _mock(request, *args, **kwargs):
        ctx.requested_id = request.query['composition_id']
        return ctx.response

    return ctx


@pytest.fixture(name='v1_ndd_calc_client_creator')
async def _v1_ndd_calc_client_creator(
        taxi_cargo_pricing, mock_ndd_tariff_composer,
):
    class Creator:
        url = '/v1/next-day-delivery/client/calc-price'
        payload = utils.get_default_calc_request()
        composer = mock_ndd_tariff_composer

        async def execute(self, previous_calc_id=None):
            request = copy.deepcopy(self.payload)
            if previous_calc_id is not None:
                request['previous_calculation_id'] = previous_calc_id
                request['idempotency_token'] = previous_calc_id + '_token'
            return await taxi_cargo_pricing.post(self.url, json=request)

    return Creator()


@pytest.fixture(name='v1_ndd_offer_calc_client_creator')
async def _v1_ndd_offer_calc_client_creator(
        taxi_cargo_pricing, mock_ndd_tariff_composer,
):
    class Creator:
        url = '/v1/next-day-delivery/client/calc-offer-price'
        payload = utils.get_default_calc_offer_request()
        composer = mock_ndd_tariff_composer

        async def execute(self):
            return await taxi_cargo_pricing.post(self.url, json=self.payload)

    return Creator()


@pytest.fixture(name='default_calcplan_config')
def _default_calcplan_config(taxi_config):
    taxi_config.set_values(
        {
            'CARGO_PRICING_NDD_CALCULATION_PLAN': (
                utils.get_default_calcplan_config()
            ),
        },
    )


@pytest.fixture(name='reset_calcplan_config')
def _reset_calcplan_config(taxi_config, taxi_cargo_pricing):
    class Reseter:
        async def reset(self, plan):
            taxi_config.set_values(
                {'CARGO_PRICING_NDD_CALCULATION_PLAN': {'plan': plan}},
            )
            await taxi_cargo_pricing.invalidate_caches()

    return Reseter()


@pytest.fixture(name='mock_countries_list')
def _mock_countries_list(mockserver, load_json):
    class MockCountriesListContext:
        mock = None
        response = load_json('countries_list.json')

    ctx = MockCountriesListContext()

    @mockserver.json_handler('/territories/v1/countries/list')
    def _mock(request):
        request.get_data()
        return ctx.response

    ctx.mock = _mock

    return ctx
