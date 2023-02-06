import dataclasses
import typing

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pytest  # pylint: disable=wrong-import-order

# pylint: disable=wrong-import-order
from corp_billing_orders_plugins import *  # noqa: F403 F401 I100 I202

from tests_corp_billing_orders import accounts_service
from tests_corp_billing_orders import docs_service


@pytest.fixture(autouse=True, name='tvm_config')
def tvm_config_fixture(taxi_config):
    taxi_config.set(
        TVM_SERVICES={
            'corp-billing-orders': 2345,
            'billing_accounts': 123,
            'billing-docs': 456,
            'statistics': 777,
        },
    )


@pytest.fixture
def call_process_order(taxi_corp_billing_orders):
    async def _wrapper(order):
        response = await taxi_corp_billing_orders.post(
            '/internal/order/process', json=order,
        )
        return response

    return _wrapper


@pytest.fixture
def put_order_in_queue(taxi_corp_billing_orders):
    async def _wrapper(order):
        response = await taxi_corp_billing_orders.post(
            '/v1/order/process', json=order,
        )
        return response

    return _wrapper


@pytest.fixture
def get_order_status(taxi_corp_billing_orders):
    async def _wrapper(order):
        response = await taxi_corp_billing_orders.post(
            '/v1/order/status', json=order,
        )
        return response

    return _wrapper


@pytest.fixture
def billing_docs_service(mockserver, load_json):
    def _wrapper(keep_history=True):
        doc_example = load_json('billing_doc_example.json')
        journal_entry_example = load_json('billing_journal_entry_example.json')

        service = docs_service.Service(
            keep_history, doc_example, journal_entry_example,
        )

        @mockserver.json_handler('/billing-docs/v1/docs/create')
        def docs_create_handler(request):
            return service.docs_create_handler(request)

        @mockserver.json_handler('/billing-docs/v1/docs/search')
        def docs_search_handler(request):
            return service.docs_search_handler(request)

        @mockserver.json_handler(
            '/billing-docs/v1/docs/is_ready_for_processing',
        )
        def ready_for_processing_handler(request):
            return service.ready_for_processing_handler(request)

        @mockserver.json_handler('/billing-docs/v1/docs/finish_processing')
        def doc_finish_processing_handler(request):
            return service.doc_finish_processing_handler(request)

        @mockserver.json_handler('/billing-docs/v2/journal/search')
        def doc_journal_search_handler(request):
            return service.doc_journal_search_handler(request)

        class State:
            service = None
            docs_create_handler = None
            docs_search_handler = None
            ready_for_processing_handler = None
            doc_finish_processing_handler = None
            doc_journal_search_handler = None

        state = State()
        state.service = service
        state.docs_create_handler = docs_create_handler
        state.docs_search_handler = docs_search_handler
        state.ready_for_processing_handler = ready_for_processing_handler
        state.doc_finish_processing_handler = doc_finish_processing_handler
        state.doc_journal_search_handler = doc_journal_search_handler

        return state

    return _wrapper


@pytest.fixture
def billing_accounts_service(mockserver):
    def _wrapper(keep_history=True):
        service = accounts_service.Service(keep_history)

        @mockserver.json_handler('/billing-accounts/v1/entities/create')
        def create_entity_handler(request):
            return service.create_entity_handler(request)

        @mockserver.json_handler('/billing-accounts/v1/accounts/create')
        def create_account_handler(request):
            return service.create_account_handler(request)

        @mockserver.json_handler('/billing-accounts/v1/accounts/search')
        def search_accounts_handler(request):
            return service.search_accounts_handler(request)

        class State:
            service = None
            create_entity_handler = None
            create_account_handler = None
            search_accounts_handler = None

        state = State()
        state.service = service
        state.create_entity_handler = create_entity_handler
        state.create_account_handler = create_account_handler
        state.search_accounts_handler = search_accounts_handler

        return state

    return _wrapper


class _Service:
    def __init__(self, order_statuses):
        self.requests = []
        self.responses = self._build_responses(order_statuses)

    def process_order(self, request):
        self.requests.append(request.json)
        data = request.json
        key = self._build_key(data)
        return self.responses[key]

    def _build_responses(self, order_statuses):
        responses = {}
        for order_status in order_statuses:
            key = self._build_key(order_status)
            responses[key] = order_status
        return responses

    @staticmethod
    def _build_key(data):
        return (
            data['kind'],
            data['topic']['external_ref'],
            data['topic']['revision'],
        )


@pytest.fixture
def _self_service(mockserver):
    def _wrapper(order_statuses):
        service = _Service(order_statuses)

        @mockserver.json_handler('/corp-billing-orders/internal/order/process')
        def handler(request):
            return service.process_order(request)

        @dataclasses.dataclass
        class State:
            service: _Service
            handler: typing.Any

        return State(service, handler)

    return _wrapper


@pytest.fixture
def _build_orders_with_statuses(load_json):
    def _wrapper(refs_revs_finished_status=None):
        order_example = load_json('order_eats_1_v1_order.json')

        if refs_revs_finished_status is None:
            refs_revs_finished_status = [('d1', 1, True, 'complete')]

        orders = []
        statuses = []
        for ref, rev, processed, status in refs_revs_finished_status:
            order = order_example.copy()
            order['topic'] = order_example['topic'].copy()
            order['topic']['external_ref'] = ref
            order['topic']['revision'] = rev
            orders.append(order)
            statuses.append(
                {
                    'kind': order['kind'],
                    'topic': order['topic'],
                    'processed': processed,
                    'status': status,
                },
            )

        return orders, statuses

    return _wrapper


@pytest.fixture
def call_sync(taxi_corp_billing_orders):
    async def _wrapper():
        response = await taxi_corp_billing_orders.post(
            '/testonly/callsyncprocedure',
        )
        assert response.status_code == 200
        return response.json()['pending_count']

    return _wrapper


@pytest.fixture
def _push_orders(put_order_in_queue):
    async def _wrapper(orders):
        responses = []
        for order in orders:
            response = await put_order_in_queue(order)
            assert response.status_code == 200
            responses.append(response.json())
        return responses

    return _wrapper


@pytest.fixture
def _do_sync_until_finish(call_sync):
    async def _wrapper():
        num_calls = 0
        for dummy_i in range(10):
            num_calls += 1
            pending_count = await call_sync()
            if not pending_count:
                break
        return num_calls

    return _wrapper


@pytest.fixture
def call_delete_orders(taxi_corp_billing_orders):
    async def _wrapper():
        response = await taxi_corp_billing_orders.post(
            '/testonly/calldeleteprocedure',
        )
        assert response.status_code == 200
        return response.json()['deleted_count']

    return _wrapper
