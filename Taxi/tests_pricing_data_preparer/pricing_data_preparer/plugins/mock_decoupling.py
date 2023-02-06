# pylint: disable=redefined-outer-name, import-error, E1101
from pricing_extended import mocking_base
import pytest


def decoupling_tariff():
    return {
        'boarding_price': 49,
        'minimum_price': 49,
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 10.8},
        'paid_cancel_options': {
            'add_minimal_to_paid_cancel': True,
            'paid_cancel_fix': 100.0,
        },
        'requirement_prices': {'cargo_loaders': 0, 'waiting_in_transit': 12},
        'requirement_multipliers': {'cargo_loaders': 1.5},
        'requirements_included_one_of': ['some_fake_decoupling_requirement'],
    }


class DecouplingContext(mocking_base.BasicMock):
    def __init__(self, load_json):
        super().__init__()
        self.corp_tariffs_response = load_json('decoupling_tariff_corp.json')
        self.corp_tariffs_error = False
        self.expected_corp_tariff_errors = 0

    def check_client_tariff_request(self, request):
        data = request.args
        assert 'client_id' in data
        assert data['client_id'] == 'decoupling'

    def check_tariff_request(self, request):
        data = request.args
        assert 'id' in data
        assert data['id'] == 'corp_tariff_id'

    def disable_fix_price(self):
        self.corp_tariffs_response['disable_fixed_price'] = True

    def disable_surge(self):
        for category in self.corp_tariffs_response['tariff']['categories']:
            category['disable_surge'] = True

    def disable_paid_supply(self):
        self.corp_tariffs_response['disable_paid_supply_price'] = True

    def tariffs_crack(self, expected_requests=1):
        self.corp_tariffs_error = True
        self.expected_corp_tariff_errors = expected_requests


@pytest.fixture
def decoupling(load_json):
    return DecouplingContext(load_json)


@pytest.fixture
def mock_decoupling_corp_tariffs(mockserver, decoupling):
    class DecouplingMocks:
        @mockserver.json_handler('/corp-tariffs/v1/tariff')
        @staticmethod
        async def handler_tariff(request):
            decoupling.check_tariff_request(request)
            decoupling.response = decoupling.corp_tariffs_response
            if decoupling.corp_tariffs_error:
                decoupling.must_crack()
                decoupling.expected_corp_tariff_errors -= 1
                if decoupling.expected_corp_tariff_errors <= 0:
                    decoupling.corp_tariffs_error = False
            return decoupling.process(mockserver)

        @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
        @staticmethod
        async def handler_client_tariff(request):
            decoupling.check_client_tariff_request(request)
            decoupling.response = dict(
                decoupling.corp_tariffs_response,
                client_tariff_plan={
                    'tariff_plan_series_id': 'decoupling_tariff_plan_id',
                    'date_from': '2019-04-02T00:00:00+00:00',
                    'date_to': '2119-04-02T00:00:00+00:00',
                },
            )
            if decoupling.corp_tariffs_error:
                decoupling.must_crack()
                decoupling.expected_corp_tariff_errors -= 1
                if decoupling.expected_corp_tariff_errors <= 0:
                    decoupling.corp_tariffs_error = False
            return decoupling.process(mockserver)

    return DecouplingMocks()
