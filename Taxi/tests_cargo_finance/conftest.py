import dataclasses
import typing

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from cargo_finance_plugins import *  # noqa: F403 F401
from testsuite.mockserver import classes


@dataclasses.dataclass
class MockserverData:
    request: typing.Optional[classes.MockserverRequest]
    response_data: typing.Any
    response_code: int
    mock: typing.Optional[classes.GenericRequestHandler]


@pytest.fixture(name='procaas_extract_token')
def _procaas_extract_token():
    def wrapper(request):
        return request.headers['X-Idempotency-Token']

    return wrapper


@pytest.fixture(name='mock_with_context')
def _mock_with_context(mockserver):
    def _callable(
            decorator: classes.GenericRequestDecorator,
            response_data,
            response_code=200,
    ) -> MockserverData:
        data = MockserverData(
            request=None,
            response_data=response_data,
            response_code=response_code,
            mock=None,
        )

        @decorator
        def handler(request):
            data.request = request
            return mockserver.make_response(
                json=data.response_data, status=data.response_code,
            )

        data.mock = handler
        return data

    return _callable


@pytest.fixture(name='mock_procaas_create')
def _mock_procaas_create(mockserver, procaas_extract_token):
    url = r'/processing/v1/(?P<scope>\w+)/(?P<queue>\w+)/create-event'

    @mockserver.json_handler(url, regex=True)
    def handler(request, scope, queue):
        return {'event_id': procaas_extract_token(request)}

    return handler


@pytest.fixture(name='procaas_events_response')
def _procaas_events_response():
    class Response:
        def __init__(self):
            self.events = []

        def make(self, request, scope, queue):
            if isinstance(self.events, list):
                return {'events': self.events}
            if isinstance(self.events, dict):
                return {'events': self.events[request.query['item_id']]}
            return {'events': []}

    return Response()


@pytest.fixture(name='mock_procaas_events', autouse=True)
def _mock_procaas_events(mockserver, procaas_events_response):
    url = r'/processing/v1/(?P<scope>\w+)/(?P<queue>\w+)/events'

    @mockserver.json_handler(url, regex=True)
    def handler(request, scope, queue):
        return procaas_events_response.make(request, scope, queue)

    return handler


@pytest.fixture(name='py2_products_response')
def _py2_products_response(static_response_cls, load_json):
    return static_response_cls('py2_billing_products_response.json')


@pytest.fixture(name='mock_py2_products')
def _mock_py2_products(mockserver, py2_products_response):
    url = '/py2-delivery/fetch-product-ids'

    @mockserver.json_handler(url)
    def handler(request):
        return py2_products_response.make(request)

    return handler


@pytest.fixture(name='py2_fiscal_data_response')
def _py2_fiscal_data_response(static_response_cls, load_json):
    return static_response_cls('py2_fiscal_data_response.json')


@pytest.fixture(name='mock_py2_fiscal_data')
def _mock_py2_fiscal_data(mockserver, py2_fiscal_data_response):
    url = '/py2-delivery/fetch-fiscal-data'

    @mockserver.json_handler(url)
    def handler(request):
        return py2_fiscal_data_response.make(request)

    return handler


@pytest.fixture(name='mock_py2_fiscal_data_kz')
def _mock_py2_fiscal_data_kz(mockserver, py2_fiscal_data_response):
    url = '/py2-delivery/fetch-fiscal-data'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            json={
                'inn_for_receipt_id': '2201208428a9412eb6543c5433064ec9',
                'inn_for_receipt': '091240006400',
                'nds_for_receipt': None,
            },
            status=200,
        )

    return handler


@pytest.fixture(name='mock_py2_fiscal_data_null')
def _mock_py2_fiscal_data_null(mockserver):
    url = '/py2-delivery/fetch-fiscal-data'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            json={
                'inn_for_receipt_id': None,
                'inn_for_receipt': None,
                'nds_for_receipt': None,
            },
            status=200,
        )

    return handler


