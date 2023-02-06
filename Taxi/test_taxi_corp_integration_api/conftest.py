# pylint: disable=redefined-outer-name
import pytest

import taxi_corp_integration_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = ['taxi_corp_integration_api.generated.service.pytest_plugins']

EXP3_DECOUPLING_PAYMENT_METHOD_IDS = {
    'corp-client_id_6',
    'corp-client_id_7',
    'corp-client_id_8',
}


@pytest.fixture
def mock_billing(mockserver):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return {'entries': []}


@pytest.fixture
def exp3_decoupling_mock(client_experiments3, request):
    for client_id in EXP3_DECOUPLING_PAYMENT_METHOD_IDS:
        client_experiments3.add_record(
            consumer='corp_integration_api',
            experiment_name='plugin_decoupling',
            args=[
                {
                    'name': 'payment_method_id',
                    'type': 'string',
                    'value': client_id,
                },
                {'name': 'payment_option', 'type': 'string', 'value': 'corp'},
                {'name': 'country', 'type': 'string', 'value': 'rus'},
            ],
            value={},
        )
        client_experiments3.add_record(
            consumer='corp-integration-api/v1/corp_paymentmethods',
            experiment_name='yandex_corp_payment_uber',
            args=[],
            value={},
        )
