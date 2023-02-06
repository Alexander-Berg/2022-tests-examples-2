# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import cashback.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from cashback.utils import postgres
from cashback.utils import time_storage
from .utils import requests
from .utils import responses

pytest_plugins = ['cashback.generated.service.pytest_plugins']


class BaseFacade:
    p_key = 'id'
    table_name: str

    def __init__(self, web_context):
        self.pgaas = web_context.pg

    async def by_query(self, query, *query_args):
        return await postgres.fetch(self.pgaas, query, *query_args)

    async def all(self):
        query = 'SELECT * FROM cashback.{}'.format(self.table_name)
        return await self.by_query(query)

    async def by_ids(self, ids):
        query = (
            """
        SELECT * FROM cashback.{}
        WHERE {} = ANY($1)
        """.format(
                self.table_name, self.p_key,
            )
        )
        return await self.by_query(query, ids)


class OrderRatesFacade(BaseFacade):
    table_name = 'order_rates'
    p_key = 'order_id'


class EventsFacade(BaseFacade):
    table_name = 'events'

    async def by_external_ref(self, external_ref):
        query = 'select * from cashback.{} where external_ref = $1'.format(
            self.table_name,
        )
        return await self.by_query(query, external_ref)


class OrderClearFacade(BaseFacade):
    table_name = 'order_clears'
    p_key = 'order_id'


class BalancesContext:
    expected_currencies = ['RUB']
    expected_uid = 'yandex_uid_1'
    wallets = [{'wallet_id': 'wallet_1', 'currency': 'RUB'}]


@pytest.fixture
def pg_cashback(web_context):
    class Ctx:
        def __init__(self, web_context):
            self.order_rates = OrderRatesFacade(web_context)
            self.events = EventsFacade(web_context)
            self.order_clears = OrderClearFacade(web_context)

    return Ctx(web_context)


@pytest.fixture
def web_cashback(taxi_cashback_web):
    class Ctx:
        def __init__(self, taxi_cashback_web):
            self.register_cashback = requests.RegisterCashbackRequest(
                taxi_cashback_web,
            )
            self.calc_cashback = requests.CalcCashbackRequest(
                taxi_cashback_web,
            )
            self.v2_calc_cashback = requests.V2CalcCashbackRequest(
                taxi_cashback_web,
            )
            self.restore_cashback = requests.RestoreCashbackRequest(
                taxi_cashback_web,
            )
            self.payment_split = requests.PaymentSplitRequest(
                taxi_cashback_web,
            )

    return Ctx(taxi_cashback_web)


@pytest.fixture(name='transactions_mock')
def _transactions_mock(
        mock_transactions,
        mock_transactions_eda,
        mock_transactions_lavka_isr,
        mockserver,
):
    class Context:
        invoice_retrieve = responses.RetrieveInvoice()
        invoice_retrieve_v2 = responses.RetrieveInvoiceV2()

    context = Context()

    @mock_transactions('/invoice/retrieve')
    @mock_transactions_eda('/invoice/retrieve')
    @mock_transactions_lavka_isr('/invoice/retrieve')
    def _mock_retrieve_invoice(request):
        return context.invoice_retrieve.make_response()

    @mock_transactions('/v2/invoice/retrieve')
    @mock_transactions_eda('/v2/invoice/retrieve')
    @mock_transactions_lavka_isr('/v2/invoice/retrieve')
    def _mock_retrieve_invoice_v2(request):
        return context.invoice_retrieve_v2.make_response()

    return context


@pytest.fixture(autouse=True)
def mock_time_storage():
    time_storage.init_time_storage('test_mock')


@pytest.fixture(name='balances_context')
def _balances_context():
    return BalancesContext()


@pytest.fixture(name='mock_plus_balances')
def _mock_plus_balances(mock_plus_wallet, balances_context):
    @mock_plus_wallet('/v1/balances')
    def _handler(request):
        context = balances_context
        assert request.query['currencies'] == context.expected_currencies[0]
        assert request.query['yandex_uid'] == context.expected_uid

        return {
            'balances': [
                {'balance': '0', **wallet} for wallet in context.wallets
            ],
        }

    return _handler


@pytest.fixture(name='mock_reschedule')
def _mock_reschedule(mockserver):
    def _make_mock(queue, task_id='order_id', expected_eta=None):
        @mockserver.json_handler('/stq-agent/queues/api/reschedule')
        def _handler(request):
            assert request.json['queue_name'] == queue
            assert request.json['task_id'] == task_id
            if expected_eta is not None:
                assert request.json['eta'] == expected_eta

            return {}

        return _handler

    return _make_mock


@pytest.fixture(name='mock_cashback_events')
def _mock_cashback_events(mock_cashback):
    def _make_mock(service='yataxi'):
        @mock_cashback('/internal/events')
        async def _mock_events(request, **kwargs):
            assert request.query['service'] == service
            return {
                'events': [
                    {
                        'event_id': 'event3',
                        'external_ref': 'order_id',
                        'currency': 'RUB',
                        'value': '100',
                        'source': 'user',
                        'type': 'invoice',
                        'yandex_uid': 'yandex_uid_1',
                        'service': 'yataxi',
                        'payload': {},
                    },
                ],
            }

        return _mock_events

    return _make_mock