@pytest.fixture(name='mock_py2_fetch_country', autouse=True)
def _mock_py2_fetch_country(mockserver):
    url = '/py2-delivery/fetch-country'

    @mockserver.json_handler(url)
    def handler(request):
        if request.json['nearest_zone'] == 'telaviv':
            return mockserver.make_response(
                json={'country': 'isr'}, status=200,
            )
        return mockserver.make_response(json={'country': 'rus'}, status=200)

    return handler


@pytest.fixture(name='mock_py2_fiscal_data_none')
def _mock_py2_fiscal_data_none(mockserver, py2_fiscal_data_response):
    url = '/py2-delivery/fetch-fiscal-data'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(status=404)

    return handler


@pytest.fixture(name='order_proc')
def _order_proc(load_json, order_archive_mock):
    order_proc = load_json('order_proc.json')
    order_archive_mock.set_order_proc(order_proc)
    return order_proc


@pytest.fixture(name='taxi_order_id')
def _taxi_order_id(order_proc):
    return order_proc['_id']


@pytest.fixture(name='claims_full_response')
def _claims_full_response(static_response_cls):
    return static_response_cls('claims_full_response.json')


@pytest.fixture(name='mock_claims_full')
def _mock_claims_full(mockserver, claims_full_response):
    url = '/cargo-claims/v2/claims/full'

    @mockserver.json_handler(url)
    def handler(request):
        return claims_full_response.make(request)

    return handler


@pytest.fixture(name='mock_transactions_ng_retrieve_admin')
def _mock_transactions_ng_retrieve_admin(mockserver, load_json):
    url = '/transactions-ng/v2/invoice/retrieve'

    @mockserver.json_handler(url)
    def handler(request):
        if (
                request.json['id']
                == 'claims/agent/71478df92af4ca6a9a841a34b46c85b6'
        ):
            return mockserver.make_response(
                status=200,
                json=load_json('response_t-ng_v2_invoice_retrieve.json'),
            )
        return mockserver.make_response(
            status=404,
            json={
                'code': 'invoice_is_not_found',
                'message': 'invoice is not found',
            },
        )

    return handler


@pytest.fixture(name='claims_estimated_payment_methods_response')
def _claims_estimated_payment_methods_response(static_response_cls):
    return static_response_cls(
        'claims_estimated_payment_methods_response.json',
    )


@pytest.fixture(name='mock_claims_estimated_payment_methods')
def _mock_claims_estimated_payment_methods(
        mockserver, claims_estimated_payment_methods_response,
):
    url = '/cargo-claims/v2/claims/finance/estimation-result/payment-methods'

    @mockserver.json_handler(url)
    def handler(request):
        return claims_estimated_payment_methods_response.make(request)

    return handler


@pytest.fixture(name='static_response_cls')
def _static_response_cls(mockserver, load_json):
    class Response:
        def __init__(self, filename):
            self.filename = filename
            self.data = None
            self.status = 200

        def make(self, response):
            if self.status == 200:
                return self.load()
            return mockserver.make_response(status=self.status, json={})

        def load(self):
            if self.data is not None:
                return self.data
            return load_json(self.filename)

    return Response


@pytest.fixture(name='calc_id')
def _calc_id():
    return '123'


@pytest.fixture(name='claim_id')
def _claim_id(claim_doc):
    return claim_doc['id']


@pytest.fixture(name='claim_doc')
def _claim_doc(load_json):
    return load_json('claims_full_response.json')


@pytest.fixture(name='ndd_order_id')
def _ndd_order_id(ndd_order_doc):
    return ndd_order_doc['id']


@pytest.fixture(name='ndd_order_doc')
def _ndd_order_doc(load_json):
    return load_json('ndd_order.json')


@pytest.fixture(name='trucks_order_id')
def _trucks_order_id(trucks_order_doc):
    return trucks_order_doc['id']


