# pylint: disable=redefined-outer-name
# pylint: disable=import-only-modules
import pytest

from taxi.clients.billing_v2 import BillingInfoNotFound

import cargo_tasks.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['cargo_tasks.generated.service.pytest_plugins']

DEFAULT_HANDLER_KEY = 'default'
BILLING_GET_ORDERS_INFO = 'get_orders_info'
BILLING_CREATE_PREPAY_INVOICE = 'create_prepay_invoice'


@pytest.fixture(name='mocked_billing')
def _mocked_billing(patch):
    class Context:
        def __init__(self):
            self.response = None
            self.expected_request = None

        def set_response(self, response, handler_key=DEFAULT_HANDLER_KEY):
            assert response is not None
            if self.response is None:
                self.response = {}
            self.response[handler_key] = response

        def get_response(self, handler_key=DEFAULT_HANDLER_KEY):
            if self.response is None:
                return self.response
            return self.response[handler_key]

        def set_expected_request(self, data, handler_key=DEFAULT_HANDLER_KEY):
            assert data is not None
            if self.expected_request is None:
                self.expected_request = {}
            self.expected_request[handler_key] = data

        def get_expected_request(self, handler_key=DEFAULT_HANDLER_KEY):
            if self.expected_request is None:
                return self.expected_request
            return self.expected_request[handler_key]

    context = Context()

    @patch('taxi.clients.billing_v2.BalanceClient.create_client')
    async def _create_client(*args, **kwargs):
        assert args == context.get_expected_request()
        return context.get_response()

    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    async def _create_association(*args, **kwargs):
        assert kwargs == context.get_expected_request()
        return context.get_response()

    @patch('taxi.clients.billing_v2.BalanceClient.create_person')
    async def _create_person(*args, **kwargs):
        assert args == context.get_expected_request()
        return context.get_response()

    @patch('taxi.clients.billing_v2.BalanceClient.create_offer')
    async def _create_offer(*args, **kwargs):
        assert (*args, kwargs) == context.get_expected_request()
        return context.get_response()

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_contracts(*args, **kwargs):
        assert kwargs == context.get_expected_request()
        return context.get_response()

    @patch('taxi.clients.billing_v2.BalanceClient.find_client')
    async def _find_client(*args, **kwargs):
        assert kwargs == context.get_expected_request()
        response = context.get_response()
        if response is None:
            raise BillingInfoNotFound()
        return response

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_persons')
    async def _get_client_persons(*args, **kwargs):
        assert kwargs == context.get_expected_request()
        return context.get_response()

    @patch('taxi.clients.billing_v2.BalanceClient.create_common_contract')
    async def _create_common_contract(*args, **kwargs):
        assert (*args, kwargs) == context.get_expected_request()
        return context.get_response()

    @patch('taxi.clients.billing_v2.BalanceClient.get_orders_info')
    async def _get_orders_info(*args, **kwargs):
        assert kwargs == context.get_expected_request(
            handler_key=BILLING_GET_ORDERS_INFO,
        )
        return context.get_response(handler_key=BILLING_GET_ORDERS_INFO)

    @patch('taxi.clients.billing_v2.BalanceClient.create_prepay_invoice')
    async def _create_prepay_invoice(*args, **kwargs):
        assert kwargs == context.get_expected_request(
            handler_key=BILLING_CREATE_PREPAY_INVOICE,
        )
        return context.get_response(handler_key=BILLING_CREATE_PREPAY_INVOICE)

    return context


@pytest.fixture(name='mocked_corp_tariffs')
def _mocked_corp_tariffs(mockserver, load_json):
    class Context:
        def __init__(self):
            self.response = None
            self.expected_request = None

        def set_response(self, response, handler_key=DEFAULT_HANDLER_KEY):
            assert response is not None
            if self.response is None:
                self.response = {}
            self.response[handler_key] = response

        def get_response(self, handler_key=DEFAULT_HANDLER_KEY):
            if self.response is None:
                return self.response
            return self.response[handler_key]

        def set_expected_request(self, data, handler_key=DEFAULT_HANDLER_KEY):
            assert data is not None
            if self.expected_request is None:
                self.expected_request = {}
            self.expected_request[handler_key] = data

        def get_expected_request(self, handler_key=DEFAULT_HANDLER_KEY):
            if self.expected_request is None:
                return self.expected_request
            return self.expected_request[handler_key]

    context = Context()

    @mockserver.json_handler('/corp-tariffs/v1/tariff/current')
    async def _get_tariff_current(request):
        assert request.query == context.get_expected_request()
        return context.get_response()

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    async def _get_client_tariff_current(request):
        assert request.query == context.get_expected_request()
        return context.get_response()

    return context