@pytest.fixture(name='trucks_order_doc')
def _trucks_order_doc(load_json):
    return load_json('trucks_order.json')


@pytest.fixture(name='mock_transactions_ng_retrieve_ctx')
def _mock_transactions_ng_reponse_ctx(load_json):
    class Context:
        def __init__(self):
            self.response = load_json('response_t-ng_v2_invoice_retrieve.json')
            self.status = 200

    return Context()


@pytest.fixture(name='mock_transactions_ng_retrieve', autouse=True)
def _mock_transactions_ng_reponse(
        mock_transactions_ng_retrieve_ctx, mockserver,
):
    url = '/transactions-ng/v2/invoice/retrieve'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            status=mock_transactions_ng_retrieve_ctx.status,
            json=mock_transactions_ng_retrieve_ctx.response,
        )

    return handler


@pytest.fixture(name='mock_debt_collector_by_id_ctx')
def _mock_debt_collector_by_id_ctx():
    class Context:
        def __init__(self):
            self.response = {}
            self.status = 200

    return Context()


@pytest.fixture(name='mock_debt_collector_by_id')
def _mock_debt_collector_by_id(mock_debt_collector_by_id_ctx, mockserver):
    url = '/debt-collector/v1/debts/by_id'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            status=mock_debt_collector_by_id_ctx.status,
            json=mock_debt_collector_by_id_ctx.response,
        )

    return handler


@pytest.fixture(name='mock_debt_collector_update_ctx')
def _mock_debt_collector_update_ctx():
    class Context:
        def __init__(self):
            self.response = {}
            self.status = 200

    return Context()


@pytest.fixture(name='mock_debt_collector_update')
def _mock_debt_collector_update(mock_debt_collector_update_ctx, mockserver):
    url = '/debt-collector/v1/debt/update'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            status=mock_debt_collector_update_ctx.status,
            json=mock_debt_collector_update_ctx.response,
        )

    return handler


@pytest.fixture(name='mock_debt_collector_create_ctx')
def _mock_debt_collector_create_ctx():
    class Context:
        def __init__(self):
            self.response = {}
            self.status = 200

    return Context()


@pytest.fixture(name='mock_debt_collector_create')
def _mock_debt_collector_create(mock_debt_collector_create_ctx, mockserver):
    url = '/debt-collector/v1/debt/create'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            status=mock_debt_collector_create_ctx.status,
            json=mock_debt_collector_create_ctx.response,
        )

    return handler


@pytest.fixture(name='mock_debt_collector_list_ctx')
def _mock_debt_collector_list_ctx():
    class Context:
        def __init__(self):
            self.response = {}
            self.status = 200

    return Context()


@pytest.fixture(name='mock_debt_collector_list')
def _mock_debt_collector_list(mock_debt_collector_list_ctx, mockserver):
    url = '/debt-collector/v1/debts/list'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            status=mock_debt_collector_list_ctx.status,
            json=mock_debt_collector_list_ctx.response,
        )

    return handler


@pytest.fixture(name='get_events_up_to')
def _get_events_up_to(load_json):
    def wrapper(filename, event_id=None):
        events_up_to = []
        for event in load_json(filename):
            events_up_to.append(event)
            if event['event_id'] == event_id:
                break
        return events_up_to

    return wrapper


@pytest.fixture(name='get_expected_sum2pay')
def _get_expected_sum2pay(load_json):
    def wrapper(filename, event_id=None):
        for item in load_json(filename):
            if item['event_id'] == event_id:
                return item['sum2pay']
        raise RuntimeError('did not meet sum2pay for event_id=' + event_id)

    return wrapper


@pytest.fixture(name='mock_v2_process_async')
def _mock_v2_process_async(mockserver):
    url = '/billing-orders/v2/process/async'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {'topic': 'foo', 'external_ref': '1', 'doc_id': 123},
                ],
            },
        )

    return handler
